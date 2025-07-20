import pygame
import config # Assuming config.py exists and contains necessary constants
from .base import GameObject # Assuming base.py contains a GameObject class inheriting from pygame.sprite.Sprite
import math

class DynamicObject(GameObject):
    """Base class for objects that can move or be affected by forces."""
    def __init__(self, x, y, width, height, color=None, image_path=None, animations=None, platforms=None, use_gravity=True):
        super().__init__(x, y, width, height, color, image_path)
        self.change_x = 0  # Horizontal velocity
        self.change_y = 0  # Vertical velocity
        self.state = "idle"

        # Animation attributes
        self.animations = animations if animations is not None else {}
        self.current_animation = "idle" if "idle" in self.animations else (list(self.animations.keys())[0] if self.animations else "idle")
        self.current_frame = 0
        # Animation speeds in ms per frame (defaults to 100ms if not specified)
        self.animation_speeds = {"idle": 75, "death": 200, "walk": 75, "hurt": 200, "shoot": 100, "attack": 100}
        self.last_update = pygame.time.get_ticks()

        # Timed states and their attributes
        self.is_dying = False
        self.is_hurting = False
        self.hurt_start_time = 0
        self.hurt_duration = 1000
        self.is_shooting = False
        self.shoot_start_time = 0
        self.shoot_duration = 500
        self.is_attacking = False
        self.attack_start_time = 0
        self.attack_duration = 500

        self.freeze = False
        self.freeze_duration = 3000 # Default freeze duration in ms (e.g., 3 seconds)
        self.freezed_time = 0

        # Movement related flags and references
        self.original_change_x = 0 # Stores horizontal velocity before a state (like hurt/shoot) overrides it
        self.platforms = platforms # Reference to the platform group for collision detection
        self.on_ground = False     # Flag to track if the object is currently on the ground
        self.facing_right = True   # Default facing direction

        # New attribute to control gravity
        self.use_gravity = use_gravity

    def _cycle_frame(self):
        """Advance to the next frame and update the sprite image. Handles flipping."""
        if not self.animations.get(self.current_animation):
            # No animation frames for the current state, use fallback image or do nothing
            # For debugging: print(f"No animation frames for state: {self.current_animation}")
            return

        self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_animation])
        self.image = self.animations[self.current_animation][self.current_frame]

        # Apply flipping based on facing_right direction
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False) # Flip horizontally

    def _handle_timed_state_end(self, now, state_flag_name, start_time_name, duration_name):
        """Generic method to handle the end of a timed state (e.g., hurt, shoot, attack)."""
        if getattr(self, state_flag_name) and now - getattr(self, start_time_name) >= getattr(self, duration_name):
            setattr(self, state_flag_name, False)
            # Revert to the default movement state after the timed animation ends
            # The change_x will be set by the main update logic (player input/AI)
            # No explicit restoration of change_x here, as update_state will re-evaluate.
            # This relies on the subclass's update method to set change_x based on its current logic.

    def _handle_freeze_state(self, now):
        """Handles unfreezing the object after a duration."""
        if self.freeze and now - self.freezed_time >= self.freeze_duration:
            self.freeze = False
            # No need to restore change_x/y here; the main update loop will re-apply desired movement

    def update_animation(self):
        """Manages animation frame progression and calls timed state handlers."""
        now = pygame.time.get_ticks()
        frame_duration = self.animation_speeds.get(self.current_animation, 100)

        # Advance animation frame if enough time has passed
        if self.animations.get(self.current_animation) and now - self.last_update > frame_duration:
            self.last_update = now
            self._cycle_frame()
            # If a death animation just completed its cycle, kill the sprite
            if self.current_animation == "death" and self.current_frame == 0 and self.is_dying:
                self.kill() # This should happen when the death animation loops back to frame 0 (completes)

        # Handle ending of timed states
        self._handle_timed_state_end(now, "is_hurting", "hurt_start_time", "hurt_duration")
        self._handle_timed_state_end(now, "is_shooting", "shoot_start_time", "shoot_duration")
        self._handle_timed_state_end(now, "is_attacking", "attack_start_time", "attack_duration")
        self._handle_freeze_state(now) # Also manage freeze duration here

    def _update_base_state(self):
        """Determines the basic movement state (idle, walk, falling) without overrides."""
        if self.change_y > 0 and not self.on_ground: # Falling down
            self.state = "falling"
        elif self.change_x != 0:
            self.state = "walk"
        else:
            self.state = "idle"

    def update_state(self):
        """Sets the current animation state based on priority."""
        # State priority: Death > Hurt > Shoot > Attack > (Falling/Walk/Idle)
        if self.is_dying:
            new_state = "death"
        elif self.is_hurting:
            new_state = "hurt"
        elif self.is_shooting:
            new_state = "shoot"
        elif self.is_attacking:
            new_state = "attack"
        else:
            self._update_base_state() # Determine basic movement state
            new_state = self.state # Use the state set by _update_base_state

        # Change current_animation only if different and animations exist for it
        if new_state in self.animations and self.current_animation != new_state:
            self.current_animation = new_state
            self.current_frame = 0 # Reset frame when changing animation
        elif new_state not in self.animations:
            # Fallback if the desired animation doesn't exist
            # Could default to "idle" or a specific placeholder animation
            if self.current_animation != "idle" and "idle" in self.animations:
                self.current_animation = "idle"
                self.current_frame = 0
            # If even "idle" isn't there, keep current_animation but issue a warning
            # print(f"Warning: No animation for '{new_state}' or 'idle' for {self.__class__.__name__}")
        
        self.state = new_state # Update internal state string

    def calc_grav(self):
        """Applies gravity to the vertical velocity, capping at max fall speed, if enabled."""
        if self.use_gravity:
            self.change_y += config.GLOBAL_GRAVITY
            if self.change_y > config.MAX_FALL_SPEED: # Uses MAX_FALL_SPEED from config
                self.change_y = config.MAX_FALL_SPEED

    def _resolve_vertical_collision(self):
        """Resolves collisions with platforms after vertical movement."""
        self.on_ground = False # Reset on_ground flag
        if self.platforms:
            collided_platforms = pygame.sprite.spritecollide(self, self.platforms, False)
            for platform in collided_platforms:
                if self.change_y > 0: # Moving down, hit top of platform
                    self.rect.bottom = platform.rect.top
                    self.change_y = 0
                    self.on_ground = True
                elif self.change_y < 0: # Moving up, hit bottom of platform
                    self.rect.top = platform.rect.bottom
                    self.change_y = 0

    def _resolve_horizontal_collision(self):
        """Resolves collisions with platforms after horizontal movement."""
        if self.platforms:
            collided_platforms = pygame.sprite.spritecollide(self, self.platforms, False)
            for platform in collided_platforms:
                if self.change_x > 0: # Moving right, hit left side of platform
                    self.rect.right = platform.rect.left
                elif self.change_x < 0: # Moving left, hit right side of platform
                    self.rect.left = platform.rect.right
                self.change_x = 0 # Stop horizontal movement upon collision

    def update(self):
        """
        Main update method for DynamicObject. Handles gravity, timed states,
        movement, collision resolution, and animation/state updates.
        """
        # 1. Apply gravity (before vertical movement)
        self.calc_grav()

        # 2. Apply state-based movement overrides
        # These flags are managed by _handle_timed_state_end in update_animation
        if self.freeze or self.is_dying or self.is_hurting or self.is_shooting or self.is_attacking:
            # Stop movement if in one of these override states
            self.change_x = 0
            if self.freeze: # Freeze also stops vertical movement
                self.change_y = 0

        # 3. Apply horizontal movement and resolve horizontal collisions
        self.rect.x += self.change_x
        self._resolve_horizontal_collision() # Adjusts self.rect.x and self.change_x

        # Clamp to scene boundaries horizontally
        if self.rect.right > config.SCENE_WIDTH:
            self.rect.right = config.SCENE_WIDTH
            self.change_x = 0
        elif self.rect.left < 0:
            self.rect.left = 0
            self.change_x = 0

        # 4. Apply vertical movement and resolve vertical collisions
        self.rect.y += self.change_y
        self._resolve_vertical_collision() # Adjusts self.rect.y, self.change_y, and self.on_ground

        # Clamp to scene boundaries vertically (optional, depending on game design)
        # If object falls below screen, kill it
        if self.rect.top > config.SCENE_HEIGHT + 100:
            self.kill()
        # If jumping and hits top of screen
        if self.rect.top < 0:
            self.rect.top = 0
            self.change_y = 0 # Stop upward movement

        # 5. Update state and animation (based on final movement/flags)
        self.update_state()
        self.update_animation()

class Player(DynamicObject):
    def __init__(self, x, y, width=30, height=30, color=None, health=100, damage=100, image_path=None, animations=None, platforms=None):
        super().__init__(x, y, width, height, color, image_path, animations, platforms)
        self.health = health
        self.max_health = health
        self.damage = damage
        self.shield = False
        self.last_hurt_time = 0 # Cooldown for hurt animation
        self.last_shoot_time = 0 # Cooldown for shoot animation
        self.last_attack_time = 0 # Cooldown for attack animation

    def take_damage(self, amount):
        if self.shield:
            return
        """Subtracts the given amount from player's health."""
        self.health -= amount
        if self.health < 0:
            self.health = 0

        if self.health <= 0 and not self.is_dying:
            self.is_dying = True
            self.state = "death"
            self.current_animation = "death"
            self.original_change_x = self.change_x # Capture current velocity before death
            self.change_x = 0 # Stop movement during death
            self.change_y = 0 # Stop vertical movement during death
            if "death" not in self.animations: # If no death animation, just kill instantly
                self.kill()
        elif self.health > 0 and not self.is_dying:
            now = pygame.time.get_ticks()
            # Using self.hurt_duration for cooldown consistency
            if not self.is_hurting and (now - self.last_hurt_time > self.hurt_duration):
                self.is_hurting = True
                self.hurt_start_time = now
                self.state = "hurt"
                self.current_animation = "hurt"
                self.original_change_x = self.change_x # Save current movement before stopping
                # self.change_x will be set to 0 by DynamicObject's update due to is_hurting
            self.last_hurt_time = now

    def is_dead(self):
        """Returns True if the player's health has dropped to 0."""
        return self.health <= 0

    def _can_perform_action(self):
        """Helper to check if player can perform actions like shoot or attack."""
        return not self.is_dying and not self.is_hurting and not self.freeze

    def shoot(self):
        """Initiates shoot animation and returns a Projectile object."""
        if self._can_perform_action():
            now = pygame.time.get_ticks()
            if not self.is_shooting and (now - self.last_shoot_time > self.shoot_duration): # Use shoot_duration for cooldown
                self.is_shooting = True
                self.shoot_start_time = now
                self.state = "shoot"
                self.current_animation = "shoot"
                self.original_change_x = self.change_x # Save original velocity
                # self.change_x will be set to 0 by DynamicObject's update due to is_shooting
                self.last_shoot_time = now
                return True # Indicate that shoot action was initiated
        return False # Indicate that shoot action was NOT initiated (e.g., on cooldown or cannot perform)

    def attack(self):
        """Initiates attack animation."""
        if self._can_perform_action():
            now = pygame.time.get_ticks()
            if not self.is_attacking and (now - self.last_attack_time > self.attack_duration): # Use attack_duration for cooldown
                self.is_attacking = True
                self.attack_start_time = now
                self.state = "attack"
                self.current_animation = "attack"
                self.original_change_x = self.change_x # Save original velocity
                # self.change_x will be set to 0 by DynamicObject's update due to is_attacking
                self.last_attack_time = now
                return True
        return False

    def draw_health_bar(self, surface):
        """Draws a health bar above the player based on current health."""
        bar_width = self.rect.width
        bar_height = config.PLAYER_BAR_HEIGHT
        bar_x = self.rect.x
        bar_y = self.rect.y - bar_height - 5

        health_ratio = self.health / self.max_health
        health_width = bar_width * health_ratio
 
        pygame.draw.rect(surface, config.PLAYER_BAR_BACKGROUND_COLOR, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, config.PLAYER_BAR_HEALTH_COLOR, (bar_x, bar_y, health_width, bar_height))

    def update(self):
        # Player-specific logic should set change_x and change_y based on input
        # and then call super().update()
        super().update() # Calls DynamicObject's update to handle all movement, collisions, animations

class Fighter(Player):
    def __init__(self, x, y, width=70, height=70, color=None, controls=None, health=config.PLAYER_HEALTH,
                 damage=config.PLAYER_DAMAGE, image_path=None, platforms=None, animations=None):
        # Pass platforms to DynamicObject via Player's super() call
        super().__init__(x, y, width, height, color, health, damage, image_path, animations, platforms)
        self.controls = controls or {}
        self.speed = config.PLAYER_SPEED
        self.jump_strength = config.PLAYER_JUMP # Should be negative for upward movement

        self.powered = False
        self.left_duration_powerup = 0
        self.started_powerup = 0
        self.powered_up_type = ""
        self.powered_up_amount = 0
        self.supershot = False
        self.supershot_amount = 1

    def upgrade(self, type, amount):
        self.powered_up_amount = amount
        self.started_powerup = pygame.time.get_ticks()
        self.left_duration_powerup = 5000 # 5 seconds
        if type == "damage":
            self.damage += amount
        elif type == "double_jump":
            # Assuming double_jump affects jump_strength, e.g., makes jumps higher/easier
            # Or perhaps allows an extra jump. This implementation makes jump_strength smaller (stronger jump)
            self.jump_strength -= amount # e.g., -10 becomes -15
        elif type == "shield":
            self.shield = True
        elif type == "supershot":
            self.supershot = True
            self.supershot_amount += amount
        
        self.powered = True
        self.powered_up_type = type

    def check_power_up(self):
        """Checks if a power-up has expired and reverts effects."""
        if not self.powered:
            return
        now = pygame.time.get_ticks()
        if now - self.started_powerup >= self.left_duration_powerup:
            if self.powered_up_type == "damage":
                self.damage -= self.powered_up_amount
            elif self.powered_up_type == "double_jump":
                self.jump_strength += self.powered_up_amount # Revert jump strength
            elif self.powered_up_type == "shield":
                self.shield = False
            elif self.powered_up_type == "supershot":
                self.supershot = False
                self.supershot_amount = 1 # Reset supershot amount
            
            self.powered = False
            self.left_duration_powerup = 0
            self.started_powerup = 0
            self.powered_up_type = ""
            self.powered_up_amount = 0

    def update(self):
        self.check_power_up()

        keys = pygame.key.get_pressed()

        # Reset change_x based on player input for this frame
        self.change_x = 0
        if self.controls.get("left") and keys[self.controls["left"]]:
            self.change_x = (-1) * self.speed
            self.facing_right = False
        elif self.controls.get("right") and keys[self.controls["right"]]:
            self.change_x = self.speed
            self.facing_right = True

        # Apply jump if jump key pressed and on ground
        if self.controls.get("jump") and keys[self.controls["jump"]] and self.on_ground:
            self.change_y = self.jump_strength

        # Call parent's update. It will apply change_x/y, resolve collisions, update animations.
        super().update()

    def shoot(self):
        """Creates a projectile with potential supershot effect."""
        if super().shoot(): # Call Player's shoot to trigger animation and cooldown
            velocity_x = config.PROJECTILE_SPEED if self.facing_right else (-1) * config.PROJECTILE_SPEED
            # Adjust projectile starting position to account for fighter size
            offset_x = (self.rect.width // 2) if self.facing_right else (-self.rect.width // 2)
            
            # Create the projectile
            return Projectile(self.rect.centerx + offset_x, 
                             self.rect.centery, 
                             velocity=(velocity_x * self.supershot_amount, 0),
                             damage=self.damage,
                             image_path="src/assets/images/inused_single_images/bullet.png", 
                             owner=self)
        return None # Return None if shoot was not allowed (e.g., on cooldown)
 
class NPC(Player):
    vision_boost = 0 # Class variable for global vision boost
    
    def __init__(self, x, y, width=32, height=48, color=None, speed=2, health=config.NPC_HEALTH, 
                damage=config.NPC_DAMAGE, image_path=None, platforms=None, 
                projectiles=None, all_sprites=None, fighter=None, animations=None, roam=True):
        # Pass platforms to DynamicObject via Player's super() call
        super().__init__(x, y, width, height, color, health, damage, image_path, animations, platforms)
        self.speed = speed
        self.projectiles = projectiles # For ranged NPCs
        self.all_sprites = all_sprites # For adding new sprites (projectiles)
        self.single_fighter = fighter # The player/fighter to target
        self.can_see_the_fighter = False
        self.show_vision_line = True # For debugging vision
        self.roam = roam # If it's a standing or patroling npc

    def update_vision(self):
        """Checks line of sight to the fighter, considering platforms."""
        if not self.single_fighter or not self.platforms:
            self.can_see_the_fighter = False
            return

        npc_center = self.rect.center
        fighter_center = self.single_fighter.rect.center
        collision_with_platform = False

        # Check for line-of-sight collision with any platform
        # Note: This is a basic check. For complex maps, a more advanced raycasting might be needed.
        for platform in self.platforms:
            if platform.rect.clipline(npc_center, fighter_center):
                collision_with_platform = True
                break
        
        # Apply global vision boost
        self.can_see_the_fighter = not collision_with_platform or (NPC.vision_boost > 0)

    def draw_vision_line(self, surface):
        """Draws a line from NPC to fighter to visualize line of sight."""
        if not self.single_fighter or not self.show_vision_line:
            return
        npc_center = self.rect.center
        fighter_center = self.single_fighter.rect.center
        color = (0, 255, 0) if self.can_see_the_fighter else (255, 0, 0) # Green if visible, Red if blocked
        pygame.draw.line(surface, color, npc_center, fighter_center, 2)

    def update(self):
        self.update_vision()

        # Determine NPC's desired change_x
        self.change_x = 0 # Reset for this frame

        if self.single_fighter and self.can_see_the_fighter:
            # Face and potentially move towards the fighter if visible and roaming
            self.facing_right = self.single_fighter.rect.centerx > self.rect.centerx
            if self.roam: # Roaming NPCs chase when they see the fighter
                self.change_x = self.speed if self.facing_right else -self.speed
            # If not roaming, change_x remains 0 (stationary)
        elif self.roam:
            # Patrol behavior if not seeing the fighter and set to roam
            # If current change_x is 0 (e.g., after an attack animation ended), set it to patrol speed
            if self.change_x == 0:
                self.change_x = self.speed if self.facing_right else -self.speed
            # The base DynamicObject will handle platform edge detection via _resolve_horizontal_collision

        # Call parent's update. It will apply change_x/y, resolve collisions, update animations.
        super().update()

class Suicide_Bomb(NPC):
    """A NPC that patrols until it sees the fighter, then chases and explodes when close enough."""
    def __init__(self, x, y, width=40, height=32, color=None, speed=0.3, health=50, 
                 damage=20, image_path=None, platforms=None, projectiles=None, 
                 all_sprites=None, fighter=None, animations=None, roam=True):
        super().__init__(x, y, width, height, color, speed, health, damage, image_path, 
                         platforms=platforms, projectiles=projectiles, all_sprites=all_sprites, 
                         fighter=fighter, animations=animations, roam=roam)
        self.explosion_range = 50
        self.explosion_damage = damage
        self.exploded = False

    def update(self):
        self.update_vision()

        if self.exploded:
            # If already exploded, just let the base class handle death animation/killing
            super().update()
            return

        if self.single_fighter and self.can_see_the_fighter:
            dist = math.hypot(self.rect.centerx - self.single_fighter.rect.centerx,
                              self.rect.centery - self.single_fighter.rect.centery)
            
            if dist <= self.explosion_range:
                # Trigger explosion (damage fighter, initiate death sequence)
                self.single_fighter.take_damage(self.explosion_damage)
                self.is_dying = True # Trigger death animation
                self.state = "death"
                self.current_animation = "death"
                # Movement will be stopped by DynamicObject.update due to is_dying
                self.exploded = True
            else:
                # Chase the fighter
                self.facing_right = self.single_fighter.rect.centerx > self.rect.centerx
                self.change_x = self.speed if self.facing_right else -self.speed
        elif self.roam:
            # Patrol if not seeing fighter
            if self.change_x == 0:
                self.change_x = self.speed if self.facing_right else -self.speed
        else: # Stationary if not roaming and not chasing
            self.change_x = 0

        super().update()

class Eye(NPC):
    """
    A support enemy that increases the vision distance of all NPCs (enemies)
    as long as it is alive.
    """
    def __init__(self, x, y, width=20, height=20, color=(255,0,255), speed=0, animations=None, platforms=None, fighter=None):
        # Eye is usually stationary, so roam=False
        super().__init__(x, y, width, height, color, speed, health=100, damage=0, platforms=platforms, animations=animations, roam=False, fighter=fighter)
        self.vision_increase = 500 # Boost value to add to all NPCs' vision distance

    def update(self):
        # While alive, set the global vision boost
        NPC.vision_boost = self.vision_increase
        # Eye is stationary, so change_x will remain 0 from init and roam=False
        super().update()

    def kill(self):
        # When Eye is killed, remove the vision boost
        NPC.vision_boost = 0
        super().kill()

class Ranged(NPC):
    """Ranged NPC uses projectile attacks."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attack_range = 600
        self.reload_time = 3000
        # self.last_shot = pygame.time.get_ticks() # Redundant, use self.last_shoot_time

    def update(self):
        now = pygame.time.get_ticks()

        # If fighter is visible, within range (including vision boost), and can shoot
        if (self.single_fighter and self.can_see_the_fighter and 
            math.hypot(self.rect.centerx - self.single_fighter.rect.centerx,
                       self.rect.centery - self.single_fighter.rect.centery) <= (self.attack_range + NPC.vision_boost) and
            not self.is_shooting and (now - self.last_shoot_time >= self.reload_time)): # Use last_shoot_time
            
            # Initiate shoot animation
            self.is_shooting = True
            self.shoot_start_time = now
            self.state = "shoot"
            self.current_animation = "shoot"
            self.original_change_x = self.change_x # Save current movement
            # self.change_x will be set to 0 by DynamicObject.update due to is_shooting

            # Create and add projectile
            velocity_x = config.PROJECTILE_SPEED if self.facing_right else (-1) * config.PROJECTILE_SPEED
            projectile = Projectile(self.rect.centerx, self.rect.centery, 
                                     velocity=(velocity_x, 0), damage=self.damage, owner=self,image_path="src/assets/images/inused_single_images/bullet.png")
                        
            self.projectiles.add(projectile)
            self.all_sprites.add(projectile)
            self.last_shoot_time = now # Update the last shoot time for cooldown

        elif not self.is_shooting: # If not currently shooting animation, set movement
            # Chase fighter if visible and within range, or patrol if not
            if self.single_fighter and self.can_see_the_fighter and self.roam:
                 # Only move if out of range, otherwise hold position to shoot
                dist = math.hypot(self.rect.centerx - self.single_fighter.rect.centerx,
                                  self.rect.centery - self.single_fighter.rect.centery)
                if dist > (self.attack_range + NPC.vision_boost): # Too far, move closer
                    self.facing_right = self.single_fighter.rect.centerx > self.rect.centerx
                    self.change_x = self.speed if self.facing_right else -self.speed
                else: # Within range, stop and prepare to shoot (handled by is_shooting above)
                    self.change_x = 0
            elif self.roam: # Patrol if not seeing fighter
                if self.change_x == 0: # If stopped (e.g., after last action), resume patrol
                    self.change_x = self.speed if self.facing_right else -self.speed
            else: # Stationary if not roaming
                self.change_x = 0
        
        super().update() # Process movement, collision, animation based on determined change_x

class Melee(NPC):
    """Melee NPC uses close combat attacks."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attack_range = 40
        self.attack_power = self.damage
        self.attack_cooldown = 3000 # Faster cooldown for melee, adjust as needed

    def update(self):
        now = pygame.time.get_ticks()

        # If fighter is visible, within range, and can attack
        if (self.single_fighter and self.can_see_the_fighter and
            math.hypot(self.rect.centerx - self.single_fighter.rect.centerx,
                       self.rect.centery - self.single_fighter.rect.centery) <= self.attack_range and
            not self.is_attacking and (now - self.last_attack_time >= self.attack_cooldown)):

            # Trigger attack animation
            self.is_attacking = True
            self.attack_start_time = now
            self.state = "attack"
            self.current_animation = "attack"
            self.original_change_x = self.change_x # Save current movement
            # self.change_x will be set to 0 by DynamicObject.update due to is_attacking

            self.single_fighter.take_damage(self.attack_power) # Deal damage immediately on attack initiation
            self.last_attack_time = now # Update cooldown
        
        elif not self.is_attacking: # If not currently attacking animation, set movement
            # Chase fighter if visible and within range, or patrol if not
            if self.single_fighter and self.can_see_the_fighter and self.roam:
                dist = math.hypot(self.rect.centerx - self.single_fighter.rect.centerx,
                                  self.rect.centery - self.single_fighter.rect.centery)
                if dist > self.attack_range: # Too far, move closer
                    self.facing_right = self.single_fighter.rect.centerx > self.rect.centerx
                    self.change_x = self.speed if self.facing_right else -self.speed
                else: # Within range, stop and prepare to attack (handled by is_attacking above)
                    self.change_x = 0
            elif self.roam: # Patrol if not seeing fighter
                if self.change_x == 0: # If stopped (e.g., after last action), resume patrol
                    self.change_x = self.speed if self.facing_right else -self.speed
            else: # Stationary if not roaming
                self.change_x = 0
        
        super().update()

class Medusa(Melee):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.freeze_duration = 1000 # Medusa's unique attack duration

    def update(self):
        now = pygame.time.get_ticks()

        # Medusa's attack logic: same as Melee, but triggers freeze instead of damage
        if (self.single_fighter and self.can_see_the_fighter and 
            math.hypot(self.rect.centerx - self.single_fighter.rect.centerx,
                       self.rect.centery - self.single_fighter.rect.centery) <= self.attack_range and
            not self.is_attacking and (now - self.last_attack_time >= self.attack_cooldown)):

            self.is_attacking = True
            self.attack_start_time = now
            self.state = "attack"
            self.current_animation = "attack"
            self.original_change_x = self.change_x # Save current movement

            # Medusa-specific effect: freeze the fighter
            if not self.single_fighter.freeze: # Only apply if not already frozen
                self.single_fighter.freeze = True
                self.single_fighter.freezed_time = now
                self.single_fighter.freeze_duration = self.freeze_duration # Apply Medusa's specific freeze duration

            self.last_attack_time = now
        
        elif not self.is_attacking: # If not attacking animation, set movement
            # Medusa's movement logic (same as Melee for chasing/patrolling)
            if self.single_fighter and self.can_see_the_fighter and self.roam: # Corrected typo here
                dist = math.hypot(self.rect.centerx - self.single_fighter.rect.centerx,
                                  self.rect.centery - self.single_fighter.rect.centery)
                if dist > self.attack_range:
                    self.facing_right = self.single_fighter.rect.centerx > self.rect.centerx
                    self.change_x = self.speed if self.facing_right else -self.speed
                else:
                    self.change_x = 0
            elif self.roam:
                if self.change_x == 0:
                    self.change_x = self.speed if self.facing_right else -self.speed
            else:
                self.change_x = 0

        super().update() # Process movement, collision, animation

class Projectile(DynamicObject):
    """A projectile that moves with a fixed velocity."""
    def __init__(self, x, y, width=10, height=10, color=(255,255,0), velocity=(10, 0), damage=config.PROJECTILE_DAMAGE, 
                 use_gravity=False, image_path=None, owner=None, animations=None, platforms=None):
        # Projectiles typically don't interact with platforms for collision resolution
        # unless they are complex (e.g., bouncing, arrows).
        # We pass platforms=None here to DynamicObject.
        super().__init__(x, y, width, height, color, image_path, animations, platforms=None)
        self.damage = damage
        self.velocity_x, self.velocity_y = velocity
        self.use_gravity = use_gravity
        self.owner = owner # Store the owner (e.g., the Fighter who shot it)
        # For projectiles, change_x/y is handled by fixed velocity, not external forces usually
        self.change_x = self.velocity_x # Initialize for DynamicObject's update to use
        self.change_y = self.velocity_y # Initialize for DynamicObject's update to use

    def update(self):
        # If not using gravity, DynamicObject's calc_grav will not add to self.change_y
        # If using gravity, self.change_y will be affected by calc_grav.
        # DynamicObject.update will handle applying change_x/y to rect and boundary checks.
        super().update()
        # Projectiles might have their own specific collision checks with other objects
        # (e.g., enemies or player) in the main game loop, not here.

class PowerUp(DynamicObject):
    """A power-up that sits there, potentially affected by gravity, and can be collected."""
    def __init__(self, x, y, type, amount, width=30, height=30, color=(255,255,0), animations=None, image_path=None, platforms=None):
        # Power-ups might interact with platforms for falling
        super().__init__(x, y, width, height, color, image_path, animations, platforms)
        self.upgrade_type = type
        self.amount = amount
        # self.duration (PowerUp's internal duration before despawning, if any)
        # Note: Fighter uses its own `left_duration_powerup` for active power-up duration
        self.use_gravity = True # Power-ups usually fall
        self.change_y = 0 # Start still, gravity will apply

    def update(self):
        # PowerUp's only special logic is often gravity and collision with ground
        # The DynamicObject.update method already handles calc_grav and _resolve_vertical_collision
        super().update()