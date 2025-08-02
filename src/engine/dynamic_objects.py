import pygame
import config
import random
from .base import GameObject
from .animation_loader import *
import math  # Added for distance calculations

pygame.mixer.init()  # Initialize mixer for audio

# "animations" is a dictionary with keys of states and values of corresponding frames in order
class DynamicObject(GameObject):
    """Base class for objects that can move or be affected by forces."""
    def __init__(self, x, y, width, height, color=None, image_path=None, animations=None,image=None):
        super().__init__(x, y, width, height, color, image_path, image)
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
        self.freeze_duration = 1000 # lenght of freeze duration
        self.freezed_time = 0 # the time it got freezed
        self.blood_sound = pygame.mixer.Sound("src/assets/sounds/blood2.wav")

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
        now = pygame.time.get_ticks()
        if self.freeze and now - self.freezed_time > self.freeze_duration:
            self.freeze = False
            self.freezed_time = 0 
        self.calc_grav()  # Adjust vertical velocity due to gravity
        if self.freeze:
            self.change_x = self.change_x
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

class Player(DynamicObject):
    def __init__(self, x, y, width=30, height=30, color=None, health=100, damage=100, image_path=None, animations=None):
        # Pass animations into DynamicObject for centralized animation management
        super().__init__(x, y, width, height, color, image_path, animations)
        self.health = health          # Current health of the player
        self.max_health = health      # Maximum health for the player
        self.damage = damage          # Damage that this player can inflict
        self.facing_right = True
        self.jump_strength = config.PLAYER_JUMP  # Vertical speed for jumping (negative to move up)
####################################################
        self.powered = False
        self.left_duration_powerup = 0
        self.started_powerup = 0
        self.powered_up_type = ""
        self.powered_up_amount = 0
        self.supershot = False
        self.supershot_amount = 1
        self.shield = False
        self.base_jump = self.jump_strength
        self.base_damage = self.damage
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

    def shoot(self,arrow = "arcane"):
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
        if arrow == "default":          
            return Projectile(self.rect.centerx + offset_x, 
                             self.rect.centery, 
                             velocity=(velocity_x, 0),  # Only horizontal movement
                             damage=self.damage,
                             image_path="src/assets/images/inused_single_images/bullet.png", 
                             owner=self)
        elif arrow =="arcane":
            return Projectile(self.rect.centerx + offset_x, 
                             self.rect.centery, 
                             velocity=(velocity_x, 0),  # Only horizontal movement
                             damage=self.damage,
                             image_path="src/assets/images/inused_single_images/projectile_Arcane.png", 
                             owner=self)
        elif arrow =="elf":
            return Projectile(self.rect.centerx + offset_x, 
                             self.rect.centery, 
                             velocity=(velocity_x, 0),  # Only horizontal movement
                             damage=self.damage,
                             image_path="src/assets/images/inused_single_images/projectile_Elf.png", 
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
        ##############################################333
        if self.freeze and not self.is_dying:
            self.last_update = now
            #print("sssssssss")
            #self._cycle_frame()
            #self._handle_death_animation()
            return
        ######################################################3
        if self.freeze and self.is_dying:
            self.last_update = now
            #print("rrrrrrrrrrr")
            self._cycle_frame()
            self._handle_death_animation()
            return
        ######################################################3



        elif self.animations.get(self.current_animation) and now - self.last_update > frame_duration:
            self.last_update = now
            self._cycle_frame()
            self._handle_death_animation()
        # Hurt and shoot state handling is checked each update regardless of frame timing
        self._handle_hurt_animation(now)
        self._handle_shoot_animation(now)
        self._handle_attack_animation(now)

    def check_power_up(self):
        now = pygame.time.get_ticks()
        if now - self.started_powerup >= self.left_duration_powerup:
            self.remove_all_powers()
    def remove_all_powers(self):

        self.powered = False
        self.left_duration_powerup = 0
        self.started_powerup = 0
        self.powered_up_type = ""
        self.powered_up_amount = 0

        self.damage = self.base_damage
        self.jump_strength = self.base_jump
        self.shield = False
        self.supershot = False
        self.supershot_amount = 1
    def upgrade(self, type, amount):
        self.remove_all_powers()

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



    def update(self):
        self.check_power_up()

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

class Fighter(Player):
    def __init__(self, x, y, width=70, height=70, color=None, controls=None, health=config.PLAYER_HEALTH, 
                 damage=config.PLAYER_DAMAGE, image_path=None, platforms=None, enemies=None, fighters=None, animations=None):
        super().__init__(x, y, width, height, color, health, damage, image_path, animations)
        self.controls = controls or {}  # Store control keys for this fighter
        self.speed = config.PLAYER_SPEED  # Horizontal speed
        self.platforms = platforms  # Store platforms group
        self.enemies = enemies
        self.fighters = fighters
        self.server_update = False
        self.client_input  = []

        

        # Store the original image to avoid quality loss when flipping repeatedly
        self.original_image = self.image if image_path else pygame.Surface([width, height]) if color else None
        if self.original_image and not image_path:
            self.original_image.fill(color)

    
    
    def update(self):

        if self.freeze:
            self.change_x *= 28/30  # Stop horizontal movement if no keys are pressed     
        else:
            if self.client_input:
                previous_facing = self.facing_right
                if self.controls.get("left") and self.controls["left"] in self.client_input:
                    self.change_x = (-1) * self.speed
                    self.facing_right = False
                elif self.controls.get("right") and self.controls["right"] in self.client_input:
                    self.change_x = self.speed
                    self.facing_right = True
                else:
                    self.change_x = 0
                if self.controls.get("jump") and self.controls["jump"] in self.client_input:
                    if self.change_y == 0:
                        self.change_y = self.jump_strength
                # Update the image based on direction
                if self.facing_right != previous_facing and not self.animations.get(self.current_animation):  # Only flip if no animation
                    if self.original_image:  # Only flip if original_image exists
                        self.image = pygame.transform.flip(self.original_image, not self.facing_right, False)
                self.client_input = []  # Clear the input list after processing
            else:
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
                # Update the image based on direction
                if self.facing_right != previous_facing and not self.animations.get(self.current_animation):  # Only flip if no animation
                    if self.original_image:  # Only flip if original_image exists
                        self.image = pygame.transform.flip(self.original_image, not self.facing_right, False)





        #@@@@@@@ Check for horizontal collisions with platforms
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
        #@@@@@@@ Check for scene boundaries
        if self.rect.right + self.change_x > config.SCENE_WIDTH:
            self.rect.right = config.SCENE_WIDTH
            self.change_x = 0
        elif self.rect.left + self.change_x < 0:
            self.rect.left = 0
            self.change_x = 0

        # Call the parent's update to apply gravity and update movement
        super().update()

    def shoot(self,arrow = "arcane"):
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
        
        if arrow == "default":          
            return Projectile(self.rect.centerx + offset_x, 
                             self.rect.centery, 
                             velocity=(velocity_x*self.supershot_amount, 0),  # Only horizontal movement
                             damage=self.damage,
                             image_path="src/assets/images/inused_single_images/bullet.png", 
                             owner=self)
        elif arrow =="arcane":
            path = "src/assets/images/inused_single_images/projectile_Arcane.png"

            frame = pygame.image.load(path).convert_alpha()
            frame = pygame.transform.flip(frame, not self.facing_right, False)
            return Projectile(self.rect.centerx + offset_x, 
                             self.rect.centery,width=40,height=5,
                             velocity=(velocity_x*self.supershot_amount, 0),  # Only horizontal movement
                             damage=self.damage,
                             image_path="src/assets/images/inused_single_images/projectile_Arcane.png", 
                             owner=self,image=frame)
                             
        elif arrow =="elf":

            path = "src/assets/images/inused_single_images/projectile_Elf.png"

            sheet = pygame.image.load(path).convert_alpha()
            crop_rect = pygame.Rect(109, 56, 36, 14)
            frame = sheet.subsurface(crop_rect)
            frame = pygame.transform.flip(frame, not self.facing_right, False)
            return Projectile(self.rect.centerx + offset_x, 
                             self.rect.centery, width=36,height=14,
                             velocity=(velocity_x*self.supershot_amount, 0),  # Only horizontal movement
                             damage=self.damage,image_path=path,
                             image=frame, 
                             owner=self)

class MeleeFighter(Fighter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attack_range = 50  # Melee attack range in pixels
        self.attack_cooldown = 500  # 1 second cooldown for attack
        self.last_attack_time = 0  # Track last attack time
        self.last_sound_time = 0  # Track last sound time

    def update(self):
        self.check_power_up()
        keys = pygame.key.get_pressed()
        previous_facing = self.facing_right

        # Movement like Fighter
        if self.controls.get("left") and keys[self.controls["left"]]:
            self.change_x = (-1) * self.speed
            self.facing_right = False
        elif self.controls.get("right") and keys[self.controls["right"]]:
            self.change_x = self.speed
            self.facing_right = True
        else:
            self.change_x = 0

        if self.controls.get("jump") and keys[self.controls["jump"]] and self.change_y == 0:
            self.change_y = self.jump_strength

        # Platform and boundary collisions like Fighter
        if self.platforms:
            self.rect.x += self.change_x
            collided_platforms = pygame.sprite.spritecollide(self, self.platforms, False)
            for platform in collided_platforms:
                if self.change_x > 0 and self.rect.right > platform.rect.left:
                    self.rect.right = platform.rect.left
                    self.change_x = 0
                elif self.change_x < 0 and self.rect.left < platform.rect.right:
                    self.rect.left = platform.rect.right
                    self.change_x = 0
            self.rect.y += self.change_y
            collided_platforms = pygame.sprite.spritecollide(self, self.platforms, False)
            for platform in collided_platforms:
                if self.change_y > 0 and self.rect.bottom > platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.change_y = 0
                elif self.change_y < 0 and self.rect.top < platform.rect.bottom:
                    self.rect.top = platform.rect.bottom
                    self.change_y = 0

        if self.rect.right > config.SCENE_WIDTH:
            self.rect.right = config.SCENE_WIDTH
            self.change_x = 0
        elif self.rect.left < 0:
            self.rect.left = 0
            self.change_x = 0

        # Melee attack with space key
        if self.controls.get("attack") and keys[self.controls["attack"]]:
            now = pygame.time.get_ticks()
            if not self.is_attacking and now - self.last_attack_time >= self.attack_cooldown:
                self.is_attacking = True
                self.attack_start_time = now
                self.state = "attack"
                self.current_animation = "attack"
                self.original_change_x = self.change_x
                self.change_x = 0
                self.last_attack_time = now

                # Check for targets in attack range
                attack_x = self.rect.centerx + (self.attack_range * (1 if self.facing_right else -1))
                attack_y = self.rect.centery
                for sprite in self.enemies:  # Assuming all_sprites contains fighters and NPCs
                    if hasattr(sprite, 'health') and sprite != self:
                        dist = math.hypot(sprite.rect.centerx - attack_x, sprite.rect.centery - attack_y)
                        if dist <= self.attack_range:
                            sprite.take_damage(self.damage)
                            if now - self.last_sound_time >= 3000:  # 3-second sound cooldown
                                sprite.blood_sound.play()
                                self.last_sound_time = now
                for sprite in self.fighters:  # Assuming all_sprites contains fighters and NPCs
                    if hasattr(sprite, 'health') and sprite != self:
                        dist = math.hypot(sprite.rect.centerx - attack_x, sprite.rect.centery - attack_y)
                        if dist <= self.attack_range:
                            sprite.take_damage(self.damage)
                            if now - self.last_sound_time >= 3000:  # 3-second sound cooldown
                                sprite.blood_sound.play()
                                self.last_sound_time = now

        # Update image based on direction
        if self.facing_right != previous_facing and not self.animations.get(self.current_animation):
            if self.original_image:
                self.image = pygame.transform.flip(self.original_image, not self.facing_right, False)

        self.calc_grav()
        super().update()
 
class NPC(Player):
    vision_boost = 0  # <-- New class variable for global vision boost 
    """A simple enemy that moves horizontally and bounces at the screen edges."""
    def __init__(self, x, y, width=32, height=48, color=None, speed=2, health=config.NPC_HEALTH, 
                damage=config.NPC_DAMAGE, image_path=None, platforms=None, 
                projectiles=None, all_sprites=None, fighter=None, enemies=None, fighters=None, animations=None,roam=True):
        super().__init__(x, y, width, height, color, health, damage, image_path,  animations)
        self.change_x = speed  # Set initial horizontal patrol speed
        self.speed = speed
        self.facing_right = True  # Track the direction the NPC is facing (True for right, False for left)
        self.platforms = platforms  # Store platforms group
        self.projectiles = projectiles  # Store projectiles group
        self.all_sprites = all_sprites  # Store all_sprites group
        self.enemies = enemies
        self.fighters = fighters,
        self.single_fighter = fighter
        self.can_see_the_fighter = False
        self.show_vision_line = True  # New flag to toggle vision line visibility
        self.enemy_classes = [Medusa, Melee, Ranged, Suicide_Bomb, Eye]
        self.roam = roam # if it is a standing or patroling npc
        

        
        # Store the original image to avoid quality loss when flipping repeatedly
        self.original_image = self.image if image_path else pygame.Surface([width, height]) if color else None
        if self.original_image and not image_path:
            self.original_image.fill(color)

    def update_vision(self):
        # Calculate vision: check if the imaginary line between NPC and fighter collides with any platform
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
        if NPC.vision_boost > 0:
            self.can_see_the_fighter = True

    def draw_vision_line(self, surface):
        # Draw the vision line only if show_vision_line is True
        if not self.single_fighter or not self.show_vision_line:
            return
        npc_center = self.rect.center
        fighter_center = self.single_fighter.rect.center
        color = (0, 255, 0) if self.can_see_the_fighter else (255, 0, 0)
        pygame.draw.line(surface, color, npc_center, fighter_center, 2)

    def update(self):
        # Update vision before doing other movements
        self.update_vision()
        # Initially, if the fighter is visible, face towards the fighter.
        if self.single_fighter and self.can_see_the_fighter:
            self.facing_right = self.single_fighter.rect.centerx > self.rect.centerx
        previous_facing = self.facing_right

        # Apply gravity and update vertical position
        self.calc_grav()
        self.rect.y += self.change_y
        if self.roam:
            # Check if the NPC is on a platform
            if self.platforms and self.change_y <= 1:  # NPC is on a platform (not falling)
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
                else:# If not on a platform, check scene boundaries
                    if self.rect.right > config.SCENE_WIDTH or self.rect.left < 0:
                        self.change_x *= -1
            else:# If falling, check scene boundaries
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
        else:
            self.change_x = 0
            # NPC remains stationary
        
        # Enforce fighter-facing if visible; otherwise, base on movement
        if not (self.single_fighter and self.can_see_the_fighter):
            self.facing_right = self.change_x > 0

        # Update image flipping if facing changed
        if self.facing_right != previous_facing and not self.animations.get(self.current_animation):  # Only flip if no animation
            if self.original_image:  # Only flip if original_image exists
                self.image = pygame.transform.flip(self.original_image, not self.facing_right, False)

        super().update()

class Boss(NPC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spawn_cooldown = 10000  # 5 seconds cooldown for spawning enemies
        self.phase = 0
        self.last_spawn_time = 0
        self.phase_effect_start = 0  
        self.phase_effect_duration = 5000  
        self.phase_effect_active = False  
        self.blackout_start = 0  
        self.blackout_duration = 10 
        self.phase_changed = False
        self.fade_radius = 100

    def update(self):
        now = pygame.time.get_ticks()

        
        if self.phase_changed and not self.phase_effect_active:
            self.phase_effect_start = now
            self.phase_effect_active = True
            self.phase_changed = False  

        if self.phase_effect_active:
            if now - self.phase_effect_start >= self.phase_effect_duration:
                self.blackout_start = now
                self.phase_effect_active = False
        
        if self.blackout_start > 0 and now - self.blackout_start >= self.blackout_duration:
            self.blackout_start = 0  
        
        self.change_x = 0

        # Spawn enemies periodically
        if now - self.last_spawn_time >= self.spawn_cooldown:
            self.spawn_enemy()
            self.last_spawn_time = now

        super().update()

    def spawn_enemy(self):
        if self.phase == 0:
            new_enemy1 = Melee(500, 50, 30, 35, platforms=self.platforms, fighter=self.single_fighter,
                              animations=load_animations_Goblin(150, 150, crop_x=60, crop_y=65, crop_width=30, crop_height=35))
            new_enemy2 = Medusa(550, 50, 128, 128,
                               speed=config.NPC_SPEED, platforms=self.platforms, projectiles=self.projectiles, all_sprites=self.all_sprites, fighter=self.single_fighter,
                               animations=load_animations_Medusa(), roam=False)
            new_enemy3 = Melee(650, 50, 30, 35, platforms=self.platforms, fighter=self.single_fighter,
                              animations=load_animations_Goblin(150, 150, crop_x=60, crop_y=65, crop_width=30, crop_height=35))
            self.all_sprites.add(new_enemy1, new_enemy2, new_enemy3)
            self.enemies.add(new_enemy1, new_enemy2, new_enemy3)
            self.phase = 1
            self.phase_changed = True 
            self.fade_radius = 100
        elif self.phase == 1 and len(self.enemies) == 1:
            new_enemy1 = Ranged(500, 50, 32, 32,
                               speed=config.NPC_SPEED, platforms=self.platforms, projectiles=self.projectiles,
                               all_sprites=self.all_sprites, fighter=self.single_fighter,
                               animations=load_animations_Arcane_Archer(64, 64), roam=False)
            new_enemy2 = Ranged(550, 50, 32, 32,
                               speed=config.NPC_SPEED, platforms=self.platforms, projectiles=self.projectiles,
                               all_sprites=self.all_sprites, fighter=self.single_fighter,
                               animations=load_animations_Arcane_Archer(64, 64), roam=False)
            new_enemy3 = Ranged(650, 50, 32, 32,
                               speed=config.NPC_SPEED, platforms=self.platforms, projectiles=self.projectiles,
                               all_sprites=self.all_sprites, fighter=self.single_fighter,
                               animations=load_animations_Arcane_Archer(64, 64), roam=False)
            new_enemy4 = Suicide_Bomb(750, 50,
                                     speed=2, health=50,
                                     damage=20, platforms=self.platforms, projectiles=self.projectiles,
                                     all_sprites=self.all_sprites, fighter=self.single_fighter, animations=load_animations_Suicide_Bomber(), roam=True)
            self.all_sprites.add(new_enemy1, new_enemy2, new_enemy3, new_enemy4)
            self.enemies.add(new_enemy1, new_enemy2, new_enemy3, new_enemy4)
            self.phase = 2
            self.phase_changed = True
            self.fade_radius = 100
        elif self.phase == 2 and len(self.enemies) == 1:
            new_enemy1 = Medusa(500, 50, 128, 128,
                               speed=config.NPC_SPEED, platforms=self.platforms, projectiles=self.projectiles, all_sprites=self.all_sprites, fighter=self.single_fighter,
                               animations=load_animations_Medusa(), roam=False)
            new_enemy2 = Ranged(550, 50, 32, 32,
                               speed=config.NPC_SPEED, platforms=self.platforms, projectiles=self.projectiles,
                               all_sprites=self.all_sprites, fighter=self.single_fighter,
                               animations=load_animations_Arcane_Archer(64, 64), roam=False)
            new_enemy3 = Ranged(650, 50, 32, 32,
                               speed=config.NPC_SPEED, platforms=self.platforms, projectiles=self.projectiles,
                               all_sprites=self.all_sprites, fighter=self.single_fighter,
                               animations=load_animations_Arcane_Archer(64, 64), roam=False)
            new_enemy4 = Eye(750, 50,
                            width=20, height=30, speed=0, animations=load_animations_Eye(32, 32), platforms=self.platforms)
            self.all_sprites.add(new_enemy1, new_enemy2, new_enemy3, new_enemy4)
            self.enemies.add(new_enemy1, new_enemy2, new_enemy3, new_enemy4)
            self.phase = 3
            self.phase_changed = True
            self.fade_radius = 100
        elif self.phase == 3 and len(self.enemies) == 1:
            new_enemy1 = Melee(500, 50, 30, 35, platforms=self.platforms, fighter=self.single_fighter,
                              animations=load_animations_Goblin(150, 150, crop_x=60, crop_y=65, crop_width=30, crop_height=35))
            new_enemy2 = Melee(550, 50, 30, 35, platforms=self.platforms, fighter=self.single_fighter,
                              animations=load_animations_Goblin(150, 150, crop_x=60, crop_y=65, crop_width=30, crop_height=35))
            new_enemy3 = Suicide_Bomb(650, 50,
                                     speed=2, health=50,
                                     damage=20, platforms=self.platforms, projectiles=self.projectiles,
                                     all_sprites=self.all_sprites, fighter=self.single_fighter, animations=load_animations_Suicide_Bomber(), roam=True)
            self.all_sprites.add(new_enemy1, new_enemy2, new_enemy3)
            self.enemies.add(new_enemy1, new_enemy2, new_enemy3)
            self.phase = 4
            self.phase_changed = True
            self.fade_radius = 100
        elif self.phase == 4 and len(self.enemies) == 1:
            self.phase = 5
            self.phase_changed = True
        elif self.phase == 5:
            # Random position near boss (within 100-300 pixels)
            offset_x = random.randint(373, 709)
            offset_y = random.randint(0, 50)
            spawn_x = offset_x
            spawn_y = offset_y

            # Create a new Melee enemy (can be extended to other types)
            enemy_class = random.choice(self.enemy_classes)
            if enemy_class == Melee:
                new_enemy = Melee(spawn_x, spawn_y, 30, 35, platforms=self.platforms, fighter=self.single_fighter,
                                 animations=load_animations_Goblin(150, 150, crop_x=60, crop_y=65, crop_width=30, crop_height=35))
            elif enemy_class == Medusa:
                new_enemy = Medusa(spawn_x, spawn_y, 128, 128,
                                  speed=config.NPC_SPEED, platforms=self.platforms, projectiles=self.projectiles, all_sprites=self.all_sprites, fighter=self.single_fighter,
                                  animations=load_animations_Medusa(), roam=False)
            elif enemy_class == Ranged:
                new_enemy = Ranged(spawn_x, spawn_y, 32, 32,
                                  speed=config.NPC_SPEED, platforms=self.platforms, projectiles=self.projectiles,
                                  all_sprites=self.all_sprites, fighter=self.single_fighter,
                                  animations=load_animations_Arcane_Archer(64, 64), roam=False)
            elif enemy_class == Eye:
                new_enemy = Eye(spawn_x, spawn_y,
                               width=20, height=20, speed=0, animations=load_animations_Eye(32, 32), platforms=self.platforms)
            elif enemy_class == Suicide_Bomb:
                new_enemy = Suicide_Bomb(spawn_x, spawn_y,
                                       speed=2, health=50,
                                       damage=20, platforms=self.platforms, projectiles=self.projectiles,
                                       all_sprites=self.all_sprites, fighter=self.single_fighter, animations=load_animations_Suicide_Bomber(), roam=True)
            self.all_sprites.add(new_enemy)
            self.enemies.add(new_enemy)

class Suicide_Bomb(NPC):
    """A NPC that patrols until it sees the fighter, then chases and explodes when close enough."""
    def __init__(self, x, y, width=40, height=32, color=None, speed=0.3, health=50, 
                 damage=20, image_path=None, platforms=None, projectiles=None, 
                 all_sprites=None, fighter=None, fighters=None, animations=None, roam=True):
        super().__init__(x, y, width, height, color, speed, health, damage, image_path, 
                         platforms=platforms, projectiles=projectiles, all_sprites=all_sprites, 
                         fighter=fighter, fighters=fighters, animations=animations, roam=roam)
        self.explosion_range = 50  # Distance threshold to trigger explosion
        self.explosion_damage = damage  # Damage dealt to the fighter upon explosion
        self.exploded = False
    def update(self):
        # Update vision first
        self.update_vision()
        if self.exploded:
            super().update()
            return
        
        if self.single_fighter and self.can_see_the_fighter:
            dist = math.hypot(self.rect.centerx - self.single_fighter.rect.centerx,
                              self.rect.centery - self.single_fighter.rect.centery)
            if dist <= self.explosion_range and not self.exploded:
                # Explode: trigger death animation and damage the fighter
                self.single_fighter.take_damage(self.explosion_damage)
                
                print("fighter is taking damage")
                self.state = "death"
                self.current_animation = "death"
                self.is_dying = True
                self.change_x = 0
                self.change_y = 0
                self.exploded = True
                # Let update_animation handle death animation and eventual kill
                super().update()
                return
            else:
                # Chase the fighter by moving towards its x position
                self.facing_right = self.single_fighter.rect.centerx> self.rect.centerx
                self.change_x = self.speed if self.facing_right else -self.speed
                if abs(self.rect.centerx - self.single_fighter.rect.centerx) <= self.explosion_range/2:
                    self.change_x = 0

                # Prevent moving off the platform edges
                if self.platforms:
                    collided_platforms = pygame.sprite.spritecollide(self, self.platforms, False)
                    for platform in collided_platforms:
                        if self.facing_right and self.rect.right >= platform.rect.right:
                            self.change_x = 0
                        elif not self.facing_right and self.rect.left <= platform.rect.left:
                            self.change_x = 0
        # If fighter is not seen, maintain patrol behavior (using NPC's existing logic)
        # ...existing patrol logic...
        super().update()

class Eye(NPC):
    """
    A support enemy that increases the vision distance of all NPCs (enemies)
    as long as it is alive.
    """
    def __init__(self, x, y, width=20, height=20, color=(255,0,255), speed=0, animations=None, platforms=None, projectiles=None, 
                 all_sprites=None, fighter=None, fighters=None):
        super().__init__(x, y, width, height, color, speed, health=100, damage=0, platforms=platforms,
                         projectiles=projectiles, 
                 all_sprites=all_sprites, fighter=fighter, fighters=fighters, animations=animations,roam=False)
        self.vision_increase = 500  # Boost value to add to all NPCs' vision distance
        self.facing_right = True  # Can be set as needed
        self.exploded = False
    def update(self):
        # While alive, set the global vision boost.
        NPC.vision_boost = self.vision_increase
        # Eye may have its own behavior; here we keep it stationary.
        # ...existing update logic if needed...
        super().update()

    def kill(self):
        # When Eye is killed, remove the vision boost.
        NPC.vision_boost = 0
        super().kill()

class Ranged(NPC):
    """Ranged NPC uses projectile attacks."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attack_range = 600  # Ranged attack distance
        self.reload_time = 3000  # Milliseconds between shots
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if self.single_fighter:
            dist = math.hypot(self.rect.centerx - self.single_fighter.rect.centerx,
                              self.rect.centery - self.single_fighter.rect.centery)
            # Use effective range = attack_range + NPC.vision_boost
            if (not self.is_shooting and now - self.last_shot >= self.reload_time and 
                self.can_see_the_fighter and dist <= self.attack_range + NPC.vision_boost):
                self.facing_right = self.single_fighter.rect.centerx> self.rect.centerx
                self.is_shooting = True
                self.shoot_start_time = now
                self.state = "shoot"
                self.current_animation = "shoot"
                self.original_change_x = self.speed  # Save original movement speed
                self.change_x = 0  # Stop movement during shoot animation
                projectile = self.shoot()
                self.projectiles.add(projectile)
                self.all_sprites.add(projectile)
                self.last_shot = now
                self.last_shoot_time = now  # Update last shoot time
            elif not self.is_shooting:  # Resume movement if not shooting
                self.change_x = self.speed if self.facing_right else -self.speed

        super().update()

class Melee(NPC):
    """Melee NPC uses close combat attacks."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attack_range = 40  # Custom melee range
        self.attack_power = self.damage  # Melee uses base damage
        self.attack_cooldown = 3000  # 3 seconds cooldown in milliseconds
        self.last_sound_time = 0
    

    def update(self):
        # Added melee attack logic: if fighter is within range and cooldown has passed, attack
        if self.single_fighter:
            dist = math.hypot(self.rect.centerx - self.single_fighter.rect.centerx,
                              self.rect.centery - self.single_fighter.rect.centery)
            now = pygame.time.get_ticks()
            # Use effective range = attack_range + NPC.vision_boost
            if not self.is_attacking and dist <= self.attack_range  and now - self.last_attack_time >= self.attack_cooldown:
                self.is_attacking = True
                self.attack_start_time = now
                self.state = "attack"
                self.current_animation = "attack"
                self.original_change_x = self.speed  # Save original movement speed
                self.change_x = 0  # Stop movement during shoot animation
                self.attack()
                self.single_fighter.take_damage(self.attack_power)
                self.last_attack_time = now
            elif not self.is_attacking:  # Resume movement if not shooting
                self.change_x = self.speed if self.facing_right else -self.speed
        super().update()

class Medusa(Melee):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set freeze duration in milliseconds (example: 3000ms = 3 seconds)
        self.freeze_duration = 10000
        self.attack_cooldown = 3000 + self.freeze_duration
        self.attack_range = 100
        self.last_attack_time = -self.attack_cooldown

    def update(self):
        # Override update to freeze the fighter instead of dealing repeated damage
        if self.single_fighter:
            now = pygame.time.get_ticks()
            dist = math.hypot(self.rect.centerx - self.single_fighter.rect.centerx,
                              self.rect.centery - self.single_fighter.rect.centery)
            if not self.is_attacking and dist <= self.attack_range and now - self.last_attack_time >= self.attack_cooldown:
                # Freeze fighter: set freeze flag and record freeze time
                self.single_fighter.freeze = True
                self.single_fighter.freezed_time = now
                self.single_fighter.freeze_duration =  self.freeze_duration
                self.single_fighter.take_damage(self.damage)
                self.last_attack_time = now

                self.is_attacking = True
                self.attack_start_time = now
                self.state = "attack"
                self.current_animation = "attack"
                self.original_change_x = self.speed  # Save current movement speed
                self.change_x = 0  # Stop movement during attack animation
            elif not self.is_attacking:
                self.change_x = self.speed if self.facing_right else -self.speed
        # Continue with the default update behavior
        # ...existing code...
        super().update()


class Projectile(DynamicObject):
    """A projectile that moves with a fixed velocity.
       Optionally, it can be affected by gravity (e.g., for arrows)."""
    def __init__(self, x, y, image_path, width=10, height=10, color=(255,255,0), velocity=(10, 0), damage=config.PROJECTILE_DAMAGE, 
                 use_gravity=False, owner=None, animations=None, image=None):
        super().__init__(x, y, width, height, color, image_path, animations,image=image)
        self.damage = damage
        self.velocity_x, self.velocity_y = velocity
        self.use_gravity = use_gravity
        self.owner = owner  # Store the owner of the projectile (the fighter who shot it)
        # For projectiles we typically do not use the standard gravity unless needed
        if not self.use_gravity:
            self.change_y = 0  

    def update(self):
        # Move based on fixed velocity
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        # Optionally apply gravity
        if self.use_gravity:
            self.calc_grav()
            self.rect.y += self.change_y

class PowerUp(DynamicObject):
    """A power-up that moves with a fixed velocity and respawns periodically."""
    def __init__(self, x, y, type, amount, width=10, height=10, color=(255,255,0), image_path=None, animations=None, all_sprites=None, power_ups=None, platforms=None):
        super().__init__(x, y, width, height, color, image_path, animations)
        self.color = color
        self.image_path = image_path
        self.upgrade_type = type
        self.amount = amount
        self.use_gravity = False
        self.lifetime = 10000  # 5 seconds lifetime before disappearing
        self.spawn_interval = 10000  # 10 seconds before respawning
        self.creation_time = pygame.time.get_ticks()
        self.all_sprites = all_sprites  # Store all_sprites group for respawning
        self.power_ups = power_ups  # Store power_ups group for respawning
        self.platforms=platforms

    def update(self):
        now = pygame.time.get_ticks()
        # Check if lifetime has expired
        if now - self.creation_time >= self.lifetime:
            self.respawn()
        # Apply gravity if enabled
        if self.use_gravity:
            self.calc_grav()
            self.rect.y += self.change_y
        super().update()

    def respawn(self):
        """Remove the current power-up and create a new one at a random position."""
        # Remove the current power-up
        self.kill()
        # Create a new power-up at a random position
        selected_platform = random.choice(list(self.platforms))
        new_x = random.randint(selected_platform.rect.x, selected_platform.rect.x + selected_platform.rect.width)
        new_y = 0
        new_power_up = PowerUp(
            x=new_x,
            y=new_y,
            type=self.upgrade_type,
            amount=self.amount,
            width=self.rect.width,
            height=self.rect.height,
            color=self.color,
            image_path=self.image_path,
            animations=self.animations,
            all_sprites=self.all_sprites,
            power_ups=self.power_ups,
            platforms=self.platforms
        )
        # Add the new power-up to the sprite groups
        if self.all_sprites:
            self.all_sprites.add(new_power_up)
        if self.power_ups:
            self.power_ups.add(new_power_up)