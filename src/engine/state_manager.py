import pygame
import config
import socket
import pickle
import threading
from src.config.server_config import SERVER_IP, SERVER_PORT
from src.engine.client_media import (
    draw_game_state, draw_game_over, draw_lobby_screen, 
    draw_menu_screen, draw_waiting_screen, draw_enter_lobby_screen, 
    draw_game_mode_screen, draw_countdown_screen, draw_enter_username_screen
)
from src.engine.dynamic_objects import *
from src.engine.animation_loader import load_animations_Arcane_Archer
from src.engine.states.loading import LoadingState
from src.engine.states.mode_select import ModeSelectState
from src.engine.states.map_select import MapSelectState
from src.engine.states.fighter_select import FighterSelectState
from src.engine.states.playing import PlayingState

class StateManager:
    def __init__(self, scene):
        self.scene = scene
        self.game_state = config.GAME_STATE_LOADING
        self.game_mode = None
        self.current_map = None
        self.fighter1_id = None
        self.fighter2_id = None
        self.animation = None
        self.fighter_select_phase = 1
        self.last_click_time = 0
        self.win_boss = False
        self.win_fighter = False
        self.multi_mode = None
        self.is_initialized = False
        self.win_sound = pygame.mixer.Sound("src/assets/sounds/win.mp3")



        self.fighter_type = None
        self.run_client = False
        self.fighter_type_send = False
        self.username = ""
        self.client_socket = None
        self.client_id = None
        self.option_rects = []
        self.game_id = None
        self.opponents = []
        self.error_message = ""
        self.error_message_time = None
        self.countdown_value = None
        self.client_state = "enter_username"  
        self.game_over = False
        self.winning_team = None
        self.losing_team = None
        self.entered_lobby_id = ""
        self.key_pressed = {
            pygame.K_a: False, pygame.K_d: False, pygame.K_w: False, pygame.K_SPACE: False
        }
        self.client_anim_states = {}
        self.game_world = None
        self.previous_game_world = None
        self.last_update_time = 0
        self.network_interval = 0.1
        self.shared_lock = threading.Lock()
        transparent_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        transparent_surface.fill((0, 0, 0, 0))
        self.images = {
            "fighter": transparent_surface,
            "projectiles": pygame.image.load("src/assets/images/inused_single_images/projectile_Arcane.png"),
            # power up images
            "double_jump": "src/assets/images/inused_single_images/double_jump.png",
            "damage":"src/assets/images/inused_single_images/damage.png",
            "shield":"src/assets/images/inused_single_images/shield.png",
            "supershot":"src/assets/images/inused_single_images/supershot.png",

        }
        self.fighter_animations = {} 
        self.fighter_types = {} 
        try:
            self.fighter_animations["arcane"] = load_animations_Arcane_Archer()
            self.fighter_animations["samurai"] = load_animations_Samurai(scale=1)
            self.fighter_animations["knight"] = load_animations_Knight(scale=1)
            self.fighter_animations["elf"] = load_animations_Elf_Archer()
        except Exception as e:
            print(f"Error loading animations: {e}")
            self.fighter_animations["arcane"] = {}
            self.fighter_animations["samurai"] = {}
            self.fighter_animations["knight"] = {}
            self.fighter_animations["elf"] = {}
        self.states = {
            config.GAME_STATE_LOADING: LoadingState(scene),
            config.GAME_STATE_MODE_SELECT: ModeSelectState(scene),
            config.GAME_STATE_MAP_SELECT: MapSelectState(scene),
            config.GAME_STATE_FIGHTER_SELECT: FighterSelectState(scene),
            config.GAME_STATE_PLAYING: PlayingState(scene),
            "enter_username": None,  
            "select_game_mode": None,
            "menu": None,
            "lobby": None,
            "countdown": None,
            "in_game": None,
            "searching": None
        }

        self.click_sound = pygame.mixer.Sound("src/assets/sounds/mixkit-stapling-paper-2995.wav")
        self.blood_sound = pygame.mixer.Sound("src/assets/sounds/blood2.wav")
        try:
            pygame.mixer.music.load("src/assets/sounds/LevelHellboy.mp3.mpeg")
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"Error loading menu music: {e}")
            self.error_message = "Failed to load menu music"

        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
            self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
            self.client_socket.connect((SERVER_IP, SERVER_PORT))
            client_id_data = self.client_socket.recv(4096)
            self.client_id = pickle.loads(client_id_data)
            print(f"Connected to server. Your client ID is: {self.client_id}")
            self.recv_thread = threading.Thread(target=self.threaded_receive_update, args=(), daemon=True)
            self.recv_thread.start()
        except Exception as e:
            print(f"Could not connect to server: {e}")
            self.error_message = "Could not connect to server"
            self.error_message_time = pygame.time.get_ticks()

    def threaded_receive_update(self):
        while self.client_socket:
            try:
                data = self.client_socket.recv(16384)
                if not data:
                    print("Disconnected from server.")
                    break
                client_package = pickle.loads(data)
                request_type = client_package.get("request_type")
                if request_type == "game_update":
                    self.previous_game_world = self.game_world
                    self.game_world = client_package.get("game_world")
                    self.last_update_time = pygame.time.get_ticks() / 1000.0
                    self.client_state = "in_game"
                    if self.game_world and "fighters" in self.game_world:
                        for fighter_data in self.game_world["fighters"]:
                            self.fighter_types[fighter_data["id"]] = fighter_data["fighter_type"]
                elif request_type == "game_started":
                    self.client_state = "in_game"
                    self.countdown_value = None
                    print("Game started!")
                elif request_type == "game_finished":
                    self.winning_team = client_package.get("winning_team")
                    self.losing_team = client_package.get("losing_team")
                    self.game_over = True
                    self.client_state = "lobby"
                    print(f"Game finished: winning_team={self.winning_team}, losing_team={self.losing_team}")
                elif request_type == "lobby_destroyed":
                    print("Lobby has been destroyed by the host.")
                    self.client_state = "menu"
                elif request_type == "lobby_created":
                    self.game_id = client_package.get("lobby_id")
                    self.client_state = "lobby"
                    print(f"Lobby created with ID: {self.game_id}")
                elif request_type == "lobby_joined":
                    self.game_id = client_package.get("lobby_id")
                    self.client_state = "lobby"
                    self.entered_lobby_id = ""
                    print(f"Joined lobby with ID: {self.game_id}")
                elif request_type == "lobby_join_failed":
                    self.error_message = client_package.get("message", "Lobby not found")
                    self.error_message_time = pygame.time.get_ticks()
                    print(f"Lobby join failed: {self.error_message}")
                elif request_type == "client_disconnected":
                    print(f"Client {client_package.get('client_id')} disconnected from the game or lobby")
                elif request_type == "countdown":
                    self.countdown_value = client_package.get("count")
                    self.client_state = "countdown"
                    print(f"Countdown: {self.countdown_value}")
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def send_request_to_server(self, client_package):
        try:
            self.client_socket.sendall(pickle.dumps(client_package))
            return True
        except Exception as e:
            print(f"Error sending data: {e}")
            return False

    def handle_event(self, event, current_time, scale):
        if self.game_state in self.states and self.states[self.game_state] and self.run_client == False:
            self.states[self.game_state].handle_event(event, current_time, scale, self.current_map, self)
        elif self.run_client == True:
            if self.fighter_type_send == False:
                pkg = {
                "client_id": self.client_id,
                "request_type": "set_fighter_type",
                "fighter_type": self.fighter_type 
                }
                self.send_request_to_server(pkg)
                self.fighter_type_send = True
                print(f"Sent fighter_type {self.fighter_type} to server for client {self.client_id}")
            inputs, shoots = self.handle_multiplayer_input(event)
            if inputs or shoots:
                client_package = {
                    "client_id": self.client_id,
                    "request_type": "input",
                    "game_mode": self.game_mode,
                    "inputs": inputs,
                    "shoots": shoots
                }
                self.send_request_to_server(client_package)

    def handle_multiplayer_input(self, event):
        inputs = []
        shoots = []
        if event.type == pygame.QUIT:
            return [], []
        elif event.type == pygame.KEYDOWN:
            if self.client_state == "enter_username":
                if event.key == pygame.K_RETURN:
                    if self.username:
                        self.client_state = "select_game_mode"
                        pkg = {"client_id": self.client_id, "request_type": "set_username", "username": self.username}
                        self.send_request_to_server(pkg)
                elif event.key == pygame.K_BACKSPACE:
                    self.username = self.username[:-1]
                elif event.unicode.isalnum() or event.unicode in ['_']:
                    if len(self.username) < 15:
                        self.username += event.unicode
            elif self.client_state == "select_game_mode":
                if event.key == pygame.K_1:
                    self.game_mode = "1vs1"
                    self.client_state = "menu"
                    self.click_sound.play()
                elif event.key == pygame.K_2:
                    self.game_mode = "2vs2"
                    self.client_state = "menu"
                    self.click_sound.play()
            elif self.client_state == "enter_lobby_id":
                if event.key == pygame.K_RETURN:
                    if self.entered_lobby_id and not self.error_message:
                        pkg = {"client_id": self.client_id, "request_type": "join_lobby", "room_id": self.entered_lobby_id, "game_mode": self.game_mode}
                        self.send_request_to_server(pkg)
                    elif self.error_message:
                        self.error_message = None
                        self.error_message_time = None
                        self.client_state = "menu"
                elif event.key == pygame.K_BACKSPACE:
                    self.entered_lobby_id = self.entered_lobby_id[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.error_message = None
                    self.error_message_time = None
                    self.entered_lobby_id = ""
                    self.client_state = "menu"
                elif event.unicode.isalnum():
                    self.entered_lobby_id += event.unicode
            elif self.client_state == "menu":
                if event.key == pygame.K_1:
                    pkg = {"client_id": self.client_id, "request_type": "find_random_game", "game_mode": self.game_mode}
                    if self.send_request_to_server(pkg):
                        self.client_state = "searching"
                        self.click_sound.play()
                elif event.key == pygame.K_2:
                    pkg = {"client_id": self.client_id, "request_type": "make_lobby", "game_mode": self.game_mode}
                    if self.send_request_to_server(pkg):
                        self.client_state = "lobby"
                        self.click_sound.play()
                elif event.key == pygame.K_3:
                    self.client_state = "enter_lobby_id"
                    self.click_sound.play()
            elif self.client_state == "lobby":
                if event.key == pygame.K_4:
                    pkg = {"client_id": self.client_id, "request_type": "start_the_game_as_host"}
                    self.send_request_to_server(pkg)
                    self.click_sound.play()
                elif event.key == pygame.K_5:
                    pkg = {"client_id": self.client_id, "request_type": "destroy_lobby"}
                    self.send_request_to_server(pkg)
                    self.click_sound.play()
            if event.key in self.key_pressed and not self.key_pressed[event.key]:
                if event.key == pygame.K_SPACE:
                    shoots.append("arcane")
                self.key_pressed[event.key] = True
                inputs.append(("down", event.key))
        elif event.type == pygame.KEYUP:
            if event.key in self.key_pressed:
                self.key_pressed[event.key] = False
                inputs.append(("up", event.key))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            print(f"Mouse clicked at: {mouse_pos}, option_rects: {self.option_rects}") 
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mouse_pos):
                    print(f"Option {i} clicked") 
                    self.click_sound.play()
                    if self.client_state == "select_game_mode":
                        if i == 0:
                            self.game_mode = "1vs1"
                            self.client_state = "menu"
                        elif i == 1:
                            self.game_mode = "2vs2"
                            self.client_state = "menu"
                    elif self.client_state == "menu":
                        if i == 0:
                            pkg = {"client_id": self.client_id, "request_type": "find_random_game", "game_mode": self.game_mode}
                            if self.send_request_to_server(pkg):
                                self.client_state = "searching"
                        elif i == 1:
                            pkg = {"client_id": self.client_id, "request_type": "make_lobby", "game_mode": self.game_mode}
                            if self.send_request_to_server(pkg):
                                self.client_state = "lobby"
                        elif i == 2:
                            self.client_state = "enter_lobby_id"
                    elif self.client_state == "lobby":
                        if i == 1:  
                            pkg = {"client_id": self.client_id, "request_type": "start_the_game_as_host"}
                            self.send_request_to_server(pkg)
                        elif i == 2:  
                            pkg = {"client_id": self.client_id, "request_type": "destroy_lobby"}
                            self.send_request_to_server(pkg)
        return inputs, shoots

    def update(self, current_time, scale):
        if self.game_state in self.states and self.states[self.game_state] and self.run_client == False:
            self.states[self.game_state].update(current_time, scale, self)
        if self.run_client == True:
            if self.error_message and self.error_message_time and (current_time - self.error_message_time > 3000):
                self.error_message = None
                self.error_message_time = None

    def draw(self, scale):
        if self.game_state in self.states and self.states[self.game_state] and self.run_client == False:
            self.states[self.game_state].draw(self.scene, scale, self)
        elif self.run_client == True:
            mouse_pos = pygame.mouse.get_pos()
            self.option_rects = []
            if self.game_over:
                draw_game_over(self.scene, self.winning_team, self.losing_team)
                pygame.time.delay(3000)
                self.game_over = False
                self.winning_team = None
                self.losing_team = None
                self.client_state = "menu"
            elif self.client_state == "in_game":
                draw_game_state(self.scene, self.shared_lock, self.game_world, self.previous_game_world, 
                               self.last_update_time, self.network_interval, self.fighter_animations, self.client_anim_states, self.images)
            elif self.client_state in ["searching", "waiting"]:
                draw_waiting_screen(self.scene)
            elif self.client_state == "lobby":
                draw_lobby_screen(self.scene, self.game_id)
            elif self.client_state == "menu":
                self.option_rects = draw_menu_screen(self.scene, mouse_pos)
            elif self.client_state == "enter_lobby_id":
                draw_enter_lobby_screen(self.scene, self.entered_lobby_id, self.error_message)
            elif self.client_state == "select_game_mode":
                self.option_rects = draw_game_mode_screen(self.scene, mouse_pos)
            elif self.client_state == "countdown":
                draw_countdown_screen(self.scene, self.countdown_value)
            elif self.client_state == "enter_username":
                draw_enter_username_screen(self.scene, self.username)
            else:
                draw_waiting_screen(self.scene)
            if self.error_message:
                font = pygame.font.Font(None, 60)
                error_text = font.render(self.error_message, True, (255, 0, 0))
                error_rect = error_text.get_rect(center=(config.SCENE_WIDTH // 2, config.SCENE_HEIGHT // 2 - 150))
                self.scene.blit(error_text, error_rect)

    def change_state(self, new_state, state_instance=None):
        """Change the current game state."""
        previous_state = self.game_state
        self.game_state = new_state
        if state_instance:
            self.states[new_state] = state_instance
        if new_state not in [config.GAME_STATE_PLAYING, config.GAME_STATE_MULTIPLATER]:
            try:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load("src/assets/sounds/LevelHellboy.mp3.mpeg")
                    pygame.mixer.music.play(-1)
            except pygame.error as e:
                print(f"Error loading menu music: {e}")
                self.error_message = "Failed to load menu music"
        elif new_state in [config.GAME_STATE_PLAYING, config.GAME_STATE_MULTIPLATER] and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()