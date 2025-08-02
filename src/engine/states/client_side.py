# client side
import pygame
import config
from src.engine.dynamic_objects import *
from src.engine.states.base_state import BaseState
from src.engine import map1, map4, map_boss, map_jesus, map_levels
import socket
import pickle
import threading
# package_to_server = {"request": "lobby" , "inputs" : []}
#blood_sound = pygame.mixer.Sound("src/assets/sounds/blood2.wav")

blood_sound = []
class PlayingState_Multiplayer(BaseState):
    def __init__(self, scene):
        super().__init__(scene)
        self.make_sound = False # flag to make the blood sound

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

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("127.0.0.1", 5555))
        self.package_to_server = {"inputs": []}
        self.network_thread = threading.Thread(target=self.receive_updates, daemon=True)
        self.network_thread.start()

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
                    map_levels.load_map(level_state, fighter1_id, fighter2_id, fighter_select_phase)
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

    def receive_updates(self):
        while True:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                updated_package = pickle.loads(data)
                # Update local sprite groups from the package
                self.all_sprites.empty()
                for group in [updated_package.get("platforms", []),
                              updated_package.get("fighters", []),
                              updated_package.get("projectiles", []),
                              updated_package.get("power_ups", [])]:
                    # Here we assume each group is a list of sprites; add them to the group.
                    for sprite in group:
                        self.all_sprites.add(sprite)
                # Play sounds if any are specified in updated_package["sounds"]
                for sound in updated_package.get("sounds", []):
                    sound.play()
            except Exception as e:
                print("Network error:", e)
                break

    def handle_event(self, event, current_time, scale, map_name, state_manager):
        global package_to_server
        """Handle events in playing state."""
        if not state_manager.current_map:
            state_manager.change_state(config.GAME_STATE_MAP_SELECT)
            return
        if not self.all_sprites:
            self.load_map(state_manager.current_map, state_manager.fighter1_id, state_manager.fighter2_id, state_manager.fighter_select_phase)
        
        if self.game_over_fighter1: # if died keep watching until the game is finished
            
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

        if event.type == pygame.KEYDOWN: # Get the state of keyboard keys
            keys = pygame.key.get_pressed()  
            if keys[pygame.K_a]:
                self.package_to_server["inputs"].append(pygame.K_a)# Get the state of keyboard keys
            elif keys[pygame.K_d]:
                self.package_to_server["inputs"].append(pygame.K_d)
            if keys[pygame.K_w]:
                self.package_to_server["inputs"].append(pygame.K_w)
            if keys[pygame.K_SPACE]:
                  self.package_to_server["inputs"].append(pygame.K_SPACE)

            # send package to server     
            try:
                self.client_socket.send(pickle.dumps(self.package_to_server))
            except Exception as e:
                print("Send error:", e)
            self.package_to_server["inputs"].clear()


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
        if not self.all_sprites:
            self.load_map(state_manager.current_map, state_manager.fighter1_id, state_manager.fighter2_id, state_manager.fighter_select_phase, self.change_level)
        
        # sent input in handle_event, recive objects from server and update sprites
        
        # receive()

        # Check if all enemies are defeated
        if len(self.enemies) == 0 and not self.level_complete:
            self.level_complete = True
            if self.audio_playing:
                pygame.mixer.music.stop()
                self.audio_playing = False
            state_manager.level_complete_sound.play()
        if state_manager.fighter_select_phase == 1 and len(self.fighters) == 0 and not self.level_complete:
            self.game_over_fighter1 = True
            

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

        if self.audio_playing:
            pygame.mixer.music.stop()
            self.audio_playing = False
        self.load_map(state_manager.current_map,state_manager.fighter1_id, state_manager.fighter2_id, state_manager.fighter_select_phase, self.change_level)

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