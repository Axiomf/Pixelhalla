import pygame
import config
from src.engine.dynamic_objects import *
from src.engine.platforms import *
from src.engine.states.base_state import BaseState
from src.engine import map1_multi, map4, map_boss, map_jesus, map_levels
import socket
import pickle
import threading
import time

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
        self.game_id = state_manager.game_id
        self.opponents = state_manager.opponents
        self.load_map(state_manager.current_map, state_manager.fighter1_id, state_manager.client_id, state_manager.username)
        # Load map and initialize game
        # map_data = self.load_map(state_manager.current_map, state_manager.fighter1_id, state_manager.username)
        # self.platforms.add(map_data["platforms"])
        # self.fighters.add(map_data["fighters"])
        # self.all_sprites.add(map_data["platforms"], map_data["fighters"])
        # Start a thread to receive server updates
        self.running = True
        self.receive_thread = threading.Thread(target=self.receive_server_updates)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def load_map(self, map_name, fighter1_id, client_id, username):
        """Load map components using a module mapping."""
        map_modules = {
            "map1": "src.engine.map1_multi",
            "map_levels": "src.engine.map_levels",
            "map_jesus": "src.engine.map_jesus",
            "map4": "src.engine.map4",
            "map_boss" : "src.engine.map_boss"
        }
        module_path = map_modules.get(map_name)
        if module_path:
            try:
                if map_name == "map1" and not self.audio_playing:
                    map1_multi.load_map(fighter1_id, client_id, username)
                if map_name == "map_levels" and not self.audio_playing:
                    map_levels.load_map(fighter1_id, client_id, username)
                if map_name == "map_jesus" and not self.audio_playing:
                    map_jesus.load_map(fighter1_id, client_id, username)
                if map_name == "map4" and not self.audio_playing:
                    map4.load_map(fighter1_id, client_id, username)

                mod = __import__(module_path, fromlist=['all_sprites', 'platforms', 'fighters', 'projectiles', 'power_ups', 'draw_background'])
                self.all_sprites = mod.all_sprites
                self.platforms = mod.platforms
                self.fighters = mod.fighters
                self.projectiles = mod.projectiles
                self.power_ups = mod.power_ups
                self.draw_background = mod.draw_background
            except ImportError as e:
                return
                        

    def receive_server_updates(self):
        while self.running:
            try:
                self.client_socket.settimeout(1.0)
                data = self.client_socket.recv(4096)
                if not data:
                    print(f"No data received from server for client {self.client_id}")
                    self.state_manager.error_message = "Lost connection to server"
                    self.running = False
                    if self.client_socket:
                        self.client_socket.close()
                    self.state_manager.client_socket = None
                    self.state_manager.client_id = None
                    self.state_manager.game_id = None
                    self.state_manager.opponents = []
                    self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                    return
                response = pickle.loads(data)
                print(f"Received server update: {response}")
                if not isinstance(response, dict):
                    print(f"Error: Received non-dict response: {response}")
                    self.state_manager.error_message = f"Invalid server response: {response}"
                    self.running = False
                    if self.client_socket:
                        self.client_socket.close()
                    self.state_manager.client_socket = None
                    self.state_manager.client_id = None
                    self.state_manager.game_id = None
                    self.state_manager.opponents = []
                    self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                    return
                request_type = response.get("request_type")
                if request_type == "game_update":
                    self.update_game_state(response)
                elif request_type == "error":
                    self.state_manager.error_message = response.get("message", "Server error")
                    print(f"Server error: {self.state_manager.error_message}")
                    self.running = False
                    if self.client_socket:
                        self.client_socket.close()
                    self.state_manager.client_socket = None
                    self.state_manager.client_id = None
                    self.state_manager.game_id = None
                    self.state_manager.opponents = []
                    self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                else:
                    print(f"Unknown response in PlayingState: {response}")
            except socket.timeout:
                continue
            except pickle.UnpicklingError as e:
                print(f"Unpickling error: {e}")
                self.state_manager.error_message = "Invalid server response"
                self.running = False
                if self.client_socket:
                    self.client_socket.close()
                self.state_manager.client_socket = None
                self.state_manager.client_id = None
                self.state_manager.game_id = None
                self.state_manager.opponents = []
                self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)
            except Exception as e:
                print(f"Error receiving server update: {e}")
                self.state_manager.error_message = f"Lost connection to server: {str(e)}"
                self.running = False
                if self.client_socket:
                    self.client_socket.close()
                self.state_manager.client_socket = None
                self.state_manager.client_id = None
                self.state_manager.game_id = None
                self.state_manager.opponents = []
                self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)

    def update_game_state(self, server_package):
        # Update platforms
        self.platforms.empty()
        for platform_data in server_package.get("platforms", []):
            platform = Platform(platform_data["x"], platform_data["y"], platform_data["width"], platform_data["height"])
            self.platforms.add(platform)
            self.all_sprites.add(platform)
        # Update fighters
        self.fighters.empty()
        for fighter_data in server_package.get("fighters", []):
            fighter = Fighter(fighter_data["fighter_id"], fighter_data["x"], fighter_data["y"],multi_player_mode=True)
            fighter.health = fighter_data.get("health", 100)
            fighter.team = fighter_data.get("team", 0)
            self.fighters.add(fighter)
            self.all_sprites.add(fighter)
        # Update projectiles
        self.projectiles.empty()
        for proj_data in server_package.get("projectiles", []):
            projectile = Projectile(proj_data["x"], proj_data["y"], proj_data["velocity_x"], proj_data["velocity_y"], proj_data["damage"],multi_player_mode=True)
            projectile.team = proj_data.get("team", 0)
            self.projectiles.add(projectile)
            self.all_sprites.add(projectile)
        # Update power-ups
        self.power_ups.empty()
        for power_data in server_package.get("power_ups", []):
            power_up = PowerUp(power_data["x"], power_data["y"], power_data["upgrade_type"], power_data["amount"],multi_player_mode=True)
            self.power_ups.add(power_up)
            self.all_sprites.add(power_up)
        # Check for game end
        team1_alive = any(f.team == 1 and f.health > 0 for f in self.fighters)
        team2_alive = any(f.team == 2 and f.health > 0 for f in self.fighters)
        if not team1_alive or not team2_alive:
            self.win = team1_alive and self.client_id in self.state_manager.opponents[:len(self.state_manager.opponents)//2]
            self.running = False
            self.state_manager.error_message = "You win!" if self.win else "Game over!"
            if self.client_socket:
                self.client_socket.close()
            self.state_manager.client_socket = None
            self.state_manager.client_id = None
            self.state_manager.game_id = None
            self.state_manager.opponents = []
            self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)

    def handle_event(self, event, current_time, scale, current_map, state_manager):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_time - state_manager.last_click_time > config.CLICK_COOLDOWN:
            pulsed_back_button = pygame.Rect(self.back_button.x - scale / 2, self.back_button.y - scale / 2, 
                                            self.back_button.width + scale, self.back_button.height + scale)
            if pulsed_back_button.collidepoint(event.pos):
                state_manager.click_sound.play()
                self.running = False
                if self.client_socket:
                    self.client_socket.close()
                state_manager.client_socket = None
                state_manager.client_id = None
                state_manager.game_id = None
                state_manager.opponents = []
                state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                state_manager.last_click_time = current_time
                pygame.event.clear()
        # Send player inputs to server
        inputs = []
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            inputs.append("left")
        if keys[pygame.K_RIGHT]:
            inputs.append("right")
        if keys[pygame.K_UP]:
            inputs.append("jump")
        if keys[pygame.K_SPACE]:
            inputs.append("shoot")
        if inputs:
            client_package = {
                "request_type": "input",
                "client_id": self.client_id,
                "game_id": self.game_id,
                "fighter_id": self.state_manager.fighter1_id,
                "inputs": inputs,
                "shoots": ["shoot"] if keys[pygame.K_SPACE] else []
            }
            try:
                self.client_socket.send(pickle.dumps(client_package))
                print(f"Sent input to server: {client_package}")
            except Exception as e:
                print(f"Error sending input to server: {e}")
                self.state_manager.error_message = f"Failed to send input: {str(e)}"
                self.running = False
                if self.client_socket:
                    self.client_socket.close()
                self.state_manager.client_socket = None
                self.state_manager.client_id = None
                self.state_manager.game_id = None
                self.state_manager.opponents = []
                self.state_manager.change_state(config.GAME_STATE_MAP_SELECT)

    def update(self, current_time, scale, state_manager):
        self.all_sprites.update()
        # Handle local collisions (optional, since server handles collisions)
        for projectile in self.projectiles:
            hit_fighters = pygame.sprite.spritecollide(projectile, self.fighters, False)
            for fighter in hit_fighters:
                if hasattr(projectile, "team") and fighter.team != projectile.team:
                    fighter.take_damage(projectile.damage)
                    projectile.kill()
        for power in self.power_ups:
            hit_fighters = pygame.sprite.spritecollide(power, self.fighters, False)
            for fighter in hit_fighters:
                fighter.upgrade(power.upgrade_type, power.amount)
                power.kill()
        for sprite in self.fighters:
            sprite.handle_platform_collision(self.platforms)
        for sprite in self.projectiles:
            sprite.handle_platform_collision(self.platforms)
        for sprite in self.power_ups:
            sprite.handle_platform_collision(self.platforms)

    def draw(self, scene, scale, state_manager):
        if not self.draw_background:
            print("YEEESSSSSSSSSSs")
            return
        mouse_pos = pygame.mouse.get_pos()
        default_color = self.button_color
        hover_color = (0, 200, 255)
        self.draw_background()  # Draw map background
        time.sleep(6)
        self.all_sprites.draw(scene)
        if self.level_complete:
            scene.fill((0, 0, 0, 128))
            title_font = pygame.font.Font(None, 72)
            title_text = title_font.render("Level Complete!", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(config.SCENE_WIDTH // 2, config.SCENE_HEIGHT // 2))
            scene.blit(title_text, title_rect)
            self.next_button = pygame.Rect(config.SCENE_WIDTH // 2 - 100, config.SCENE_HEIGHT // 2 - 50, 200, 70)
            self.restart_button = pygame.Rect(config.SCENE_WIDTH // 2 - 100, config.SCENE_HEIGHT // 2 + 30, 200, 70)
            self.back_button = pygame.Rect(config.SCENE_WIDTH // 2 - 100, config.SCENE_HEIGHT // 2 + 110, 200, 70)
            pygame.draw.rect(scene, hover_color if self.next_button.collidepoint(mouse_pos) else default_color, self.next_button)
            pygame.draw.rect(scene, hover_color if self.restart_button.collidepoint(mouse_pos) else default_color, self.restart_button)
            pygame.draw.rect(scene, hover_color if self.back_button.collidepoint(mouse_pos) else default_color, self.back_button)
            next_text = self.font.render("Next Level", True, (255, 255, 255))
            restart_text = self.font.render("Restart", True, (255, 255, 255))
            back_text = self.font.render("Back to Map", True, (255, 255, 255))
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