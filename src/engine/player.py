import pygame
import config
from .dynamic_objects import DynamicObject
from .projectile import Projectile

class Player(DynamicObject):
    def __init__(self, x, y, width=30, height=30, color=None, health=100, damage=100, image_path=None, animations=None):
        # Pass animations into DynamicObject for centralized animation management
        super().__init__(x, y, width, height, color, image_path, animations)
        self.health = health          # Current health of the player
        self.max_health = health      # Maximum health for the player
        self.damage = damage          # Damage that this player can inflict
        self.facing_right = True
        self.shield = False
        # Added shooting state attributes

        

    def take_damage(self, amount):
        if self.shield:
            return
        """Subtracts the given amount from player's health."""
        self.health -= amount
        if self.health < 0:
            self.health = 0  # Ensure health doesn't go negative
        if self.health > 0 and not self.is_dying:  # If not dead, trigger hurt state
            now = pygame.time.get_ticks()
            # Only start new hurt animation if enough time has passed since last hurt
            if not self.is_hurting or (now - self.last_hurt_time > 500):  # 500ms cooldown
                self.is_hurting = True
                self.hurt_start_time = now
                self.state = "hurt"
                self.current_animation = "hurt"
                self.original_change_x = self.change_x  # Save original movement
                self.change_x = 0  # Stop movement during hurt animation
            self.last_hurt_time = now  # Update last hurt time

    def is_dead(self):
        """Returns True if the player's health has dropped to 0."""
        return self.health <= 0

    def is_hurt(self):
        return self.health > 0 and not self.is_dying

    def is_shoot(self):
        return not self.is_dying and not self.is_hurting
    def is_attack(self):
        return not self.is_dying and not self.is_hurting

    def draw_health_bar(self, surface):
        """Draws a health bar above the player based on current health."""
        # Health bar dimensions
        bar_width = self.rect.width  # Same width as the player sprite
        bar_height = config.PLAYER_BAR_HEIGHT  # Height of the health bar
        bar_x = self.rect.x  # Align with the player's x position
        bar_y = self.rect.y - bar_height - 5  # Position above the player

        # Calculate the width of the health bar based on health percentage
        health_ratio = self.health / self.max_health
        health_width = bar_width * health_ratio
 
        # Draw background (gray) and health (red)
        pygame.draw.rect(surface, config.PLAYER_BAR_BACKGROUND_COLOR, (bar_x, bar_y, bar_width, bar_height))  # Background
        pygame.draw.rect(surface, config.PLAYER_BAR_HEALTH_COLOR, (bar_x, bar_y, health_width, bar_height))  # Health
    
    def _handle_death_animation(self):
        # If death animation is playing and the current frame cycle resets, remove the sprite
        if self.is_dying and self.current_frame == 0 and len(self.animations[self.current_animation]) > 1:
            self.kill()

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
                         velocity=(velocity_x, 0),  # Only horizontal movement
                         damage=self.damage,
                         image_path="src/assets/images/inused_single_images/bullet.png", 
                         owner=self)
    
    
    def attack(self):
        if self.is_attack():
            now = pygame.time.get_ticks()
            if not self.is_attacking or (now - self.last_attack_time > 500):  # 500ms cooldown
                self.is_attacking = True
                self.attack_start_time = now
                self.state = "attack"
                self.current_animation = "attack"
                self.original_change_x = self.change_x  # Save original movement
                self.change_x = 0  # Stop movement during shoot animation
            self.last_attack_time = now  # Update last shoot time

    def update_animation(self):
        # Retrieve the current time for animation timing
        now = pygame.time.get_ticks()
        frame_duration = self.animation_speeds.get(self.current_animation, 100)
        # Cycle frames just as in the parent
        if self.animations.get(self.current_animation) and now - self.last_update > frame_duration:
            self.last_update = now
            self._cycle_frame()
            self._handle_death_animation()
        # Hurt and shoot state handling is checked each update regardless of frame timing
        self._handle_hurt_animation(now)
        self._handle_shoot_animation(now)
        self._handle_attack_animation(now)

    def update(self):
        # Prevent movement if frozen
        
        # Call DynamicObject's update to apply gravity and movement
        super().update()
        # Additional player-specific logic (collision, etc.)
        if self.is_dead() and not self.is_dying:
            self.state = "death"
            self.current_animation = "death"  # Sync current_animation with state
            self.is_dying = True
            self.change_x = 0  # Stop movement
            self.change_y = 0
            if not self.animations.get("death"):
                self.kill()