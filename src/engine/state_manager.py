import pygame
import config
from src.engine.states.loading import LoadingState
from src.engine.states.mode_select import ModeSelectState
from src.engine.states.map_select import MapSelectState
from src.engine.states.fighter_select import FighterSelectState
from src.engine.states.playing import PlayingState

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
        # Initialize states
        self.states = {
            config.GAME_STATE_LOADING: LoadingState(scene),
            config.GAME_STATE_MODE_SELECT: ModeSelectState(scene),
            config.GAME_STATE_MAP_SELECT: MapSelectState(scene),
            config.GAME_STATE_FIGHTER_SELECT: FighterSelectState(scene),
            config.GAME_STATE_PLAYING: PlayingState(scene)
        }

    def handle_event(self, event, current_time, scale):
        """Handle events for the current state."""
        self.states[self.game_state].handle_event(event, current_time, scale, self)

    def update(self, current_time, scale):
        """Update the current state."""
        self.states[self.game_state].update(current_time, scale, self)

    def draw(self, scale):
        """Draw the current state."""
        self.states[self.game_state].draw(self.scene, scale, self)

    def change_state(self, new_state):
        """Change the current game state."""
        self.game_state = new_state