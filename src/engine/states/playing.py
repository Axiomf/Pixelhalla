import pygame
import config
from src.engine.dynamic_objects import * # This imports the updated classes
from src.engine.states.base_state import BaseState

class PlayingState(BaseState):
    def __init__(self, scene):
        super().__init__(scene)
        self.back_button = pygame.Rect(20, 20, 100, 50)  # Top-left corner
        self.font = pygame.font.Font(None, 36)  # Use default font, size 36 for button text
        self.button_color = (0, 128, 255)  # Blue button
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.fighters = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.draw_background = None
        self.audio_playing = False  # Flag to track audio state

    def load_map(self, map_name):
        """Load map components using a module mapping."""
        map_modules = {
            "map1": "src.engine.map1",
            "map_levels": "src.engine.map_levels",
            "map_jesus": "src.engine.map_jesus",
            "map4": "src.engine.map4"
        }
        module_path = map_modules.get(map_name)
        if module_path:
            try:
                mod = __import__(module_path, fromlist=['all_sprites', 'platforms', 'enemies', 'fighters', 'projectiles', 'draw_background'])
                self.all_sprites = mod.all_sprites
                self.platforms = mod.platforms
                self.enemies = mod.enemies
                self.fighters = mod.fighters
                self.projectiles = mod.projectiles
                self.draw_background = mod.draw_background
                if map_name == "map1" and not self.audio_playing:
                    pygame.mixer.music.load("src/assets/sounds/Level03.mp3.mpeg")  # Load audio file
                    pygame.mixer.music.play(-1)  # Play in loop (-1 means loop indefinitely)
                    self.audio_playing = True
                if map_name == "map_levels" and not self.audio_playing:
                    pygame.mixer.music.load("src/assets/sounds/Level02.mp3.mpeg")  # Load audio file
                    pygame.mixer.music.play(-1)  # Play in loop (-1 means loop indefinitely)
                    self.audio_playing = True
                if map_name == "map_jesus" and not self.audio_playing:
                    pygame.mixer.music.load("src/assets/sounds/jesus_theme.mp3")  # Load audio file
                    pygame.mixer.music.play(-1)  # Play in loop (-1 means loop indefinitely)
                    self.audio_playing = True
                if map_name == "map4" and not self.audio_playing:
                    pygame.mixer.music.load("src/assets/sounds/LevelCTF.mp3.mpeg")  # Load audio file
                    pygame.mixer.music.play(-1)  # Play in loop (-1 means loop indefinitely)
                    self.audio_playing = True
            except ImportError as e:
                # print(f"Error loading map module {module_path}: {e}") # For debugging
                return

    def handle_event(self, event, current_time, scale, state_manager):
        """Handle events in playing state."""
        if not state_manager.current_map:
            state_manager.change_state(config.GAME_STATE_MAP_SELECT)
            return

        # Ensure map is loaded if not already
        if not self.all_sprites:
            self.load_map(state_manager.current_map)
        
        if event.type == pygame.KEYDOWN:
            for fighter in self.fighters:
                if event.key == fighter.controls.get("shoot"):
                    projectile = fighter.shoot()
                    # Only add projectile if it was actually created (not None)
                    if projectile:
                        self.all_sprites.add(projectile)
                        self.projectiles.add(projectile)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_time - state_manager.last_click_time > config.CLICK_COOLDOWN:
            pulsed_back_button = pygame.Rect(self.back_button.x - scale / 2, self.back_button.y - scale / 2, 
                                              self.back_button.width + scale, self.back_button.height + scale)
            if pulsed_back_button.collidepoint(event.pos):  # Back to map select
                state_manager.click_sound.play()  # Play click sound
                state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                state_manager.last_click_time = current_time
                # Reset the state by clearing sprite groups
                self.all_sprites.empty()
                self.platforms.empty()
                self.enemies.empty()
                self.fighters.empty()
                self.projectiles.empty()
                # Stop audio when leaving playing state
                if self.audio_playing:
                    pygame.mixer.music.stop()
                    self.audio_playing = False
                pygame.event.clear()  # Clear event queue

    def handle_collisions(self):
        """Handle collisions between sprites (excluding platform collisions which are handled internally by DynamicObject.update())."""
        # Platform collisions are now handled within DynamicObject.update() for all DynamicObjects.
        # This method focuses on interactions between different game entities.

        for sprite in self.all_sprites:
            # Removed: if isinstance(sprite, DynamicObject): sprite.handle_platform_collision(self.platforms)
            # This is now integrated into sprite.update()
            
            if isinstance(sprite, Projectile):
                # Ensure projectile owner is correctly identified
                if isinstance(sprite.owner, Fighter):
                    # Projectiles from a Fighter hit Enemies
                    hit_enemies = pygame.sprite.spritecollide(sprite, self.enemies, False)
                    if hit_enemies:
                        for enemy in hit_enemies:
                            enemy.take_damage(sprite.damage)
                            sprite.kill() # Projectile disappears on hit

                    # Projectiles from a Fighter (should not hit other fighters, only other players in PvP)
                    # For now, let's assume friendly fire is off for the owner.
                    # This logic should be expanded if there are multiple player characters.
                    hit_fighters = pygame.sprite.spritecollide(sprite, self.fighters, False)
                    if hit_fighters:
                        for fighter in hit_fighters:
                            if fighter != sprite.owner:  # Prevent projectile from damaging its owner
                                fighter.take_damage(sprite.damage)
                                sprite.kill() # Projectile disappears on hit
                else: # It is a projectile from an enemy (NPC)
                    hit_fighters = pygame.sprite.spritecollide(sprite, self.fighters, False)
                    if hit_fighters:
                        for fighter in hit_fighters:
                            fighter.take_damage(sprite.damage)
                            sprite.kill() # Projectile disappears on hit
            
            if isinstance(sprite, PowerUp):
                hit_fighters = pygame.sprite.spritecollide(sprite, self.fighters, False)
                if hit_fighters:
                    for fighter in hit_fighters:
                        fighter.upgrade(sprite.upgrade_type, sprite.amount)
                        sprite.kill() # PowerUp disappears on collection

    def update(self, current_time, scale, state_manager):
        """Update logic for playing state."""
        if not self.all_sprites: # Load map if not loaded (e.g., coming from map select)
            self.load_map(state_manager.current_map)
        
        self.all_sprites.update()  # Call update for all sprites (includes DynamicObject's internal collision handling)
        self.handle_collisions()  # Process all inter-sprite collisions

    def draw(self, scene, scale, state_manager):
        """Draw playing screen."""
        if not self.draw_background: # If background function not loaded, return
            return
            
        self.draw_background()  # Draw map background (assuming this function draws to 'scene' or fills)
        self.all_sprites.draw(scene) # Draw all sprites to the scene

        # Draw specific UI elements (vision line, health bar)
        for sprite in self.all_sprites:
            if isinstance(sprite, NPC):
                sprite.draw_vision_line(scene) # This is fine to be drawn here
            if isinstance(sprite, Player):
                sprite.draw_health_bar(scene) # This is fine to be drawn here

        # Draw Back button
        pulsed_back_button = pygame.Rect(self.back_button.x - scale / 2, self.back_button.y - scale / 2, 
                                          self.back_button.width + scale, self.back_button.height + scale)
        if pulsed_back_button.collidepoint(mouse_pos := pygame.mouse.get_pos()): # Walrus operator for convenience
            pygame.draw.rect(scene, (0, 200, 255), pulsed_back_button)  # Brighter blue for hover
        else:
            pygame.draw.rect(scene, self.button_color, pulsed_back_button)  # Normal blue
        
        back_button_text = self.font.render("Back", True, (255, 255, 255))
        pulsed_back_button_text_rect = back_button_text.get_rect(center=pulsed_back_button.center)
        scene.blit(back_button_text, pulsed_back_button_text_rect)