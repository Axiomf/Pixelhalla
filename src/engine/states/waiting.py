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
            self.client_socket.settimeout(5.0)
            # Receive client_id from server
            self.client_id = pickle.loads(self.client_socket.recv(2048))
            print(f"Received client_id: {self.client_id}")
            # Send find_random_game request
            join_request = {
                "request_type": "find_random_game",
                "client_id": self.client_id,
                "game_mode": "1vs1",  # or "2vs2" based on user selection
                "username": state_manager.username or "default_user",
                "fighter_id": state_manager.fighter1_id or "default_fighter",
                "map_name": state_manager.current_map or "map1"
            }
            print(f"Sending find_random_game request: {join_request}")
            self.client_socket.send(pickle.dumps(join_request))
            self.client_socket.settimeout(None)
            self.state_manager.is_initialized = True
        except socket.timeout:
            print(f"Connection timeout to server {self.server}:{self.port}")
            self.state_manager.error_message = "Connection to server timed out"
            if self.client_socket:
                self.client_socket.close()
            self.state_manager.client_socket = None
            self.state_manager.client_id = None
            self.state_manager.is_initialized = False
            self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)
        except pickle.UnpicklingError as e:
            print(f"Unpickling error: {e}")
            self.state_manager.error_message = "Invalid server response"
            if self.client_socket:
                self.client_socket.close()
            self.state_manager.client_socket = None
            self.state_manager.client_id = None
            self.state_manager.is_initialized = False
            self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)
        except Exception as e:
            print(f"Connection error: {e}")
            self.state_manager.error_message = f"Failed to connect to server: {str(e)}"
            if self.client_socket:
                self.client_socket.close()
            self.state_manager.client_socket = None
            self.state_manager.client_id = None
            self.state_manager.is_initialized = False
            self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)
            print(f"Returning to Map Select due to connection error: {str(e)}")

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
                self.client_id = None
                state_manager.is_initialized = False
                state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                state_manager.last_click_time = current_time
                pygame.event.clear()

    def update(self, current_time, scale, state_manager):
        if not hasattr(self, 'client_id') or self.client_id is None:
            print(f"Update skipped: client_id is {getattr(self, 'client_id', 'undefined')}")
            return
        if current_time - self.last_check_time > self.check_interval * 1000:
            print("Checking for game start")
            try:
                self.client_socket.settimeout(3.0)  # Increased timeout for server response
                # Receive response from server asynchronously
                data = self.client_socket.recv(4096)
                if not data:
                    print(f"No data received from server for client {self.client_id}")
                    self.state_manager.error_message = "No response from server"
                    if self.client_socket:
                        self.client_socket.close()
                    state_manager.client_socket = None
                    state_manager.client_id = None
                    self.client_id = None
                    state_manager.is_initialized = False
                    state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                    return
                response = pickle.loads(data)
                print(f"Received response: {response}")
                self.client_socket.settimeout(None)
                if not isinstance(response, dict):
                    print(f"Error: Received non-dict response: {response}")
                    self.state_manager.error_message = f"Invalid server response: {response}"
                    if self.client_socket:
                        self.client_socket.close()
                    state_manager.client_socket = None
                    state_manager.client_id = None
                    self.client_id = None
                    state_manager.is_initialized = False
                    state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                    return
                request_type = response.get("request_type")
                print(f"Response request_type: {request_type}")
                if request_type == "game_started":
                    state_manager.client_socket = self.client_socket
                    state_manager.client_id = self.client_id
                    state_manager.game_id = response.get("game_id")
                    state_manager.opponents = response.get("members", [])
                    print(f"Transitioning to multiplayer state with game_id: {state_manager.game_id}, opponents: {state_manager.opponents}")
                    state_manager.change_state(config.GAME_STATE_MULTIPLATER, PlayingState_Multiplayer(self.scene, state_manager))
                elif request_type == "game_update":
                    print(f"Unexpected game_update received in WaitingState: {response}")
                    self.state_manager.error_message = "Received unexpected game update"
                    if self.client_socket:
                        self.client_socket.close()
                    state_manager.client_socket = None
                    state_manager.client_id = None
                    self.client_id = None
                    state_manager.is_initialized = False
                    state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                elif request_type == "error":
                    self.state_manager.error_message = response.get("message", "Server error")
                    print(f"Server error: {self.state_manager.error_message}")
                    if self.client_socket:
                        self.client_socket.close()
                    state_manager.client_socket = None
                    state_manager.client_id = None
                    self.client_id = None
                    state_manager.is_initialized = False
                    state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                else:
                    print(f"Unknown response: {response}")
                    # Instead of closing connection, wait for next response
            except socket.timeout:
                print(f"Timeout waiting for server response for client {self.client_id}")
                # Continue in waiting state
            except pickle.UnpicklingError as e:
                print(f"Unpickling error: {e}")
                self.state_manager.error_message = "Invalid server response"
                if self.client_socket:
                    self.client_socket.close()
                state_manager.client_socket = None
                state_manager.client_id = None
                self.client_id = None
                state_manager.is_initialized = False
                state_manager.change_state(config.GAME_STATE_MAP_SELECT)
            except Exception as e:
                print(f"Error receiving response: {e}")
                self.state_manager.error_message = f"Lost connection to server: {str(e)}"
                if self.client_socket:
                    self.client_socket.close()
                state_manager.client_socket = None
                state_manager.client_id = None
                self.client_id = None
                state_manager.is_initialized = False
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