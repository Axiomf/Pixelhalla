import math
import pygame
import config
from .dynamic_objects import DynamicObject
from .player import Player

class NPC(Player):
    vision_boost = 0  # <-- New class variable for global vision boost 
    """A simple enemy that moves horizontally and bounces at the screen edges."""
    def __init__(self, x, y, width=32, height=48, color=None, speed=2, health=config.NPC_HEALTH, 
                damage=config.NPC_DAMAGE, image_path=None, platforms=None, 
                projectiles=None, all_sprites=None, fighter=None, animations=None,roam=True):
        super().__init__(x, y, width, height, color, health, damage, image_path, animations)
        self.change_x = speed  # Set initial horizontal patrol speed
        self.speed = speed
        self.facing_right = True  # Track the direction the NPC is facing (True for right, False for left)
        self.platforms = platforms  # Store platforms group
        self.projectiles = projectiles  # Store projectiles group
        self.all_sprites = all_sprites  # Store all_sprites group
        self.single_fighter = fighter
        self.can_see_the_fighter = False
        self.show_vision_line = True  # New flag to toggle vision line visibility

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

class Suicide_Bomb(NPC):
    """A NPC that patrols until it sees the fighter, then chases and explodes when close enough."""
    def __init__(self, x, y, width=40, height=32, color=None, speed=0.3, health=50, 
                 damage=20, image_path=None, platforms=None, projectiles=None, 
                 all_sprites=None, fighter=None, animations=None, roam=True):
        super().__init__(x, y, width, height, color, speed, health, damage, image_path, 
                         platforms=platforms, projectiles=projectiles, all_sprites=all_sprites, 
                         fighter=fighter, animations=animations, roam=roam)
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
    def __init__(self, x, y, width=20, height=20, color=(255,0,255), speed=0, animations=None, platforms=None):
        super().__init__(x, y, width, height, color, speed, health=100, damage=0, platforms=platforms, animations=animations,roam=False)
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
    

    def update(self):
        # Added melee attack logic: if fighter is within range and cooldown has passed, attack
        if self.single_fighter:
            dist = math.hypot(self.rect.centerx - self.single_fighter.rect.centerx,
                              self.rect.centery - self.single_fighter.rect.centery)
            now = pygame.time.get_ticks()
            # Use effective range = attack_range + NPC.vision_boost
            if not self.is_attacking and dist <= self.attack_range  and now - self.last_attack_time >= self.attack_cooldown:
                self.single_fighter.take_damage(self.attack_power)
                self.last_attack_time = now


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
        self.freeze_duration = 3000

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
    def __init__(self, x, y, width=10, height=10, color=(255,255,0), velocity=(10, 0), damage=config.PROJECTILE_DAMAGE, 
                 use_gravity=False, image_path=None, owner=None, animations=None):
        super().__init__(x, y, width, height, color, image_path, animations)
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