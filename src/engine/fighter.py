import math
import pygame
import config
from .dynamic_objects import DynamicObject
from .player import Player
from .projectile import Projectile

class Fighter(Player):
    def __init__(self, x, y, width=70, height=70, color=None, controls=None, health=config.PLAYER_HEALTH, 
                 damage=config.PLAYER_DAMAGE, image_path=None, platforms=None, animations=None):
        super().__init__(x, y, width, height, color, health, damage, image_path, animations)
        self.controls = controls or {}  # Store control keys for this fighter
        self.speed = config.PLAYER_SPEED  # Horizontal speed
        self.jump_strength = config.PLAYER_JUMP  # Vertical speed for jumping (negative to move up)
        self.platforms = platforms  # Store platforms group
        self.powered = False
        self.left_duration_powerup = 0
        self.started_powerup = 0
        self.powered_up_type = ""
        self.powered_up_amount = 0

        self.supershot = False
        self.supershot_amount = 1

        # Store the original image to avoid quality loss when flipping repeatedly
        self.original_image = self.image if image_path else pygame.Surface([width, height]) if color else None
        if self.original_image and not image_path:
            self.original_image.fill(color)

    def upgrade(self, type, amount):
        self.powered_up_amount = amount
        self.started_powerup = pygame.time.get_ticks() 
        self.left_duration_powerup = 5000  # 5 seconds in milliseconds
        if type == "damage":
            self.damage += amount
        elif type == "double_jump":
            self.jump_strength -= amount
        elif type == "shield":
            self.shield = True
        elif type == "supershot":
            self.supershot = True
            self.supershot_amount += amount 
        
        self.powered = True
        self.powered_up_type = type

    def check_power_up(self):
        if not self.powered:
            return
        now = pygame.time.get_ticks()
        if now - self.started_powerup >= self.left_duration_powerup:
            if self.powered_up_type == "damage":
                self.damage -= self.powered_up_amount
            elif self.powered_up_type == "double_jump":
                self.jump_strength += self.powered_up_amount
            elif self.powered_up_type == "shield":
                self.shield = False
            self.powered = False
            self.left_duration_powerup = 0
            self.started_powerup = 0
            self.powered_up_type = ""
            self.powered_up_amount = 0

    def update(self):
        self.check_power_up()
        keys = pygame.key.get_pressed()  # Get the state of keyboard keys
        # Track previous direction to detect changes
        previous_facing = self.facing_right

        # Move left if the assigned 'left' key is pressed
        if self.controls.get("left") and keys[self.controls["left"]]:
            self.change_x = (-1) * self.speed
            self.facing_right = False  # Face left
        # Move right if the assigned 'right' key is pressed
        elif self.controls.get("right") and keys[self.controls["right"]]:
            self.change_x = self.speed
            self.facing_right = True  # Face right
        else:
            self.change_x = 0  # Stop horizontal movement if no keys are pressed

        # Initiate jump if the 'jump' key is pressed (only if on the ground)
        if self.controls.get("jump") and keys[self.controls["jump"]]:
            if self.change_y == 0:  # Simplistic ground check
                self.change_y = self.jump_strength

        # Check for horizontal collisions with platforms
        if self.platforms:
            self.rect.x += self.change_x
            collided_platforms = pygame.sprite.spritecollide(self, self.platforms, False)
            for platform in collided_platforms:
                if self.change_x > 0 and self.rect.right > platform.rect.left:  # Moving right, hit left side of platform
                    self.rect.right = platform.rect.left
                    self.change_x = 0
                elif self.change_x < 0 and self.rect.left < platform.rect.right:  # Moving left, hit right side of platform
                    self.rect.left = platform.rect.right
                    self.change_x = 0
            # Check for vertical collisions when moving upward (jumping)
            self.rect.y += self.change_y
            collided_platforms = pygame.sprite.spritecollide(self, self.platforms, False)
            for platform in collided_platforms:
                if self.change_y < 0 and self.rect.top < platform.rect.bottom:  # Moving up, hit bottom of platform
                    self.rect.top = platform.rect.bottom
                    self.change_y = 0

        # Check for scene boundaries
        if self.rect.right + self.change_x > config.SCENE_WIDTH:
            self.rect.right = config.SCENE_WIDTH
            self.change_x = 0
        elif self.rect.left + self.change_x < 0:
            self.rect.left = 0
            self.change_x = 0

        # Update the image based on direction
        if self.facing_right != previous_facing and not self.animations.get(self.current_animation):  # Only flip if no animation
            if self.original_image:  # Only flip if original_image exists
                self.image = pygame.transform.flip(self.original_image, not self.facing_right, False)

        # Call the parent's update to apply gravity and update movement
        super().update()

    def shoot(self):
        """Creates a projectile moving in the direction the player is facing."""
        if self.is_shoot():
            now = pygame.time.get_ticks()
            if not self.is_shooting or (now - self.last_shoot_time > 500):  # 500ms cooldown
                self.is_shooting = True
                self.shoot_start_time = now
                self.state = "shoot"
                self.current_animation = "shoot"
                self.original_change_x = self.change_x  # Save original movement
                self.change_x = 0  # Stop movement during shoot animation
            self.last_shoot_time = now  # Update last shoot time
        velocity_x = config.PROJECTILE_SPEED if self.facing_right else (-1) * config.PROJECTILE_SPEED
        # Adjust projectile starting position to account for smaller fighter size
        offset_x = (self.rect.width // 2) if self.facing_right else (-self.rect.width // 2)
        return Projectile(self.rect.centerx + offset_x, 
                         self.rect.centery, 
                         velocity=(velocity_x *self.supershot_amount , 0),  # Only horizontal movement
                         damage=self.damage,
                         image_path="src/assets/images/inused_single_images/bullet.png", 
                         owner=self)