import pygame
import config
from src.engine.states.loading import LoadingState
from src.engine.states.mode_select import ModeSelectState
from src.engine.states.map_select import MapSelectState
from src.engine.states.fighter_select import FighterSelectState
from src.engine.states.playing import PlayingState
from src.engine.states.multiplayer import MultiplayerState
from src.engine.states.client_side import PlayingState_Multiplayer
from src.engine.states.waiting import WaitingState

class StateManager:
    def __init__(self, scene):
        self.scene = scene
        self.game_state = config.GAME_STATE_LOADING
        self.game_mode = None  # Track single or multi mode
        self.current_map = None  # Track selected map
        self.fighter1_id = None  # Track selected fighter1
        self.fighter2_id = None  # Track selected fighter2
        self.fighter_select_phase = 1  # Track which fighter is being selected (1 for fighter1, 2 for fighter2 in multi mode)
        self.last_click_time = 0
        self.win_boss = False
        self.win_fighter = False
        self.multi_mode = None
        self.is_initialized = False
        self.username = None
        self.client_socket = None
        self.client_id = None
        self.game_id = None
        self.opponents = []  # Track opponent client IDs for multiplayer
        self.fighter_type = None
        self.error_message = ""  # Track error messages
        # Initialize states (excluding WaitingState and PlayingState_Multiplayer)
        self.states = {
            config.GAME_STATE_LOADING: LoadingState(scene),
            config.GAME_STATE_MODE_SELECT: ModeSelectState(scene),
            config.GAME_STATE_MAP_SELECT: MapSelectState(scene),
            config.GAME_STATE_FIGHTER_SELECT: FighterSelectState(scene),
            config.GAME_STATE_PLAYING: PlayingState(scene),
        }
        # Load click sound
        self.click_sound = pygame.mixer.Sound("src/assets/sounds/mixkit-stapling-paper-2995.wav")
        self.blood_sound = pygame.mixer.Sound("src/assets/sounds/blood2.wav")
        self.win_sound = pygame.mixer.Sound("src/assets/sounds/win.mp3")
        # Load menu music
        try:
            pygame.mixer.music.load("src/assets/sounds/LevelHellboy.mp3.mpeg")
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"Error loading menu music: {e}")
            self.error_message = "Failed to load menu music"

    def handle_event(self, event, current_time, scale):
        """Handle events for the current state."""
        if self.game_state in self.states and self.states[self.game_state]:
            self.states[self.game_state].handle_event(event, current_time, scale, self.current_map, self)

    def update(self, current_time, scale):
        """Update the current state."""
        if self.game_state in self.states and self.states[self.game_state]:
            self.states[self.game_state].update(current_time, scale, self)

    def draw(self, scale):
        """Draw the current state."""
        if self.game_state in self.states and self.states[self.game_state]:
            self.states[self.game_state].draw(self.scene, scale, self)
        if self.error_message:
            font = pygame.font.Font(None, 60)
            error_text = font.render(self.error_message, True, (255, 0, 0))
            error_rect = error_text.get_rect(center=(config.SCENE_WIDTH // 2, config.SCENE_HEIGHT // 2 - 150))
            self.scene.blit(error_text, error_rect)

    def change_state(self, new_state, state_instance=None):
        """Change the current game state."""
        previous_state = self.game_state
        self.game_state = new_state
        # Initialize WaitingState or PlayingState_Multiplayer only when needed
        if new_state == config.GAME_STATE_WAITING and not self.states[new_state]:
            # Ensure required variables are set before entering WaitingState
            if not self.username:
                self.username = "default_user"
            if not self.fighter1_id:
                self.fighter1_id = "default_fighter"
            if not self.current_map:
                self.current_map = "map1"
            self.states[new_state] = WaitingState(self.scene, self)
        elif new_state == config.GAME_STATE_MULTIPLATER and not self.states[new_state]:
            self.states[new_state] = PlayingState_Multiplayer(self.scene, self)
        elif state_instance:
            self.states[new_state] = state_instance
        # Manage music based on state
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