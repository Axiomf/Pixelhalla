import pygame
import config
from src.engine.dynamic_objects import *
from src.engine.states.base_state import BaseState
from src.engine import map1_multi, map4, map_boss, map_jesus, map_levels
import socket
import pickle
import threading

class PlayingState_Multiplayer(BaseState):
    def __init__(self, scene, state_manager):
        super().__init__(scene)
        self.scene = scene
        self.state_manager = state_manager
        self.back_button = pygame.Rect(1080, 20, 100, 50)
        self.font = pygame.font.Font(None, 36)
        self.button_color = (0, 128, 255)
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.fighters = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.draw_background = None
        self.audio_playing = False
        self.level_complete = False
        self.map1_level = 0
        self.map_jesus_level = 0
        self.map_levels_level = 0
        self.map4_level = 0
        self.change_level = 0
        self.boss_state = False
        self.game_over_fighter1 = False
        self.game_over_fighter2 = False
        self.win = False
        # Socket setup
        self.client_socket = state_manager.client_socket
        self.client_id = state_manager.client_id
        self.client_package = {
            "request_type": "connect",
            "username": state_manager.username,
            "fighter_id": state_manager.fighter1_id,
            "map_name": state_manager.current_map
        }
        # Load fighters and platforms locally and send to server
        map_data = self.load_map(state_manager.current_map, state_manager.fighter1_id)
        self.client_package["fighters"] = list(map_data["fighters"])
        self.client_package["platforms"] = list(map_data["platforms"])
        # try:
        self.client_socket.send(pickle.dumps(self.client_package))
        self.client_socket.settimeout(5.0)  # Set timeout for receiving response
        response = pickle.loads(self.client_socket.recv(2048))
        self.client_socket.settimeout(None)  # Reset timeout
            # if response["request_type"] != "matched":
            #     self.state_manager.error_message = response.get("message", "Connection failed")
            #     if self.client_socket:
            #         self.client_socket.close()
            #     self.state_manager.client_socket = None
            #     self.state_manager.client_id = None
            #     self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)
            #     return
        # except Exception as e:
        #     print(f"Send/Receive error: {e}")
        #     self.state_manager.error_message = "Failed to initialize game. Is the server running?"
        #     if self.client_socket:
        #         self.client_socket.close()
        #     self.state_manager.client_socket = None
        #     self.state_manager.client_id = None
        #     self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)
        #     return
        self.network_thread = threading.Thread(target=self.receive_updates, daemon=True)
        self.network_thread.start()

    def load_map(self, map_name, fighter_id):
        map_modules = {
            "map1": map1_multi,
            "map_levels": map_levels,
            "map_jesus": map_jesus,
            "map4": map4,
            "map_boss": map_boss
        }
        module = map_modules.get(map_name)
        if module:
            try:
                self.draw_background = module.draw_background
                if not self.audio_playing:
                    pygame.mixer.music.load(f"src/assets/sounds/Level03.mp3.mpeg")
                    pygame.mixer.music.play(-1)
                    self.audio_playing = True
                # Load fighters and platforms for this client
                return module.load_map(self.change_level, fighter_id, None, None, self.client_id, self.state_manager.username)
            except ImportError as e:
                print(f"Error loading map {map_name}: {e}")
                self.state_manager.error_message = f"Failed to load map {map_name}"
        return {"fighters": pygame.sprite.Group(), "platforms": pygame.sprite.Group()}

    def receive_updates(self):
        while True:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                updated_package = pickle.loads(data)
                if updated_package["request_type"] == "error":
                    self.state_manager.error_message = updated_package["message"]
                    if self.client_socket:
                        self.client_socket.close()
                    self.state_manager.client_socket = None
                    self.state_manager.client_id = None
                    self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                    break
                elif updated_package["request_type"] == "game_update":
                    self.all_sprites.empty()
                    self.fighters.empty()
                    self.platforms.empty()
                    self.projectiles.empty()
                    self.power_ups.empty()
                    for sprite in updated_package.get("platforms", []):
                        self.platforms.add(sprite)
                        self.all_sprites.add(sprite)
                    for sprite in updated_package.get("fighters", []):
                        self.fighters.add(sprite)
                        self.all_sprites.add(sprite)
                    for sprite in updated_package.get("projectiles", []):
                        self.projectiles.add(sprite)
                        self.all_sprites.add(sprite)
                    for sprite in updated_package.get("power_ups", []):
                        self.power_ups.add(sprite)
                        self.all_sprites.add(sprite)
                    for sound in updated_package.get("sounds", []):
                        sound.play()
                    # Check for game over
                    for fighter in self.fighters:
                        if fighter.id == self.client_id and fighter.health <= 0:
                            self.game_over_fighter1 = True
            except Exception as e:
                print("Network error:", e)
                self.state_manager.error_message = "Lost connection to server"
                if self.client_socket:
                    self.client_socket.close()
                self.state_manager.client_socket = None
                self.state_manager.client_id = None
                self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                break

    def handle_event(self, event, current_time, scale, map_name, state_manager):
        if not state_manager.current_map:
            state_manager.change_state(config.GAME_STATE_MAP_SELECT)
            return
        if not self.all_sprites:
            self.load_map(state_manager.current_map, state_manager.fighter1_id)

        if self.game_over_fighter1:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if map_name == "map1":
                    self.change_level = self.map1_level
                elif map_name == "map_levels":
                    self.change_level = self.map_levels_level
                elif map_name == "map_jesus":
                    self.change_level = self.map_jesus_level
                elif map_name == "map4":
                    self.change_level = self.map4_level
                if self.restart_button.collidepoint(mouse_pos):
                    state_manager.click_sound.play()
                    self.start_level(state_manager)
                elif self.back_button.collidepoint(mouse_pos):
                    state_manager.click_sound.play()
                    state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                    state_manager.last_click_time = current_time
                    self.all_sprites.empty()
                    self.platforms.empty()
                    self.fighters.empty()
                    self.projectiles.empty()
                    if self.audio_playing:
                        pygame.mixer.music.stop()
                        self.audio_playing = False
                    if self.client_socket:
                        self.client_socket.close()
                    state_manager.client_socket = None
                    state_manager.client_id = None
                    pygame.event.clear()
                if map_name == "map1":
                    self.map1_level = self.change_level
                elif map_name == "map_levels":
                    self.map_levels_level = self.change_level
                elif map_name == "map_jesus":
                    self.map_jesus_level = self.change_level
                elif map_name == "map4":
                    self.map4_level = self.change_level
            return

        if self.level_complete:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if map_name == "map1":
                    self.change_level = self.map1_level
                elif map_name == "map_levels":
                    self.change_level = self.map_levels_level
                elif map_name == "map_jesus":
                    self.change_level = self.map_jesus_level
                elif map_name == "map4":
                    self.change_level = self.map4_level
                if self.next_button.collidepoint(mouse_pos) and self.change_level == 3:
                    state_manager.click_sound.play()
                    state_manager.current_map = "map_boss"
                    self.boss_state = True
                    self.start_level(state_manager)
                elif self.next_button.collidepoint(mouse_pos):
                    state_manager.click_sound.play()
                    self.change_level += 1
                    self.start_level(state_manager)
                elif self.restart_button.collidepoint(mouse_pos):
                    state_manager.click_sound.play()
                    self.start_level(state_manager)
                elif self.back_button.collidepoint(mouse_pos):
                    state_manager.click_sound.play()
                    state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                    state_manager.last_click_time = current_time
                    self.all_sprites.empty()
                    self.platforms.empty()
                    self.fighters.empty()
                    self.projectiles.empty()
                    if self.audio_playing:
                        pygame.mixer.music.stop()
                        self.audio_playing = False
                    if self.client_socket:
                        self.client_socket.close()
                    state_manager.client_socket = None
                    state_manager.client_id = None
                    pygame.event.clear()
                if map_name == "map1":
                    self.map1_level = self.change_level
                elif map_name == "map_levels":
                    self.map_levels_level = self.change_level
                elif map_name == "map_jesus":
                    self.map_jesus_level = self.change_level
                elif map_name == "map4":
                    self.map4_level = self.change_level
            return

        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            self.client_package["inputs"] = []
            if keys[pygame.K_a]:
                self.client_package["inputs"].append(pygame.K_a)
            if keys[pygame.K_d]:
                self.client_package["inputs"].append(pygame.K_d)
            if keys[pygame.K_w]:
                self.client_package["inputs"].append(pygame.K_w)
            if keys[pygame.K_SPACE]:
                self.client_package["inputs"].append(pygame.K_SPACE)
            self.client_package["request_type"] = "input"
            self.client_package["fighter_id"] = self.client_id
            try:
                if self.client_socket:
                    self.client_socket.send(pickle.dumps(self.client_package))
            except Exception as e:
                print("Send error:", e)
                self.state_manager.error_message = "Failed to send input to server"
                if self.client_socket:
                    self.client_socket.close()
                self.state_manager.client_socket = None
                self.state_manager.client_id = None
                self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)
            self.client_package["inputs"].clear()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_time - state_manager.last_click_time > config.CLICK_COOLDOWN:
            pulsed_back_button = pygame.Rect(self.back_button.x - scale / 2, self.back_button.y - scale / 2, 
                                            self.back_button.width + scale, self.back_button.height + scale)
            if pulsed_back_button.collidepoint(event.pos):
                state_manager.click_sound.play()
                state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                state_manager.last_click_time = current_time
                self.all_sprites.empty()
                self.platforms.empty()
                self.fighters.empty()
                self.projectiles.empty()
                if self.audio_playing:
                    pygame.mixer.music.stop()
                    self.audio_playing = False
                if self.client_socket:
                    self.client_socket.close()
                state_manager.client_socket = None
                state_manager.client_id = None
                pygame.event.clear()

    def handle_collisions(self, state_manager):
        for sprite in self.all_sprites:
            if isinstance(sprite, DynamicObject):
                sprite.handle_platform_collision(self.platforms)
            if isinstance(sprite, Projectile):
                if isinstance(sprite.owner, Fighter):
                    hit_fighters = pygame.sprite.spritecollide(sprite, self.fighters, False)
                    if hit_fighters:
                        for fighter in hit_fighters:
                            if fighter != sprite.owner:
                                fighter.take_damage(sprite.damage)
                                fighter.blood_sound.play()
                                sprite.kill()
                else:
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

    def start_level(self, state_manager):
        self.game_over_fighter1 = False
        self.game_over_fighter2 = False
        self.all_sprites.empty()
        self.platforms.empty()
        self.fighters.empty()
        self.projectiles.empty()
        self.level_complete = False
        if self.audio_playing:
            pygame.mixer.music.stop()
            self.audio_playing = False
        map_data = self.load_map(state_manager.current_map, state_manager.fighter1_id)
        self.client_package["request_type"] = "connect"
        self.client_package["fighters"] = list(map_data["fighters"])
        self.client_package["platforms"] = list(map_data["platforms"])
        try:
            if self.client_socket:
                self.client_socket.send(pickle.dumps(self.client_package))
        except Exception as e:
            print("Send error:", e)
            self.state_manager.error_message = "Failed to restart game"
            if self.client_socket:
                self.client_socket.close()
            self.state_manager.client_socket = None
            self.state_manager.client_id = None
            self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)

    def draw(self, scene, scale, state_manager):
        if not self.draw_background:
            return
        mouse_pos = pygame.mouse.get_pos()
        self.draw_background()
        self.all_sprites.draw(scene)
        for sprite in self.all_sprites:
            if isinstance(sprite, NPC):
                sprite.draw_vision_line(scene)
            if isinstance(sprite, Player):
                sprite.draw_health_bar(scene)
        boss = next((e for e in self.enemies if isinstance(e, Boss)), None) if hasattr(self, 'enemies') else None
        fighter = next(iter(self.fighters), None)
        hover_color = (0, 200, 255)
        default_color = self.button_color
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
            scene.fill((0, 0, 0, 128))
            title_font = pygame.font.Font(None, 72)
            button_font = pygame.font.Font(None, 48)
            title_text = title_font.render("Game Over!", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(config.SCENE_WIDTH // 2, config.SCENE_HEIGHT // 2))
            scene.blit(title_text, title_rect)
            self.restart_button = pygame.Rect(config.SCENE_WIDTH // 2 - 100, config.SCENE_HEIGHT // 2 + 30, 200, 70)
            self.back_button = pygame.Rect(config.SCENE_WIDTH // 2 - 100, config.SCENE_HEIGHT // 2 + 110, 200, 70)
            pygame.draw.rect(scene, hover_color if self.restart_button.collidepoint(mouse_pos) else default_color, self.restart_button)
            pygame.draw.rect(scene, hover_color if self.back_button.collidepoint(mouse_pos) else default_color, self.back_button)
            restart_text = button_font.render("Restart", True, (255, 255, 255))
            back_text = button_font.render("Back to Map", True, (255, 255, 255))
            scene.blit(restart_text, restart_text.get_rect(center=self.restart_button.center))
            scene.blit(back_text, back_text.get_rect(center=self.back_button.center))
        elif self.level_complete:
            scene.fill((0, 0, 0, 128))
            title_font = pygame.font.Font(None, 72)
            button_font = pygame.font.Font(None, 48)
            title_text = title_font.render("Level Complete!", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(config.SCENE_WIDTH // 2, config.SCENE_HEIGHT // 2))
            scene.blit(title_text, title_rect)
            self.next_button = pygame.Rect(config.SCENE_WIDTH // 2 - 100, config.SCENE_HEIGHT // 2 - 50, 200, 70)
            self.restart_button = pygame.Rect(config.SCENE_WIDTH // 2 - 100, config.SCENE_HEIGHT // 2 + 30, 200, 70)
            self.back_button = pygame.Rect(config.SCENE_WIDTH // 2 - 100, config.SCENE_HEIGHT // 2 + 110, 200, 70)
            pygame.draw.rect(scene, hover_color if self.next_button.collidepoint(mouse_pos) else default_color, self.next_button)
            pygame.draw.rect(scene, hover_color if self.restart_button.collidepoint(mouse_pos) else default_color, self.restart_button)
            pygame.draw.rect(scene, hover_color if self.back_button.collidepoint(mouse_pos) else default_color, self.back_button)
            next_text = button_font.render("Next Level", True, (255, 255, 255))
            restart_text = button_font.render("Restart", True, (255, 255, 255))
            back_text = button_font.render("Back to Map", True, (255, 255, 255))
            scene.blit(next_text, next_text.get_rect(center=self.next_button.center))
            scene.blit(restart_text, restart_text.get_rect(center=self.restart_button.center))
            scene.blit(back_text, back_text.get_rect(center=self.back_button.center))
        else:
            if self.win:
                scene.fill((0, 0, 0, 128))
                title_font = pygame.font.Font(None, 72)
                title_text = title_font.render("You win!", True, (255, 255, 255))
                title_rect = title_text.get_rect(center=(config.SCENE_WIDTH // 2, config.SCENE_HEIGHT // 2))
                scene.blit(title_text, title_rect)
            pulsed_back_button = pygame.Rect(self.back_button.x - scale / 2, self.back_button.y - scale / 2, 
                                            self.back_button.width + scale, self.back_button.height + scale)
            pygame.draw.rect(scene, hover_color if pulsed_back_button.collidepoint(mouse_pos) else default_color, pulsed_back_button)
            back_button_text = self.font.render("Back", True, (255, 255, 255))
            pulsed_back_button_text_rect = back_button_text.get_rect(center=pulsed_back_button.center)
            scene.blit(back_button_text, pulsed_back_button_text_rect)