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


        # info_lock candidates:
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
        self.game_world = None # game_lock
        self.previous_game_world = None # game_lock
        self.last_update_time = 0 # game_lock
        self.network_interval = 0.1
        self.run_client = False

        
        self.shared_lock = threading.Lock() # going to split into info_lock and game_lock
        self.info_lock = threading.Lock()
        self.game_lock = threading.Lock()

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
            with self.info_lock:
                self.client_id = pickle.loads(client_id_data)
            print(f"Connected to server. Your client ID is: {self.client_id}")
            self.recv_thread = threading.Thread(target=self.threaded_receive_update, args=(), daemon=True)
            self.recv_thread.start()
        except Exception as e:
            print(f"Could not connect to server: {e}")
            with self.info_lock:
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
                    # Protect mutation of game state
                    with self.game_lock:
                        self.previous_game_world = self.game_world
                        self.game_world = client_package.get("game_world")
                        self.last_update_time = pygame.time.get_ticks() / 1000.0
                        if self.game_world and "fighters" in self.game_world:
                            for fighter_data in self.game_world["fighters"]:
                                self.fighter_types[fighter_data["id"]] = fighter_data["fighter_type"]
                    # update client_state in one grouped info_lock
                    with self.info_lock:
                        self.client_state = "in_game"
                elif request_type == "game_started":
                    # countdown_value is game-level, client_state is info-level
                    with self.game_lock:
                        self.countdown_value = None
                    with self.info_lock:
                        self.client_state = "in_game"
                    print("Game started!")
                elif request_type == "game_finished":
                    # Protect setting of end-of-game fields (game-level) and info fields grouped
                    with self.game_lock:
                        self.winning_team = client_package.get("winning_team")
                        self.losing_team = client_package.get("losing_team")
                        self.game_over = True
                    with self.info_lock:
                        self.client_state = "lobby"
                    print(f"Game finished: winning_team={self.winning_team}, losing_team={self.losing_team}")
                elif request_type == "lobby_destroyed":
                    with self.info_lock:
                        self.client_state = "menu"
                    print("Lobby has been destroyed by the host.")
                elif request_type == "lobby_created":
                    with self.info_lock:
                        self.game_id = client_package.get("lobby_id")
                        self.client_state = "lobby"
                    print(f"Lobby created with ID: {self.game_id}")
                elif request_type == "lobby_joined":
                    with self.info_lock:
                        self.game_id = client_package.get("lobby_id")
                        self.client_state = "lobby"
                        self.entered_lobby_id = ""
                    print(f"Joined lobby with ID: {self.game_id}")
                elif request_type == "lobby_join_failed":
                    with self.info_lock:
                        self.error_message = client_package.get("message", "Lobby not found")
                        self.error_message_time = pygame.time.get_ticks()
                    print(f"Lobby join failed: {self.error_message}")
                elif request_type == "client_disconnected":
                    print(f"Client {client_package.get('client_id')} disconnected from the game or lobby")
                elif request_type == "countdown":
                    # Protect countdown value update (game-level) and client_state (info-level)
                    with self.game_lock:
                        self.countdown_value = client_package.get("count")
                    with self.info_lock:
                        self.client_state = "countdown"
                    print(f"Countdown: {self.countdown_value}")
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def send_request_to_server(self, client_package):
        try:
            # snapshot socket under info_lock to avoid race and to avoid holding lock during network I/O
            with self.info_lock:
                sock = self.client_socket
            if not sock:
                return False
            sock.sendall(pickle.dumps(client_package))
            return True
        except Exception as e:
            print(f"Error sending data: {e}")
            return False

    def handle_event(self, event, current_time, scale):
        if self.game_state in self.states and self.states[self.game_state] and self.run_client == False:
            self.states[self.game_state].handle_event(event, current_time, scale, self.current_map, self)
        else:
            # Check run_client and prepare fighter-type send in a single info_lock
            with self.info_lock:
                run_client_local = self.run_client
                need_send_fighter = (not self.fighter_type_send)
                client_id_local = self.client_id
                fighter_type_local = self.fighter_type
            if run_client_local:
                if need_send_fighter:
                    # mark sent under lock, but perform network send after releasing lock
                    with self.info_lock:
                        self.fighter_type_send = True
                    pkg = {
                        "client_id": client_id_local,
                        "request_type": "set_fighter_type",
                        "fighter_type": fighter_type_local
                    }
                    self.send_request_to_server(pkg)
                    print(f"Sent fighter_type {fighter_type_local} to server for client {client_id_local}")
                inputs, shoots = self.handle_multiplayer_input(event)
                if inputs or shoots:
                    # snapshot needed info once
                    with self.info_lock:
                        client_id_local = self.client_id
                        game_mode_local = self.game_mode
                    client_package = {
                        "client_id": client_id_local,
                        "request_type": "input",
                        "game_mode": game_mode_local,
                        "inputs": inputs,
                        "shoots": shoots
                    }
                    self.send_request_to_server(client_package)

    def handle_multiplayer_input(self, event):
        inputs = []
        shoots = []
        outbound_pkg = None

        if event.type == pygame.QUIT:
            return [], []
        # Snapshot a set of info fields once to decide behavior; modify state and prepare packages inside the same lock
        with self.info_lock:
            client_state_local = self.client_state
            username_local = self.username
            entered_local = self.entered_lobby_id
            error_local = self.error_message
            game_mode_local = self.game_mode
            option_rects_local = list(self.option_rects)
        # Handle keyboard events
        if event.type == pygame.KEYDOWN:
            if client_state_local == "enter_username":
                if event.key == pygame.K_RETURN:
                    # set new state and prepare pkg under lock
                    with self.info_lock:
                        if self.username:
                            self.client_state = "select_game_mode"
                            outbound_pkg = {"client_id": self.client_id, "request_type": "set_username", "username": self.username}
                elif event.key == pygame.K_BACKSPACE:
                    with self.info_lock:
                        self.username = self.username[:-1]
                elif event.unicode.isalnum() or event.unicode in ['_']:
                    with self.info_lock:
                        if len(self.username) < 15:
                            self.username += event.unicode
            elif client_state_local == "select_game_mode":
                if event.key == pygame.K_1:
                    with self.info_lock:
                        self.game_mode = "1vs1"
                        self.client_state = "menu"
                    self.click_sound.play()
                elif event.key == pygame.K_2:
                    with self.info_lock:
                        self.game_mode = "2vs2"
                        self.client_state = "menu"
                    self.click_sound.play()
            elif client_state_local == "enter_lobby_id":
                if event.key == pygame.K_RETURN:
                    with self.info_lock:
                        entered = self.entered_lobby_id
                        has_error = bool(self.error_message)
                    if entered and not has_error:
                        outbound_pkg = {"client_id": self.client_id, "request_type": "join_lobby", "room_id": entered, "game_mode": self.game_mode}
                    elif has_error:
                        with self.info_lock:
                            self.error_message = None
                            self.error_message_time = None
                            self.client_state = "menu"
                elif event.key == pygame.K_BACKSPACE:
                    with self.info_lock:
                        self.entered_lobby_id = self.entered_lobby_id[:-1]
                elif event.key == pygame.K_ESCAPE:
                    with self.info_lock:
                        self.error_message = None
                        self.error_message_time = None
                        self.entered_lobby_id = ""
                        self.client_state = "menu"
                elif event.unicode.isalnum():
                    with self.info_lock:
                        self.entered_lobby_id += event.unicode
            elif client_state_local == "menu":
                if event.key == pygame.K_1:
                    with self.info_lock:
                        gm = self.game_mode
                    outbound_pkg = {"client_id": self.client_id, "request_type": "find_random_game", "game_mode": gm}
                    if outbound_pkg:
                        with self.info_lock:
                            self.client_state = "searching"
                        self.click_sound.play()
                elif event.key == pygame.K_2:
                    with self.info_lock:
                        gm = self.game_mode
                    outbound_pkg = {"client_id": self.client_id, "request_type": "make_lobby", "game_mode": gm}
                    if outbound_pkg:
                        with self.info_lock:
                            self.client_state = "lobby"
                        self.click_sound.play()
                elif event.key == pygame.K_3:
                    with self.info_lock:
                        self.client_state = "enter_lobby_id"
                    self.click_sound.play()
            elif client_state_local == "lobby":
                if event.key == pygame.K_4:
                    outbound_pkg = {"client_id": self.client_id, "request_type": "start_the_game_as_host"}
                    self.click_sound.play()
                elif event.key == pygame.K_5:
                    outbound_pkg = {"client_id": self.client_id, "request_type": "destroy_lobby"}
                    self.click_sound.play()
            # Key press tracking consolidated: update key state in one lock for the event
            if event.key in self.key_pressed:
                with self.info_lock:
                    if not self.key_pressed[event.key]:
                        if event.key == pygame.K_SPACE:
                            shoots.append("arcane")
                        self.key_pressed[event.key] = True
                        inputs.append(("down", event.key))
        elif event.type == pygame.KEYUP:
            if event.key in self.key_pressed:
                with self.info_lock:
                    self.key_pressed[event.key] = False
                    inputs.append(("up", event.key))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            print(f"Mouse clicked at: {mouse_pos}, option_rects: {option_rects_local}") 
            for i, rect in enumerate(option_rects_local):
                if rect.collidepoint(mouse_pos):
                    print(f"Option {i} clicked") 
                    self.click_sound.play()
                    # All state updates prepared inside one short lock per branch
                    if client_state_local == "select_game_mode":
                        with self.info_lock:
                            if i == 0:
                                self.game_mode = "1vs1"
                                self.client_state = "menu"
                            elif i == 1:
                                self.game_mode = "2vs2"
                                self.client_state = "menu"
                    elif client_state_local == "menu":
                        if i == 0:
                            with self.info_lock:
                                gm = self.game_mode
                            outbound_pkg = {"client_id": self.client_id, "request_type": "find_random_game", "game_mode": gm}
                            if outbound_pkg:
                                with self.info_lock:
                                    self.client_state = "searching"
                        elif i == 1:
                            with self.info_lock:
                                gm = self.game_mode
                            outbound_pkg = {"client_id": self.client_id, "request_type": "make_lobby", "game_mode": gm}
                            if outbound_pkg:
                                with self.info_lock:
                                    self.client_state = "lobby"
                        elif i == 2:
                            with self.info_lock:
                                self.client_state = "enter_lobby_id"
                    elif client_state_local == "lobby":
                        if i == 1:
                            outbound_pkg = {"client_id": self.client_id, "request_type": "start_the_game_as_host"}
                        elif i == 2:
                            outbound_pkg = {"client_id": self.client_id, "request_type": "destroy_lobby"}

        # Perform network send outside the locks
        if outbound_pkg:
            self.send_request_to_server(outbound_pkg)

        return inputs, shoots

    def update(self, current_time, scale):
        if self.game_state in self.states and self.states[self.game_state] and self.run_client == False:
            self.states[self.game_state].update(current_time, scale, self)
        if self.run_client == True:
            with self.info_lock:
                if self.error_message and self.error_message_time and (current_time - self.error_message_time > 3000):
                    self.error_message = None
                    self.error_message_time = None

    def draw(self, scale):
        if self.game_state in self.states and self.states[self.game_state] and self.run_client == False:
            self.states[self.game_state].draw(self.scene, scale, self)
        else:
            # snapshot client_state and set/clear option_rects under info_lock
            with self.info_lock:
                client_state_local = self.client_state
                self.option_rects = []
            mouse_pos = pygame.mouse.get_pos()
            # Safely snapshot/clear game_over and related data under game_lock
            with self.game_lock:
                game_over_local = self.game_over
                winning_team_local = self.winning_team
                losing_team_local = self.losing_team
                if game_over_local:
                    # clear the shared state while still holding the lock
                    self.game_over = False
                    self.winning_team = None
                    self.losing_team = None
            if game_over_local:
                draw_game_over(self.scene, winning_team_local, losing_team_local)
                pygame.time.delay(3000)
                with self.info_lock:
                    self.client_state = "menu"
            elif client_state_local == "in_game":
                draw_game_state(self.scene, self.game_lock, self.game_world, self.previous_game_world, 
                               self.last_update_time, self.network_interval, self.fighter_animations, self.client_anim_states, self.images)
            elif client_state_local in ["searching", "waiting"]:
                draw_waiting_screen(self.scene)
            elif client_state_local == "lobby":
                with self.info_lock:
                    game_id_local = self.game_id
                draw_lobby_screen(self.scene, game_id_local)
            elif client_state_local == "menu":
                rects = draw_menu_screen(self.scene, mouse_pos)
                with self.info_lock:
                    self.option_rects = rects
            elif client_state_local == "enter_lobby_id":
                with self.info_lock:
                    entered_local = self.entered_lobby_id
                    error_local = self.error_message
                draw_enter_lobby_screen(self.scene, entered_local, error_local)
            elif client_state_local == "select_game_mode":
                rects = draw_game_mode_screen(self.scene, mouse_pos)
                with self.info_lock:
                    self.option_rects = rects
            elif client_state_local == "countdown":
                # countdown_value is protected by game_lock
                with self.game_lock:
                    countdown_local = self.countdown_value
                draw_countdown_screen(self.scene, countdown_local)
            elif client_state_local == "enter_username":
                with self.info_lock:
                    username_local = self.username
                draw_enter_username_screen(self.scene, username_local)
            else:
                draw_waiting_screen(self.scene)
            # display error message if any (read under info_lock)
            with self.info_lock:
                error_to_show = self.error_message
            if error_to_show:
                font = pygame.font.Font(None, 60)
                error_text = font.render(error_to_show, True, (255, 0, 0))
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