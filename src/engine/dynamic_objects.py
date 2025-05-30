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
            self.change_y += config.GLOBAL_GRAVITY  # Acceleration due to gravity

    def handle_platform_collision(self, platforms):
        """
        Checks for collision with any platform in the provided group.
        If falling and colliding with a platform, adjust the vertical position
        to stand on the platform and reset vertical velocity.
        """
        collided_platforms = pygame.sprite.spritecollide(self, platforms, False)
        for platform in collided_platforms:
            # Only resolve collision if falling downward.
            if self.change_y > 0: #   and self.rect.bottom <= platform.rect.bottom
                self.rect.bottom = platform.rect.top
                self.change_y = 0

# Player class that can later be expanded with collision detection and other behaviors.
class Player(DynamicObject):
    def __init__(self, x, y, width=30, height=30, color=(0, 0, 255), health=100, damage=100,
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

    def draw_health_bar(self, surface):
        """Draws a health bar above the player based on current health."""
        # Health bar dimensions
        bar_width = self.rect.width  # Same width as the player sprite
        bar_height = 10  # Height of the health bar
        bar_x = self.rect.x  # Align with the player's x position
        bar_y = self.rect.y - bar_height - 5  # Position above the player

        # Calculate the width of the health bar based on health percentage
        health_ratio = self.health / self.max_health
        health_width = bar_width * health_ratio

        # Draw background (gray) and health (red)
        pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))  # Background
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, health_width, bar_height))  # Health

    def update(self):
        # Call DynamicObject's update to apply gravity and movement.
        super().update()
        # Additional player-specific logic (collision, animation, etc.) may be added here.
        if self.is_dead():
            self.kill()
    def shoot(self):
        """Creates a projectile moving in the direction the NPC is facing."""
        velocity_x = 5 if self.facing_right else -5
        return Projectile(self.rect.centerx + (5 if self.facing_right else -5), self.rect.centery, velocity=(velocity_x, 0), image_path="src/assets/images/bullet.png", owner=self)

# Projectile class acts like a bullet or arrow.
class Projectile(DynamicObject):
    """A projectile that moves with a fixed velocity.
       Optionally, it can be affected by gravity (e.g., for arrows)."""
    def __init__(self, x, y, width=20, height=20, color=(255,255,0), velocity=(10, 0),damage=config.PROJECTILE_DAMAGE, use_gravity=False,image_path=None, owner=None):
        super().__init__(x, y, width, height, color,image_path)
        self.damage = damage
        self.velocity_x, self.velocity_y = velocity
        self.use_gravity = use_gravity
        self.owner = owner  # Store the owner of the projectile (the fighter who shot it)
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
    def __init__(self, x, y, width=70, height=70, color=(0, 0, 255), controls=None, health=config.PLAYER_HEALTH, damage=config.PLAYER_DAMAGE, image_path=None):
        super().__init__(x, y, width, height, color, health, damage, image_path)
        self.controls = controls or {}  # Store control keys for this fighter
        self.speed = config.PLAYER_SPEED  # Horizontal speed
        self.jump_strength = config.PLAYER_JUMP  # Vertical speed for jumping (negative to move up)
        self.facing_right = True  # Track the direction the fighter is facing (True for right, False for left)
        # Store the original image to avoid quality loss when flipping repeatedly
        self.original_image = self.image if image_path else pygame.Surface([width, height])
        self.original_image.fill(color) if not image_path else None

    def update(self):
        keys = pygame.key.get_pressed()  # Get the state of keyboard keys
        # Track previous direction to detect changes
        previous_facing = self.facing_right

        # Move left if the assigned 'left' key is pressed
        if self.controls.get("left") and keys[self.controls["left"]]:
            self.rect.x -= self.speed
            self.facing_right = False  # Face left
        # Move right if the assigned 'right' key is pressed
        elif self.controls.get("right") and keys[self.controls["right"]]:
            self.rect.x += self.speed
            self.facing_right = True  # Face right
        # If no movement keys are pressed, keep the last direction
        # (You can modify this to reset to a default direction if needed)

        # Update the image based on direction
        if self.facing_right != previous_facing:  # Only flip if direction changed
            self.image = pygame.transform.flip(self.original_image, not self.facing_right, False)

        # Initiate jump if the 'jump' key is pressed (only if on the ground)
        if self.controls.get("jump") and keys[self.controls["jump"]]:
            if self.change_y == 0:  # Simplistic ground check
                self.change_y = self.jump_strength

        # Call the parent's update to apply gravity and update movement
        super().update()

    

# NPC class represents non-player enemies.
class NPC(Player):
    """A simple enemy that moves horizontally and bounces at the screen edges."""
    def __init__(self, x, y, width=32, height=48, color=(255, 0, 0), speed=2, health=config.NPC_HEALTH, damage=config.NPC_DAMAGE,
                 image_path=None):
        super().__init__(x, y, width, height, color, health, damage, image_path)
        self.change_x = speed  # Set initial horizontal patrol speed
        self.facing_right = True  # Track the direction the NPC is facing (True for right, False for left)
        # Store the original image to avoid quality loss when flipping repeatedly
        self.original_image = self.image if image_path else pygame.Surface([width, height])
        self.original_image.fill(color) if not image_path else None

    def update(self):
        # Track previous direction to detect changes
        previous_facing = self.facing_right

        # Apply gravity and update vertical position
        self.calc_grav()
        self.rect.y += self.change_y
        from run_game import platforms
        # Check if the NPC is on a platform
        if self.change_y == 1:  # NPC is on a platform (not falling)
            collided_platforms = pygame.sprite.spritecollide(self, platforms, False)
            if collided_platforms:  # If on a platform
                platform = collided_platforms[0]  # Assume standing on the first collided platform
                # Check if NPC is at the left or right edge of the platform
                if self.rect.right >= platform.rect.right and self.change_x > 0:  # At right edge, moving right
                    self.change_x *= -1  # Reverse direction
                elif self.rect.left <= platform.rect.left and self.change_x < 0:  # At left edge, moving left
                    self.change_x *= -1  # Reverse direction
            else:
                # If not on a platform, check scene boundaries
                if self.rect.right > config.SCENE_WIDTH or self.rect.left < 0:
                    self.change_x *= -1
        else:
            # If falling, check scene boundaries
            if self.rect.right > config.SCENE_WIDTH or self.rect.left < 0:
                self.change_x *= -1

        # Update facing direction based on movement
        self.facing_right = self.change_x > 0

        # Update the image based on direction
        if self.facing_right != previous_facing:  # Only flip if direction changed
            self.image = pygame.transform.flip(self.original_image, not self.facing_right, False)

        # Update horizontal position
        self.rect.x += self.change_x

        projectile = self.shoot()
        from run_game import projectiles
        from run_game import all_sprites
        # projectiles.add(projectile)
        # all_sprites.add(projectile)
        super().update()