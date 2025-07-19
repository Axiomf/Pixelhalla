import pygame
import config
from .base import GameObject
import math  # added for distance calculations

# Base class for objects that require movement or are affected by physics (e.g., gravity).
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
        self.animation_speeds = {"idle": 100, "death": 200, "walk": 75, "hurt": 200}  # ms per frame
        self.last_update = pygame.time.get_ticks()
        self.is_dying = False  # New flag to track death animation
        self.is_hurt = False  # New flag to track hurt animation
        self.hurt_start_time = 0  # Time when hurt animation started
        self.hurt_duration = 500  # Duration of hurt animation in ms (0.5 seconds)

    def update_animation(self):
        now = pygame.time.get_ticks()
        speed = self.animation_speeds.get(self.current_animation, 100)
        if self.animations.get(self.current_animation) and now - self.last_update > speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_animation])
            self.image = self.animations[self.current_animation][self.current_frame]
            if hasattr(self, "facing_right"):
                self.image = pygame.transform.flip(self.image, not self.facing_right, False)
            # If death animation is complete, kill the sprite
            if self.is_dying and self.current_frame == 0 and len(self.animations[self.current_animation]) > 1:
                self.kill()
            # Reset hurt state after duration
            if self.is_hurt and now - self.hurt_start_time >= self.hurt_duration:
                self.is_hurt = False
                if self.change_x != 0:
                    self.state = "walk"
                else:
                    self.state = "idle"
                self.current_animation = self.state

    def update_state(self):
        if not hasattr(self, 'is_dying') or not self.is_dying or not self.is_hurt:  # Only update state if not dying
            if self.change_y >= 5:
                self.state = "falling"
            elif self.change_x != 0:
                self.state = "walk"
            else:
                self.state = "idle"
            # Sync current_animation with state
            if self.state in self.animations:
                self.current_animation = self.state

    def update(self):
        self.calc_grav()  # Adjust vertical velocity due to gravity
        self.rect.x += self.change_x  # Update horizontal position
        self.rect.y += self.change_y  # Update vertical position
        self.update_state()
        self.update_animation()
        
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
            if self.change_y > 0:
                self.rect.bottom = platform.rect.top
                self.change_y = 0

class PowerUp(DynamicObject):
    """A projectile that moves with a fixed velocity.
       Optionally, it can be affected by gravity (e.g., for arrows)."""
    def __init__(self, x, y, type, amount, width=10, height=10, color=(255,255,0), image_path=None, animations=None):
        super().__init__(x, y, width, height, color, image_path, animations)
        self.upgrade_type = type
        self.amount = amount
        self.duration = 10
        self.use_gravity = False
        
    def update(self):
        # Optionally apply gravity.
        if self.use_gravity:
            self.calc_grav()
            self.rect.y += self.change_y


class Player(DynamicObject):
    def __init__(self, x, y, width=30, height=30, color=None, health=100, damage=100, image_path=None, animations=None):
        # Pass animations into DynamicObject for centralized animation management
        super().__init__(x, y, width, height, color, image_path, animations)
        self.health = health          # Current health of the player
        self.max_health = health      # Maximum health for the player
        self.damage = damage          # Damage that this player can inflict
        self.facing_right = True
        self.shield = False

    def take_damage(self, amount):
        if self.shield:
            return
        """Subtracts the given amount from player's health."""
        self.health -= amount
        if self.health < 0:
            self.health = 0  # Ensure health doesn't go negative
        if self.health > 0 and not self.is_dying:  # If not dead, trigger hurt state
            self.is_hurt = True
            self.hurt_start_time = pygame.time.get_ticks()
            self.state = "hurt"
            self.current_animation = "hurt"

    def is_dead(self):
        """Returns True if the player's health has dropped to 0."""
        return self.health <= 0

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

    def update(self):
        # Call DynamicObject's update to apply gravity and movement.
        super().update()
        # Additional player-specific logic (collision, etc.).
        if self.is_dead() and not self.is_dying:
            self.state = "death"
            self.current_animation = "death"  # Sync current_animation with state
            self.is_dying = True
            self.change_x = 0  # Stop movement
            self.change_y = 0
            if not self.animations.get("death"):
                self.kill()

    def shoot(self):
        """Creates a projectile moving in the direction the player is facing."""
        velocity_x = config.PROJECTILE_SPEED if self.facing_right else (-1)*config.PROJECTILE_SPEED
        # Adjust projectile starting position to account for smaller fighter size
        offset_x = (self.rect.width // 2) if self.facing_right else (-self.rect.width // 2)
        return Projectile(self.rect.centerx + offset_x, 
                         self.rect.centery, 
                         velocity=(velocity_x, 0),  # Only horizontal movement
                         damage=self.damage,
                         image_path="src/assets/images/inused_single_images/bullet.png", 
                         owner=self)
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
class NPC(Player):
    """A simple enemy that moves horizontally and bounces at the screen edges."""
    def __init__(self, x, y, width=32, height=48, color=None, speed=2, health=config.NPC_HEALTH, 
                damage=config.NPC_DAMAGE, image_path=None, platforms=None, 
                projectiles=None, all_sprites=None, fighter=None, animations=None):
        super().__init__(x, y, width, height, color, health, damage, image_path, animations)
        self.change_x = speed  # Set initial horizontal patrol speed
        self.facing_right = True  # Track the direction the NPC is facing (True for right, False for left)
        self.platforms = platforms  # Store platforms group
        self.projectiles = projectiles  # Store projectiles group
        self.all_sprites = all_sprites  # Store all_sprites group
        self.single_fighter = fighter
        self.can_see_the_fighter = False
        self.show_vision_line = True  # New flag to toggle vision line visibility
        
        # Store the original image to avoid quality loss when flipping repeatedly
        self.original_image = self.image if image_path else pygame.Surface([width, height]) if color else None
        if self.original_image and not image_path:
            self.original_image.fill(color)

    def update_vision(self):
        # Calculate vision: check if the imaginary line between NPC and fighter collides with any platform.
        if not self.single_fighter or not self.platforms:
            self.can_see_the_fighter = False
            return
        npc_center = self.rect.center
        fighter_center = self.single_fighter.rect.center
        collision = False
        for platform in self.platforms:
            if platform.rect.clipline(npc_center, fighter_center):
                collision = True
                break
        self.can_see_the_fighter = not collision

    def draw_vision_line(self, surface):
        # Draw the vision line only if show_vision_line is True.
        if not self.single_fighter or not self.show_vision_line:
            return
        npc_center = self.rect.center
        fighter_center = self.single_fighter.rect.center
        color = (0, 255, 0) if self.can_see_the_fighter else (255, 0, 0)
        pygame.draw.line(surface, color, npc_center, fighter_center, 2)
        
    def update(self):
        # Update vision before doing other movements.
        self.update_vision()
        # Track previous direction to detect changes
        previous_facing = self.facing_right

        # Apply gravity and update vertical position
        self.calc_grav()
        self.rect.y += self.change_y
        # Check if the NPC is on a platform
        if self.platforms and self.change_y == 1:  # NPC is on a platform (not falling)
            collided_platforms = pygame.sprite.spritecollide(self, self.platforms, False)
            if collided_platforms:  # If on a platform
                for platform in collided_platforms:
                    if self.rect.bottom == platform.rect.top + 1:
                        if self.rect.right >= platform.rect.right and self.change_x > 0:  # At right edge, moving right
                            self.change_x *= -1  # Reverse direction
                        elif self.rect.left <= platform.rect.left and self.change_x < 0:  # At left edge, moving left
                            self.change_x *= -1  # Reverse direction
                    else:
                        if self.rect.right >= platform.rect.left and self.change_x > 0:  # At right edge, moving right
                            self.change_x *= -1  # Reverse direction
                        elif self.rect.left <= platform.rect.right and self.change_x < 0:  # At left edge, moving left
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
        if self.facing_right != previous_facing and not self.animations.get(self.current_animation):  # Only flip if no animation
            if self.original_image:  # Only flip if original_image exists
                self.image = pygame.transform.flip(self.original_image, not self.facing_right, False)

        # Update horizontal position
        self.rect.x += self.change_x

        # Optional: Add projectile shooting for NPC (uncomment if needed)
        # if self.projectiles and self.all_sprites:
        #     projectile = self.shoot()
        #     self.projectiles.add(projectile)
        #     self.all_sprites.add(projectile)
        super().update()
class Projectile(DynamicObject):
    """A projectile that moves with a fixed velocity.
       Optionally, it can be affected by gravity (e.g., for arrows)."""
    def __init__(self, x, y, width=10, height=10, color=(255,255,0), velocity=(10, 0), damage=config.PROJECTILE_DAMAGE, 
                 use_gravity=False, image_path=None, owner=None, animations=None):
        super().__init__(x, y, width, height, color, image_path, animations)
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


# Derived NPC variants
class Melee(NPC):
    """Melee NPC uses close combat attacks."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attack_range = 40  # custom melee range
        self.attack_power = self.damage  # melee uses base damage

    def update(self):
        # Added melee attack logic: if fighter is within range, attack
        if self.single_fighter:
            dist = math.hypot(self.rect.centerx - self.single_fighter.rect.centerx,
                              self.rect.centery - self.single_fighter.rect.centery)
            if dist <= self.attack_range:
                self.single_fighter.take_damage(self.attack_power)
        # ...existing code...
        super().update()
class Ranged(NPC):
    """Ranged NPC uses projectile attacks."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attack_range = 1200  # ranged attack distance
        self.reload_time = 500  # milliseconds between shots
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        #
        #print(self.can_see_the_fighter)
        #print(self.single_fighter)
        #
        #projectile = self.shoot()
        #self.projectiles.add(projectile)
        #self.all_sprites.add(projectile)
        #
        now = pygame.time.get_ticks()
        if self.single_fighter:
            dist = math.hypot(self.rect.centerx - self.single_fighter.rect.centerx,
                              self.rect.centery - self.single_fighter.rect.centery)
            if now - self.last_shot >= self.reload_time and self.can_see_the_fighter and dist <= self.attack_range:
                projectile = self.shoot()
                self.projectiles.add(projectile)
                self.all_sprites.add(projectile)
                self.last_shot = now

        super().update()

