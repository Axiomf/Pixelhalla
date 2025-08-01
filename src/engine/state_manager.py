import pygame
import config
from src.engine.states.loading import LoadingState
from src.engine.states.mode_select import ModeSelectState
from src.engine.states.map_select import MapSelectState
from src.engine.states.fighter_select import FighterSelectState
from src.engine.states.playing import PlayingState
from src.engine.states.multiplayer import MultiplayerState

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
        # Initialize states
        self.states = {
            config.GAME_STATE_LOADING: LoadingState(scene),
            config.GAME_STATE_MODE_SELECT: ModeSelectState(scene),
            config.GAME_STATE_MAP_SELECT: MapSelectState(scene),
            config.GAME_STATE_FIGHTER_SELECT: FighterSelectState(scene),
            config.GAME_STATE_PLAYING: PlayingState(scene),
            config.GAME_STATE_MULTIPLATER: MultiplayerState(scene)
        }
        self.current_map = None
        self.last_click_time = 0
        # Load click sound
        self.click_sound = pygame.mixer.Sound("src/assets/sounds/mixkit-stapling-paper-2995.wav")
        self.blood_sound = pygame.mixer.Sound("src/assets/sounds/blood2.wav")
        self.win_sound = pygame.mixer.music.load("src/assets/sounds/win.mp3")
        self.level_complete_sound = pygame.mixer.Sound("src/assets/sounds/level complete.mp3")
        self.game_over = pygame.mixer.music.load("src/assets/sounds/game-over-classic-206486.mp3")
        self.game_over_boss = pygame.mixer.music.load("src/assets/sounds/possessed-laugh-94851.mp3")
        # Load menu music (only load once)
        pygame.mixer.music.load("src/assets/sounds/LevelHellboy.mp3.mpeg")
        pygame.mixer.music.play(-1)

    def handle_event(self, event, current_time, scale):
        """Handle events for the current state."""
        self.states[self.game_state].handle_event(event, current_time, scale, self.current_map, self)

    def update(self, current_time, scale):
        """Update the current state."""
        self.states[self.game_state].update(current_time, scale, self)

    def draw(self, scale):
        """Draw the current state."""
        self.states[self.game_state].draw(self.scene, scale, self)

    def change_state(self, new_state):
        """Change the current game state."""
        previous_state = self.game_state
        self.game_state = new_state
        # Manage music based on state
        if new_state != config.GAME_STATE_PLAYING and (previous_state == config.GAME_STATE_PLAYING or not pygame.mixer.music.get_busy()):
            pygame.mixer.music.play(-1)  # Play menu music in loop when leaving PlayingState or if not playing
        elif new_state == config.GAME_STATE_PLAYING and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()  # Stop menu music when entering PlayingState