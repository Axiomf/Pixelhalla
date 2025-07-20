import pygame
import config
from .base import GameObject
import math  # Added for distance calculations

# "animations" is a dictionary with keys of states and values of corresponding frames in order
class DynamicObject(GameObject):
    """Base class for objects that can move or be affected by forces."""
    def __init__(self, x, y, width, height, color=None, image_path=None, animations=None):
        super().__init__(x, y, width, height, color, image_path)
        self.change_x = 0  # Horizontal velocity
        self.change_y = 0  # Vertical velocity
        self.state = "idle"
        # New animation attributes available for every DynamicObject
        self.animations = animations if animations is not None else {}
        self.current_animation = "idle" if "idle" in self.animations else (list(self.animations.keys())[0] if self.animations else "idle")
        self.current_frame = 0
        self.animation_speeds = {"idle": 75, "death": 200, "walk": 75, "hurt": 200, "shoot": 100, "attack" : 100}  # ms per frame
        self.last_update = pygame.time.get_ticks()
        self.is_dying = False  # New flag to track death animation
        self.is_hurting = False  # New flag to track hurt animation
        self.hurt_start_time = 0  # Time when hurt animation started
        self.hurt_duration = 1000  # Duration of hurt animation in ms (1 second)
        self.original_change_x = 0  # Store original horizontal velocity
        self.last_hurt_time = 0  # Track the last time hurt occurred
        self.is_shooting = False
        self.shoot_start_time = 0
        self.shoot_duration = 500  # Duration of shoot animation in ms, adjust based on animation length
        self.last_shoot_time = 0  # Track the last time shoot occurred
        self.is_attacking = False
        self.attack_start_time = 0
        self.attack_duration = 500  # Duration of shoot animation in ms, adjust based on animation length
        self.last_attack_time = 0  # Track the last time shoot occurred
        
        self.freeze = False # it can not move while being freezed
        self.freeze_duration = 10 # lenght of freeze duration
        self.freezed_time = 0 # the time it got freezed

    def _cycle_frame(self):
        # Advance to the next frame and update the sprite image
        self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_animation])
        self.image = self.animations[self.current_animation][self.current_frame]
        if hasattr(self, "facing_right"):
            self.image = pygame.transform.flip(self.image, not self.facing_right, False)

    def update_animation(self):
        # Retrieve the current time for animation timing
        now = pygame.time.get_ticks()
        frame_duration = self.animation_speeds.get(self.current_animation, 100)
        # Only cycle frames here
        if self.animations.get(self.current_animation) and now - self.last_update > frame_duration:
            self.last_update = now
            self._cycle_frame()
        # Hurt and shoot state handling is checked each update regardless of frame timing
        self._handle_hurt_animation(now)
        self._handle_shoot_animation(now)
        self._handle_attack_animation(now)
        # Debug: Check if hurt frames are loaded
        if self.current_animation == "hurt" and hasattr(self, "animations"):
            if "hurt" in self.animations:
                print(f"Hurt animation loaded with {len(self.animations['hurt'])} frames at position {self.rect.x}")
            else:
                print(f"No hurt animation frames loaded for object at position {self.rect.x}")

    def update_state(self):
        # Only update the state if not currently in a death, hurt, or shoot animation
        if not self.is_hurting and not self.is_shooting and (not hasattr(self, 'is_dying') or not self.is_dying):
            # Determine state based on vertical and horizontal velocities
            if self.change_y >= 5:
                self.state = "falling"  # Falling when vertical speed is high
            elif self.change_x != 0:
                self.state = "walk"     # Walking when there is horizontal movement
            else:
                self.state = "idle"     # Idle otherwise
            # Synchronize the current animation with the determined state if available
        if self.is_hurting and "hurt" in self.animations:
            self.state = "hurt"
        if self.is_shooting and "shoot" in self.animations:
            self.state = "shoot"
        if self.is_attacking and "attack" in self.animations:
            self.state = "attack"
        if self.state in self.animations:
            self.current_animation = self.state

    def update(self):
        self.calc_grav()  # Adjust vertical velocity due to gravity
        if self.freeze:
            self.change_x = 0
            self.change_y = 0
        self.rect.x += self.change_x  # Update horizontal position
        self.rect.y += self.change_y  # Update vertical position
        self.update_state()
        self.update_animation()

        
        #if not self.change_y==0:
            #print(self.change_y)
    
    def calc_grav(self):
        # Basic gravity simulation: if not already falling, start falling
        
        if self.change_y == 0:
            self.change_y = 0.1
        else:
            self.change_y += config.GLOBAL_GRAVITY  # Acceleration due to gravity

    
    def handle_platform_collision(self, platforms):
        """
        Checks for collision with any platform in the provided group.
        If falling and colliding with a platform, adjust the vertical position
        to stand on the platform and reset vertical velocity.
        """
        collided_platforms = pygame.sprite.spritecollide(self, platforms, False)
        for platform in collided_platforms:
            # Only resolve collision if falling downward
            if self.change_y > 0:
                self.rect.bottom = platform.rect.top
                self.change_y = 0
                return False
        return True

    def _handle_hurt_animation(self, now):
        # If hurt duration has passed, reset hurt state
        if self.is_hurting and now - self.hurt_start_time >= self.hurt_duration:
            self.is_hurting = False
            self.change_x = self.original_change_x  # Restore original movement
            self.state = "walk" if self.change_x != 0 else "idle"
            self.current_animation = self.state

    def _handle_shoot_animation(self, now):
        # If shoot duration has passed, reset shoot state
        if self.is_shooting and now - self.shoot_start_time >= self.shoot_duration:
            self.is_shooting = False
            self.change_x = self.original_change_x  # Restore original movement
            self.state = "walk" if self.change_x != 0 else "idle"
            self.current_animation = self.state
    def _handle_attack_animation(self, now):
        # If attack duration has passed, reset attack state
        if self.is_attacking and now - self.attack_start_time >= self.attack_duration:
            self.is_attacking = False
            self.change_x = self.original_change_x  # Restore original movement
            self.state = "walk" if self.change_x != 0 else "idle"
            self.current_animation = self.state
