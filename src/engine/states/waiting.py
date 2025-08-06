import pygame
import config
from src.engine.states.base_state import BaseState
from src.engine.states.client_side import PlayingState_Multiplayer
import socket
import pickle
import time

class WaitingState(BaseState):
    def __init__(self, scene, state_manager):
        super().__init__(scene)
        self.scene = scene
        self.state_manager = state_manager
        self.font = pygame.font.Font(None, 60)
        self.button_color = (0, 128, 255)
        self.background = pygame.image.load("src/assets/images/background/blue-preview.png").convert_alpha()
        self.background = pygame.transform.scale(self.background, (config.SCENE_WIDTH, config.SCENE_HEIGHT))
        self.back_button = pygame.Rect(20, 20, 100, 50)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_id = None
        self.server = "127.0.0.1"
        self.port = 5555
        self.last_check_time = 0
        self.check_interval = 1.0
        print(f"Initializing WaitingState with username: {state_manager.username}, fighter_id: {state_manager.fighter1_id}, map_name: {state_manager.current_map}")
        try:
            self.client_socket.connect((self.server, self.port))
            # self.client_socket.settimeout(5.0)
            # join_request = {
            #     "request_type": "join",
            #     "username": state_manager.username,
            #     "fighter_id": state_manager.fighter1_id,
            #     "map_name": state_manager.current_map
            # }
            # print(f"Sending join request: {join_request}")
            # self.client_socket.send(pickle.dumps(join_request))
            # response = pickle.loads(self.client_socket.recv(2048))
            # print(f"Received join response: {response}")
            # self.client_socket.settimeout(None)
            # if response["request_type"] == "joined":
            #     self.client_id = response["client_id"]
            #     print(f"Client ID set to: {self.client_id}")
            # elif state_manager.fighter_type:
            #     self.state_manager.error_message = response.get("message", "Failed to join server")
            #     print(f"Join failed, error message: {self.state_manager.error_message}")
            #     if self.client_socket:
            #         self.client_socket.close()
            #     self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)
        except Exception as e:
            print(f"Connection error: {e}")
            self.state_manager.error_message = "Failed to connect to server. Is the server running?"
            if self.client_socket:
                self.client_socket.close()
            self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)
            print(f"Returning to Map Select due to connection error")

    def handle_event(self, event, current_time, scale, current_map, state_manager):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_time - state_manager.last_click_time > config.CLICK_COOLDOWN:
            pulsed_back_button = pygame.Rect(self.back_button.x - scale / 2, self.back_button.y - scale / 2, 
                                            self.back_button.width + scale, self.back_button.height + scale)
            if pulsed_back_button.collidepoint(event.pos):
                state_manager.click_sound.play()
                if self.client_socket:
                    self.client_socket.close()
                state_manager.client_socket = None
                state_manager.client_id = None
                state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                state_manager.last_click_time = current_time
                pygame.event.clear()

    def update(self, current_time, scale, state_manager):
        if state_manager.is_initialized == False:
            self.client_socket.settimeout(5.0)
            join_request = {
                "request_type": "join",
                "username": "ali",
                "fighter_id": state_manager.fighter1_id,
                "map_name": state_manager.current_map
            }
            print(f"Sending join request: {join_request}")
            self.client_socket.send(pickle.dumps(join_request))
            response = pickle.loads(self.client_socket.recv(2048))
            print(f"Received join response: {response}")
            self.client_socket.settimeout(None)
            if response["request_type"] == "joined":
                self.client_id = response["client_id"]
                print(f"Client ID set to: {self.client_id}")
            elif state_manager.fighter_type:
                self.state_manager.error_message = response.get("message", "Failed to join server")
                print(f"Join failed, error message: {self.state_manager.error_message}")
                if self.client_socket:
                    self.client_socket.close()
                self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)
            state_manager.is_initialized = True
        if not hasattr(self, 'client_id') or self.client_id is None:
            print(f"Update skipped: client_id is {getattr(self, 'client_id', 'undefined')}")
            return
        if current_time - self.last_check_time > self.check_interval * 1000:
            print("Hi")
            try:
                self.client_socket.settimeout(1.0)
                match_request = {"request_type": "check_match", "client_id": self.client_id, "map_name": state_manager.current_map}
                print(f"Sending check_match request: {match_request}")
                self.client_socket.send(pickle.dumps(match_request))
                response = pickle.loads(self.client_socket.recv(2048))
                print(f"Received match response: {response}")
                self.client_socket.settimeout(None)
                print(f"Response request_type: {response['request_type']}")
                if response["request_type"] == "matched":
                    state_manager.client_socket = self.client_socket
                    state_manager.client_id = self.client_id
                    state_manager.change_state(config.GAME_STATE_MULTIPLATER, PlayingState_Multiplayer(self.scene, state_manager))
                    print(f"Matched, moving to multiplayer state with game_id: {response['game_id']}")
                elif response["request_type"] == "error":
                    state_manager.error_message = response.get("message", "Match check failed")
                    print(f"Match error: {state_manager.error_message}")
                    if self.client_socket:
                        self.client_socket.close()
                    state_manager.client_socket = None
                    state_manager.client_id = None
                    state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                elif response["request_type"] == "waiting":
                    print("Still waiting for opponent")
                    # Stay in WaitingState
                else:
                    print(f"Unknown response: {response}")
                    state_manager.error_message = "Unknown server response"
                    if self.client_socket:
                        self.client_socket.close()
                    state_manager.client_socket = None
                    state_manager.client_id = None
                    state_manager.change_state(config.GAME_STATE_MAP_SELECT)
            except Exception as e:
                print(f"Match check error: {e}")
                state_manager.error_message = "Lost connection to server"
                if self.client_socket:
                    self.client_socket.close()
                state_manager.client_socket = None
                state_manager.client_id = None
                state_manager.change_state(config.GAME_STATE_MAP_SELECT)
            self.last_check_time = current_time

    def draw(self, scene, scale, state_manager):
        mouse_pos = pygame.mouse.get_pos()
        scene.blit(self.background, (0, 0))
        if state_manager.error_message:
            error_text = self.font.render(state_manager.error_message, True, (255, 0, 0))
            error_rect = error_text.get_rect(center=(config.SCENE_WIDTH // 2, config.SCENE_HEIGHT // 2 - 150))
            scene.blit(error_text, error_rect)
        if hasattr(self, 'client_id') and self.client_id is not None:
            id_text = self.font.render(f"Your ID: {self.client_id}", True, (255, 255, 255))
            id_rect = id_text.get_rect(center=(config.SCENE_WIDTH // 2, config.SCENE_HEIGHT // 2 - 100))
            scene.blit(id_text, id_rect)
        waiting_text = self.font.render("Waiting for opponent...", True, (255, 255, 255))
        waiting_rect = waiting_text.get_rect(center=(config.SCENE_WIDTH // 2, config.SCENE_HEIGHT // 2))
        scene.blit(waiting_text, waiting_rect)
        pulsed_back_button = pygame.Rect(self.back_button.x - scale / 2, self.back_button.y - scale / 2, 
                                        self.back_button.width + scale, self.back_button.height + scale)
        pygame.draw.rect(scene, (0, 200, 255) if pulsed_back_button.collidepoint(mouse_pos) else self.button_color, pulsed_back_button)
        back_text = self.font.render("Back", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=pulsed_back_button.center)
        scene.blit(back_text, back_text_rect)