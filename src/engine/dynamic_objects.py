# my h & g keys are broken so I put them here
import pygame
import config
from .base import GameObject

# Base class for objects that require movement or are affected by physics (e.g., gravity).
class DynamicObject(GameObject):
    """Base class for objects that can move or be affected by forces."""
    def __init__(self, x, y, width, height, color, image_path=None):
        super().__init__(x, y, width, height, color, image_path)
        self.change_x = 0  # Horizontal velocity
        self.change_y = 0  # Vertical velocity

    def update(self):
        self.calc_grav()  # Adjust vertical velocity due to gravity
        self.rect.x += self.change_x  # Update horizontal position
        self.rect.y += self.change_y  # Update vertical position

    def calc_grav(self):
        # Basic gravity simulation: if not already falling, start falling.
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += 0.35  # Acceleration due to gravity

    def handle_platform_collision(self, platforms):
        """
        Checks for collision with any platform in the provided group.
        If falling and colliding with a platform, adjust the vertical position
        to stand on the platform and reset vertical velocity.
        """
        collided_platforms = pygame.sprite.spritecollide(self, platforms, False)
        for platform in collided_platforms:
            # Only resolve collision if falling downward.
            if self.change_y > 0 and self.rect.bottom <= platform.rect.bottom:
                self.rect.bottom = platform.rect.top
                self.change_y = 0

# Player class that can later be expanded with collision detection and other behaviors.
class Player(DynamicObject):
    def __init__(self, x, y, width=30, height=30, color=(0, 0, 255), health=100, damage=config.PLAYER_DAMAGE,
                 image_path=None):
        super().__init__(x, y, width, height, color,image_path)
        self.health = health          # Current health of the player
        self.max_health = health      # Maximum health for the player
        self.damage = damage          # Damage that this player can inflict

    def take_damage(self, amount):
        """Subtracts the given amount from player's health."""
        self.health -= amount
        if self.health < 0:
            self.health = 0  # Ensure health doesn't go negative

    def is_dead(self):
        """Returns True if the player's health has dropped to 0."""
        return self.health <= 0

    def update(self):
        # Call DynamicObject's update to apply gravity and movement.
        super().update()
        # Additional player-specific logic (collision, animation, etc.) may be added here.

# Projectile class acts like a bullet or arrow.
class Projectile(DynamicObject):
    """A projectile that moves with a fixed velocity.
       Optionally, it can be affected by gravity (e.g., for arrows)."""
    def __init__(self, x, y, width=5, height=5, color=(255,255,0), velocity=(10, 0), use_gravity=False,image_path=None):
        super().__init__(x, y, width, height, color,image_path)
        self.velocity_x, self.velocity_y = velocity
        self.use_gravity = use_gravity
        # For projectiles we typically do not use the standard gravity unless needed.
        if not self.use_gravity:
            self.change_y = 0  

    def update(self):
        # Move based on fixed velocity.
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        # Optionally apply gravity.
        if self.use_gravity:
            self.calc_grav()
            self.rect.y += self.change_y

# Fighter class implements control logic for player actions such as movement, jumping, and shooting.
class Fighter(Player):
    """
    Fighter class with controls for left/right movement, jumping, and shooting.
    Each fighter can have custom keys assigned via the `controls` dict.
    Example controls dict:
        {
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_w,
            "shoot": pygame.K_SPACE
        }
    """
    def __init__(self, x, y, width=30, height=30, color=(0, 0, 255), controls=None, health=100, damage=config.PLAYER_DAMAGE,
                 image_path=None):
        super().__init__(x, y, width, height, color, health, damage,image_path)
        self.controls = controls or {}  # Store control keys for this fighter
        self.speed = 5                 # Horizontal speed
        self.jump_strength = -15       # Vertical speed for jumping (negative to move up)

    def update(self):
        keys = pygame.key.get_pressed()  # Get the state of keyboard keys
        # Move left if the assigned 'left' key is pressed.
        if self.controls.get("left") and keys[self.controls["left"]]:
            self.rect.x -= self.speed
        # Move right if the assigned 'right' key is pressed.
        if self.controls.get("right") and keys[self.controls["right"]]:
            self.rect.x += self.speed
        # Initiate jump if the 'jump' key is pressed (only if on the ground).
        if self.controls.get("jump") and keys[self.controls["jump"]]:
            if self.change_y == 0:  # Simplistic ground check
                self.change_y = self.jump_strength
        # Call the parent's update to apply gravity and update movement.
        super().update()

    def shoot(self):
        """Creates a projectile moving to the right from the fighter's position."""
        # For simplicity, the projectile moves right. You can enhance this by using a facing direction.
        return Projectile(self.rect.centerx, self.rect.centery, velocity=(10, 0))

# NPC class represents non-player enemies.
class NPC(Player):
    """A simple enemy that moves horizontally and bounces at the screen edges."""
    def __init__(self, x, y, width=30, height=30, color=(255, 0, 0), speed=2, health=100, damage=config.NPC_DAMAGE,
                 image_path=None):
        super().__init__(x, y, width, height, color, health, damage,image_path)
        self.change_x = speed  # Set initial horizontal patrol speed

    def update(self):
        self.rect.x += self.change_x  # Move enemy horizontally
        # Reverse direction when enemy hits either side of the game scene
        if self.rect.right > config.SCENE_WIDTH or self.rect.left < 0:
            self.change_x *= -1
        # Apply gravity and update vertical position
        self.calc_grav()
        self.rect.y += self.change_y