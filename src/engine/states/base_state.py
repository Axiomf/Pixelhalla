class BaseState:
    """Base class for all game states (e.g., menu, playing, paused)."""
    def __init__(self, scene):
        self.scene = scene
    
    def handle_event(self, event, current_time, scale, state_manager):
        """Handle events for the current state."""
        raise NotImplementedError
    
    def update(self, current_time, scale, state_manager):
        """Update logic for the current state."""
        raise NotImplementedError
    
    def draw(self, scene, scale, state_manager):
        """Draw the current state."""
        raise NotImplementedError