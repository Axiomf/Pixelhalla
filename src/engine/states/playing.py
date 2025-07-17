import pygame
import config
from src.engine.dynamic_objects import DynamicObject, Projectile, Player, PowerUp,NPC

class PlayingState:
    def __init__(self, scene):
        self.scene = scene
        self.back_button = pygame.Rect(20, 20, 100, 50)  # Top-left corner
        self.font = pygame.font.Font(None, 36)  # Use default font, size 36 for button text
        self.button_color = (0, 128, 255)  # Blue button
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.fighters = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.draw_background = None

    def load_map(self, map_name):
        """Load the specified map and its components."""
        try:
            if map_name == "map1":
                from src.engine.map1 import all_sprites, platforms, enemies, fighters, projectiles, draw_background
            elif map_name == "map_levels":
                from src.engine.map_levels import all_sprites, platforms, enemies, fighters, projectiles, draw_background
            elif map_name == "map_jesus":
                from src.engine.map_jesus import all_sprites, platforms, enemies, fighters, projectiles, draw_background
            elif map_name == "map4":
                from src.engine.map4 import all_sprites, platforms, enemies, fighters, projectiles, draw_background
            self.all_sprites = all_sprites
            self.platforms = platforms
            self.enemies = enemies
            self.fighters = fighters
            self.projectiles = projectiles
            self.draw_background = draw_background
        except ImportError as e:
            return

    def handle_event(self, event, current_time, scale, state_manager):
        """Handle events in playing screen."""
        if not state_manager.current_map:
            state_manager.change_state(config.GAME_STATE_MAP_SELECT)
            return

        # Load map if not already loaded
        if not self.all_sprites:
            self.load_map(state_manager.current_map)

        if event.type == pygame.KEYDOWN:
            for fighter in self.fighters:
                if event.key == fighter.controls.get("shoot"):
                    projectile = fighter.shoot()
                    self.all_sprites.add(projectile)
                    self.projectiles.add(projectile)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_time - state_manager.last_click_time > config.CLICK_COOLDOWN:
            pulsed_back_button = pygame.Rect(self.back_button.x - scale / 2, self.back_button.y - scale / 2, 
                                            self.back_button.width + scale, self.back_button.height + scale)
            if pulsed_back_button.collidepoint(event.pos):  # Back to map select
                state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                state_manager.last_click_time = current_time
                # Clear sprite groups to reset the map
                self.all_sprites.empty()
                self.platforms.empty()
                self.enemies.empty()
                self.fighters.empty()
                self.projectiles.empty()
                pygame.event.clear()  # Clear event queue

    def update(self, current_time, scale, state_manager):
        """Update logic for playing screen."""
        if not self.all_sprites:
            self.load_map(state_manager.current_map)
        self.all_sprites.update()  # Call update for all sprites

        # Handle collisions
        for sprite in self.all_sprites:
            if isinstance(sprite, DynamicObject):
                sprite.handle_platform_collision(self.platforms)
            if isinstance(sprite, Projectile):
                hit_enemies = pygame.sprite.spritecollide(sprite, self.enemies, False)
                if hit_enemies:
                    for enemy in hit_enemies:
                        enemy.take_damage(sprite.damage)
                        sprite.kill()
                hit_fighters = pygame.sprite.spritecollide(sprite, self.fighters, False)
                for fighter in hit_fighters:
                    if fighter != sprite.owner:  # Prevent projectile from damaging its owner
                        fighter.take_damage(sprite.damage)
                        sprite.kill()
                hit_platforms = pygame.sprite.spritecollide(sprite, self.platforms, False)
                for platform in hit_platforms:
                    sprite.kill()
            if isinstance(sprite, PowerUp):
                hit_fighters = pygame.sprite.spritecollide(sprite, self.fighters, False)
                if hit_fighters:
                    for fighter in hit_fighters:
                        fighter.upgrade(sprite.upgrade_type, sprite.amount)
                        sprite.kill()

    def draw(self, scene, scale, state_manager):
        """Draw playing screen."""
        if not self.draw_background:
            return
        mouse_pos = pygame.mouse.get_pos()
        self.draw_background()  # Use draw_background from selected map
        self.all_sprites.draw(scene)
        for sprite in self.all_sprites:
            if isinstance(sprite, NPC):
                sprite.draw_vision_line(scene)
            if isinstance(sprite, Player):  # NPC and Fighter
                sprite.draw_health_bar(scene)

        # Draw Back button
        pulsed_back_button = pygame.Rect(self.back_button.x - scale / 2, self.back_button.y - scale / 2, 
                                        self.back_button.width + scale, self.back_button.height + scale)
        if pulsed_back_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), pulsed_back_button)  # Brighter blue for hover
        else:
            pygame.draw.rect(scene, self.button_color, pulsed_back_button)  # Normal blue
        back_button_text = self.font.render("Back", True, (255, 255, 255))  # Render text here
        pulsed_back_button_text_rect = back_button_text.get_rect(center=pulsed_back_button.center)
        scene.blit(back_button_text, pulsed_back_button_text_rect)  # Draw Back button text