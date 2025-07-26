import pygame
import config
from src.engine.dynamic_objects import *
from src.engine.states.base_state import BaseState
from src.engine import map1, map4, map_boss, map_jesus, map_levels
from src.engine.gpt_api.state_changer import *
new_state_game = {  # external change
        "boss_health": 100,
        "fighter_health": 100,
        "boss_mood": "angry",
        "fighter_mood": "funny",
        "fighter_name": "the stranger",
        "fighter_class": "human",
        "fighter_level": 9,
        "dungeon_level": 10,
        "last_character_action": "Lucifer just spoke.",  
    }

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
        self.power_ups = pygame.sprite.Group()
        self.draw_background = None
        self.audio_playing = False  # Flag to track audio state
        self.level_complete = False  # Flag to track if level is complete
        self.map1_level = 0
        self.map_jesus_level = 0
        self.map_levels_level = 0
        self.map4_level = 0
        self.change_level = 0
        self.boss_state = False
        self.game_over_fighter1 = False
        self.game_over_fighter2 = False
        self.win = False

    def load_map(self, map_name, fighter1_id, fighter2_id, fighter_select_phase, level_state=None):
        """Load map components using a module mapping."""
        map_modules = {
            "map1": "src.engine.map1",
            "map_levels": "src.engine.map_levels",
            "map_jesus": "src.engine.map_jesus",
            "map4": "src.engine.map4",
            "map_boss" : "src.engine.map_boss"
        }
        module_path = map_modules.get(map_name)
        if module_path:
            try:
                if map_name == "map1" and not self.audio_playing:
                    map1.load_map(level_state, fighter1_id, fighter2_id, fighter_select_phase)
                    pygame.mixer.music.load("src/assets/sounds/Level03.mp3.mpeg")  # Load audio file
                    pygame.mixer.music.play(-1)  # Play in loop (-1 means loop indefinitely)
                    self.audio_playing = True
                if map_name == "map_levels" and not self.audio_playing:
                    pygame.mixer.music.load("src/assets/sounds/Level02.mp3.mpeg")  # Load audio file
                    pygame.mixer.music.play(-1)  # Play in loop (-1 means loop indefinitely)
                    self.audio_playing = True
                if map_name == "map_jesus" and not self.audio_playing:
                    map_jesus.load_map(level_state, fighter1_id, fighter2_id, fighter_select_phase)
                    pygame.mixer.music.load("src/assets/sounds/jesus_theme.mp3")  # Load audio file
                    pygame.mixer.music.play(-1)  # Play in loop (-1 means loop indefinitely)
                    self.audio_playing = True
                if map_name == "map4" and not self.audio_playing:
                    map4.load_map(level_state, fighter1_id, fighter2_id, fighter_select_phase)
                    pygame.mixer.music.load("src/assets/sounds/LevelCTF.mp3.mpeg")  # Load audio file
                    pygame.mixer.music.play(-1)  # Play in loop (-1 means loop indefinitely)
                    self.audio_playing = True
                if map_name == "map_boss" and not self.audio_playing:
                    map_boss.load_map(fighter1_id)
                    pygame.mixer.music.load("src/assets/sounds/boss_theme.mp3")  # Load audio file
                    pygame.mixer.music.play(-1)  # Play in loop (-1 means loop indefinitely)
                    self.audio_playing = True
                mod = __import__(module_path, fromlist=['all_sprites', 'platforms', 'enemies', 'fighters', 'projectiles', 'power_ups', 'draw_background'])
                self.all_sprites = mod.all_sprites
                self.platforms = mod.platforms
                self.enemies = mod.enemies
                self.fighters = mod.fighters
                self.projectiles = mod.projectiles
                self.power_ups = mod.power_ups
                self.draw_background = mod.draw_background
            except ImportError as e:
                return

    def handle_event(self, event, current_time, scale, map_name, state_manager):
        """Handle events in playing state."""
        if not state_manager.current_map:
            state_manager.change_state(config.GAME_STATE_MAP_SELECT)
            return

        if not self.all_sprites:
            self.load_map(state_manager.current_map, state_manager.fighter1_id, state_manager.fighter2_id, state_manager.fighter_select_phase)
        
        if self.boss_state:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if self.restart_button.collidepoint(mouse_pos):
                    state_manager.click_sound.play()
                    self.start_level(state_manager)
                elif self.back_button.collidepoint(mouse_pos):
                    state_manager.click_sound.play()  # Play click sound
                    state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                    state_manager.last_click_time = current_time
                    # Reset the state by clearing sprite groups
                    self.all_sprites.empty()
                    self.platforms.empty()
                    self.enemies.empty()
                    self.fighters.empty()
                    self.projectiles.empty()
                    self.power_ups.empty()
                    # Stop audio when leaving playing state
                    if self.audio_playing:
                        pygame.mixer.music.stop()
                        self.audio_playing = False
                        pygame.mixer.music.load("src/assets/sounds/LevelHellboy.mp3.mpeg")
                        pygame.mixer.music.play(-1)
                    pygame.event.clear()  # Clear event queue
        if self.game_over_fighter1:
            # if self.audio_playing:
            #         pygame.mixer.music.stop()
            #         self.audio_playing = False
            # if self.boss_state:
            #     state_manager.game_over_boss.play()
            # else:
            #     state_manager.game_over.play()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if map_name == "map1":
                    self.change_level = self.map1_level
                if map_name == "map_levels":
                    self.change_level = self.map_levels_level
                if map_name == "map_jesus":
                    self.change_level = self.map_jesus_level
                if map_name == "map4":
                   self.change_level = self.map4_level

                if self.restart_button.collidepoint(mouse_pos):
                    state_manager.click_sound.play()
                    self.start_level(state_manager)
                elif self.back_button.collidepoint(mouse_pos):
                    state_manager.click_sound.play()  # Play click sound
                    state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                    state_manager.last_click_time = current_time
                    # Reset the state by clearing sprite groups
                    self.all_sprites.empty()
                    self.platforms.empty()
                    self.enemies.empty()
                    self.fighters.empty()
                    self.projectiles.empty()
                    self.power_ups.empty()
                    # Stop audio when leaving playing state
                    if self.audio_playing:
                        pygame.mixer.music.stop()
                        self.audio_playing = False
                        pygame.mixer.music.load("src/assets/sounds/LevelHellboy.mp3.mpeg")
                        pygame.mixer.music.play(-1)
                    pygame.event.clear()  # Clear event queue
                if map_name == "map1":
                    self.map1_level = self.change_level
                if map_name == "map_levels":
                    self.map_levels_level = self.change_level
                if map_name == "map_jesus":
                    self.map_jesus_level = self.change_level
                if map_name == "map4":
                   self.map4_level = self.change_level
            return

        if self.level_complete:
            # if self.audio_playing:
            #         pygame.mixer.music.stop()
            #         self.audio_playing = False
            # if self.boss_state:
            #     state_manager.win_sound.play()
            # else:
            #     state_manager.level_complete_sound.play()
            # Handle clicks on end level buttons
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if map_name == "map1":
                    self.change_level = self.map1_level
                if map_name == "map_levels":
                    self.change_level = self.map_levels_level
                if map_name == "map_jesus":
                    self.change_level = self.map_jesus_level
                if map_name == "map4":
                   self.change_level = self.map4_level

                if self.next_button.collidepoint(mouse_pos)  and self.change_level == 3:
                    state_manager.click_sound.play()
                    # state_manager.change_state(config.GAME_STATE_NEXT_LEVEL)  # Assuming this state exists
                    state_manager.current_map = "map_boss"
                    self.boss_state = True
                    self.start_level(state_manager)
                elif self.next_button.collidepoint(mouse_pos):
                    state_manager.click_sound.play()
                    # state_manager.change_state(config.GAME_STATE_NEXT_LEVEL)  # Assuming this state exists
                    self.change_level += 1
                    self.start_level(state_manager)
                elif self.restart_button.collidepoint(mouse_pos):
                    state_manager.click_sound.play()
                    self.start_level(state_manager)
                elif self.back_button.collidepoint(mouse_pos):
                    state_manager.click_sound.play()  # Play click sound
                    state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                    state_manager.last_click_time = current_time
                    # Reset the state by clearing sprite groups
                    self.all_sprites.empty()
                    self.platforms.empty()
                    self.enemies.empty()
                    self.fighters.empty()
                    self.projectiles.empty()
                    self.power_ups.empty()
                    # Stop audio when leaving playing state
                    if self.audio_playing:
                        pygame.mixer.music.stop()
                        self.audio_playing = False
                        pygame.mixer.music.load("src/assets/sounds/LevelHellboy.mp3.mpeg")
                        pygame.mixer.music.play(-1)
                    pygame.event.clear()  # Clear event queue
                if map_name == "map1":
                    self.map1_level = self.change_level
                if map_name == "map_levels":
                    self.map_levels_level = self.change_level
                if map_name == "map_jesus":
                    self.map_jesus_level = self.change_level
                if map_name == "map4":
                   self.map4_level = self.change_level
            return

        if event.type == pygame.KEYDOWN:
            for fighter in self.fighters:
                if event.key == fighter.controls.get("shoot") and not fighter.freeze:
                    projectile = fighter.shoot()
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
                self.power_ups.empty()
                # Stop audio when leaving playing state
                if self.audio_playing:
                    pygame.mixer.music.stop()
                    self.audio_playing = False
                    pygame.mixer.music.load("src/assets/sounds/LevelHellboy.mp3.mpeg")
                    pygame.mixer.music.play(-1)
                pygame.event.clear()  # Clear event queue

    def handle_collisions(self, state_manager):
        """Handle collisions between sprites."""
        for sprite in self.all_sprites:
            if isinstance(sprite, DynamicObject):
                sprite.handle_platform_collision(self.platforms)
            if isinstance(sprite, Projectile):
                if isinstance(sprite.owner, Fighter):
                    hit_enemies = pygame.sprite.spritecollide(sprite, self.enemies, False)
                    if hit_enemies:
                        for enemy in hit_enemies:
                            enemy.take_damage(sprite.damage)
                            enemy.blood_sound.play()
                            sprite.kill()

                    hit_fighters = pygame.sprite.spritecollide(sprite, self.fighters, False)
                    if hit_fighters:
                        for fighter in hit_fighters:
                            if fighter != sprite.owner:  # Prevent projectile from damaging its owner
                                fighter.take_damage(sprite.damage)
                                fighter.blood_sound.play()
                                sprite.kill()
                else:  # it is a projectile of an enemy
                    hit_fighters = pygame.sprite.spritecollide(sprite, self.fighters, False)
                    if hit_fighters:
                        for fighter in hit_fighters:
                            fighter.take_damage(sprite.damage)
                            fighter.blood_sound.play()
                            sprite.kill()           
            if isinstance(sprite, PowerUp):
                hit_fighters = pygame.sprite.spritecollide(sprite, self.fighters, False)
                if hit_fighters:
                    for fighter in hit_fighters:
                        fighter.upgrade(sprite.upgrade_type, sprite.amount)
                        sprite.kill()
            if isinstance(sprite, Melee):
                hit_fighters = pygame.sprite.spritecollide(sprite, self.fighters, False)
                if hit_fighters:
                    for fighter in hit_fighters:
                        now = pygame.time.get_ticks()
                        if now - sprite.last_sound_time >= 2000:  # 3000 ms = 3 seconds
                            fighter.blood_sound.play()
                            sprite.last_sound_time = now  # Update the last sound time

    def update(self, current_time, scale, state_manager):
        global new_state_game 
        """Update logic for playing state."""
        if not self.all_sprites:
            self.load_map(state_manager.current_map, state_manager.fighter1_id, state_manager.fighter2_id, state_manager.fighter_select_phase, self.change_level)
        self.all_sprites.update()  # Call update for all sprites
        self.handle_collisions(state_manager)  # Process all collisions
        for enemy in self.enemies:
            if isinstance(enemy, Boss):  
                new_state_game["boss_health"] = enemy.health
                new_state_game["boss_mood"] = "extremely angry" if enemy.health <= enemy.max_health else "funny"
        for fighter in self.fighters:
            new_state_game["fighter_health"] = fighter.health
            new_state_game["fighter_mood"] = "under extreme pressure" if fighter.health <= fighter.max_health else ""
        


                
                



        change_game_state(new_state_game)

        # Check if all enemies are defeated
        if len(self.enemies) == 0 and not self.level_complete:
            self.level_complete = True
        if state_manager.fighter_select_phase == 1 and len(self.fighters) == 0 and not self.level_complete:
            self.game_over_fighter1 = True
            state_manager.win_boss = True
        boss = next((e for e in self.enemies if isinstance(e, Boss)), None)
        if not boss and self.boss_state:
            self.win = True
            state_manager.win_fighter = True

    def start_level(self, state_manager):
        """Restart the current level and start the next level"""
        self.game_over_fighter1 = False
        self.game_over_fighter2 = False
        self.all_sprites.empty()
        self.platforms.empty()
        self.enemies.empty()
        self.fighters.empty()
        self.projectiles.empty()
        self.power_ups.empty()
        self.level_complete = False
        self.load_map(state_manager.current_map, self.change_level,state_manager.fighter1_id, state_manager.fighter2_id, state_manager.fighter_select_phase)
        if self.audio_playing:
            pygame.mixer.music.stop()
            self.audio_playing = False

    def draw(self, scene, scale, state_manager):
        """Draw playing screen."""
        if not self.draw_background:
            return
        mouse_pos = pygame.mouse.get_pos()
        self.draw_background()  # Draw map background
        self.all_sprites.draw(scene)
        for sprite in self.all_sprites:
            if isinstance(sprite, NPC):
                sprite.draw_vision_line(scene)  # I wish this was handled somewhere else
            if isinstance(sprite, Player):  # I wish this was handled somewhere else
                sprite.draw_health_bar(scene)
        boss = next((e for e in self.enemies if isinstance(e, Boss)), None)
        fighter = next(iter(self.fighters), None)

        hover_color = (0, 200, 255)  # Light blue for hover
        default_color = self.button_color  # Default button color

        if boss and fighter:
            now = pygame.time.get_ticks()
            if boss.phase_effect_active:
                boss.fade_radius += 5
                mask_surface = pygame.Surface(scene.get_size(), pygame.SRCALPHA)
                mask_surface.fill((0, 0, 0, 255))  
                pygame.draw.circle(mask_surface, (0, 0, 0, 0), fighter.rect.center, boss.fade_radius)
                scene.blit(mask_surface, (0, 0))  
            elif boss.blackout_start > 0 and now - boss.blackout_start < boss.blackout_duration:
                scene.fill((0, 0, 0))  

        if self.game_over_fighter1:
            # Draw end level screen
            scene.fill((0, 0, 0, 128))  # Semi-transparent black overlay
            title_font = pygame.font.Font(None, 72)
            button_font = pygame.font.Font(None, 48)

            title_text = title_font.render("Game Over!", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(config.SCENE_WIDTH // 2, config.SCENE_HEIGHT // 4))
            scene.blit(title_text, title_rect)

            # Define button rectangles
            self.restart_button = pygame.Rect(config.SCENE_WIDTH // 2 - 100, config.SCENE_HEIGHT // 2 + 30, 200, 70)
            self.back_button = pygame.Rect(config.SCENE_WIDTH // 2 - 100, config.SCENE_HEIGHT // 2 + 110, 200, 70)

            # Draw buttons with hover effect
            pygame.draw.rect(scene, hover_color if self.restart_button.collidepoint(mouse_pos) else default_color, self.restart_button)
            pygame.draw.rect(scene, hover_color if self.back_button.collidepoint(mouse_pos) else default_color, self.back_button)

            # Draw button text
            restart_text = button_font.render("Restart", True, (255, 255, 255))
            back_text = button_font.render("Back to Map", True, (255, 255, 255))
            scene.blit(restart_text, restart_text.get_rect(center=self.restart_button.center))
            scene.blit(back_text, back_text.get_rect(center=self.back_button.center))

        elif self.level_complete:
            # Draw end level screen
            scene.fill((0, 0, 0, 128))  # Semi-transparent black overlay
            title_font = pygame.font.Font(None, 72)
            button_font = pygame.font.Font(None, 48)

            title_text = title_font.render("Level Complete!", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(config.SCENE_WIDTH // 2, config.SCENE_HEIGHT // 4))
            scene.blit(title_text, title_rect)

            # Define button rectangles
            self.next_button = pygame.Rect(config.SCENE_WIDTH // 2 - 100, config.SCENE_HEIGHT // 2 - 50, 200, 70)
            self.restart_button = pygame.Rect(config.SCENE_WIDTH // 2 - 100, config.SCENE_HEIGHT // 2 + 30, 200, 70)
            self.back_button = pygame.Rect(config.SCENE_WIDTH // 2 - 100, config.SCENE_HEIGHT // 2 + 110, 200, 70)

            # Draw buttons with hover effect
            pygame.draw.rect(scene, hover_color if self.next_button.collidepoint(mouse_pos) else default_color, self.next_button)
            pygame.draw.rect(scene, hover_color if self.restart_button.collidepoint(mouse_pos) else default_color, self.restart_button)
            pygame.draw.rect(scene, hover_color if self.back_button.collidepoint(mouse_pos) else default_color, self.back_button)

            # Draw button text
            next_text = button_font.render("Next Level", True, (255, 255, 255))
            restart_text = button_font.render("Restart", True, (255, 255, 255))
            back_text = button_font.render("Back to Map", True, (255, 255, 255))

            scene.blit(next_text, next_text.get_rect(center=self.next_button.center))
            scene.blit(restart_text, restart_text.get_rect(center=self.restart_button.center))
            scene.blit(back_text, back_text.get_rect(center=self.back_button.center))

        else:
            # Draw Back button with hover effect
            if self.win:
                scene.fill((0, 0, 0, 128))  # Semi-transparent black overlay
                title_font = pygame.font.Font(None, 72)
                title_text = title_font.render("You win!", True, (255, 255, 255))
                title_rect = title_text.get_rect(center=(config.SCENE_WIDTH // 2, config.SCENE_HEIGHT // 4))
                scene.blit(title_text, title_rect)
            self.back_button = pygame.Rect(1080, 20, 100, 50)  # Top-right corner
            pulsed_back_button = pygame.Rect(self.back_button.x - scale / 2, self.back_button.y - scale / 2, 
                                            self.back_button.width + scale, self.back_button.height + scale)
            pygame.draw.rect(scene, hover_color if pulsed_back_button.collidepoint(mouse_pos) else default_color, pulsed_back_button)
            back_button_text = self.font.render("Back", True, (255, 255, 255))
            pulsed_back_button_text_rect = back_button_text.get_rect(center=pulsed_back_button.center)
            scene.blit(back_button_text, pulsed_back_button_text_rect)  # Draw Back button text