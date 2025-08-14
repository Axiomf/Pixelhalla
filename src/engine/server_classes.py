# server_classes.py
import pygame
from src.engine.dynamic_objects import *
from src.engine.platforms import *
from .base import CustomGroup
from src.engine.server_helper import generate_unique_client_id, broadcast, send_to_client,serialize_fighters, serialize_projectiles, serialize_power_ups, serialize_platforms
import config

class Client:
    def __init__(self, client_id, conn, state="menu"):
        self.client_id = client_id
        self.conn = conn
        self.state = state
        self.connected_lobby_id = ""
        self.connected_game_id = ""
        self.is_host = False
        self.hero = None
        self.game_mode = None

class Lobby:
    def __init__(self, lobby_id, host_client_id, game_mode):
        self.lobby_id = lobby_id
        self.host_client_id = host_client_id
        self.members = [host_client_id]
        self.game_mode = game_mode
        self.state = "waiting"

    def add_member(self, client_id):
        if client_id not in self.members and self.state == "waiting":
            self.members.append(client_id)
            self.update_state()

    def remove_member(self, client_id):
        if client_id in self.members:
            self.members.remove(client_id)
            self.update_state()

    def update_state(self):
        required = 2 if self.game_mode == "1vs1" else 4
        if len(self.members) >= required:
            self.state = "full"
        else:
            self.state = "waiting"

    def is_host(self, client_id):
        return self.host_client_id == client_id

class Game:
    def __init__(self, id, mode, ID1, ID2, ID3=None, ID4=None, world=None, usernames=None):
        self.game_clients = [ID1, ID2] if mode == "1vs1" else [ID1, ID2, ID3, ID4]
        self.game_id = id
        self.usernames = usernames
        print("0000000000000000000000000000000000000000000000000000")
        print(usernames)
        self.platforms = CustomGroup()
        self.fighters = CustomGroup()
        self.projectiles = CustomGroup()
        self.power_ups = CustomGroup()
        self.sounds = []

        self.game_updates = []
        self.mode = mode
        self.finished = False
        self.winning_team = None

        platform1 = Platform(0, config.SCENE_HEIGHT - 20, 1200, 20, color=(139, 140, 78))
        moving_platform = MovingPlatform(config.SCENE_WIDTH/8, config.SCENE_HEIGHT/4, config.SCENE_WIDTH/4, 10, range_x=500, range_y=0, speed=1, color=(139, 120, 78))
        self.platforms.add(platform1, moving_platform)

        fighter1 = Fighter(
            x=700, 
            y=config.SCENE_HEIGHT*3/5 - 70, 
            width=32, 
            height=32, health=100,
            platforms=self.platforms,
            controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
            id=ID1, 
            team=1, 
            color=(200, 120, 78),
            multi_player_mode=True
        )
        fighter2 = Fighter(
            x=450, 
            y=config.SCENE_HEIGHT*3/5 - 70, 
            width=32, 
            height=32, health=100,
            platforms=self.platforms,
            controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
            id=ID2, 
            team=2, 
            color=(200, 120, 120),
            multi_player_mode=True
        )
        if mode == "1vs1":
            self.fighters.add(fighter1, fighter2)
        elif mode == "2vs2":
            fighter3 = Fighter(
            x=800, 
            y=config.SCENE_HEIGHT*3/5 - 70, 
            width=32, 
            height=32, health=100,
            platforms=self.platforms,
            controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
            id=ID3, 
            team=1, 
            color=(200, 120, 78),
            multi_player_mode=True
            )
            fighter4 = Fighter(
                x=350, 
                y=config.SCENE_HEIGHT*3/5 - 70, 
                width=32, 
                height=32, health=100,
                platforms=self.platforms,
                controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                id=ID4, 
                team=2, 
                color=(200, 120, 120),
                multi_player_mode=True
            )
            self.fighters.add(fighter1, fighter2, fighter3, fighter4)

        if mode == "1vs1":
            self.team1_ids = [ID1]
            self.team2_ids = [ID2]
        else:
            self.team1_ids = [ID1, ID3]
            self.team2_ids = [ID2, ID4]

    def handle_collisions(self):
        for projectile in self.projectiles:
            hit_fighters = pygame.sprite.spritecollide(projectile, self.fighters, False)
            for fighter in hit_fighters:
                if hasattr(projectile, "team") and fighter.team != projectile.team:
                    fighter.take_damage(projectile.damage)
                    print(fighter.health)
                    projectile.kill()
                    self.sounds.append("blood")
        for power in self.power_ups:
            hit_fighters = pygame.sprite.spritecollide(power, self.fighters, False)
            for fighter in hit_fighters:
                fighter.upgrade(power.upgrade_type, power.amount)
                self.sounds.append("power_up")
                power.kill()
        for sprite in self.fighters:
            sprite.handle_platform_collision(self.platforms)
        for sprite in self.projectiles:
            sprite.handle_platform_collision(self.platforms)
        for sprite in self.power_ups:
            sprite.handle_platform_collision(self.platforms)

    def check_game_finished(self):
        alive_ids = set(getattr(f, "fighter_id", None) for f in self.fighters)
        team1_alive = any(fid in alive_ids for fid in self.team1_ids if fid is not None)
        team2_alive = any(fid in alive_ids for fid in self.team2_ids if fid is not None)
        if not team1_alive or not team2_alive:
            print("Game finished everything except animations should be freezing")
            self.finished = True
            if team1_alive:
                self.winning_team = 1
            elif team2_alive:
                self.winning_team = 2

    def handle_client_disconnect(self, client_id):
        print(f"Handling disconnection of client {client_id} in game {self.game_id}")
        if client_id in self.game_clients:
            self.game_clients.remove(client_id)
            # Remove fighter associated with this client
            for fighter in self.fighters:
                if fighter.fighter_id == client_id:
                    fighter.kill()
                    break
            # Update team lists
            if client_id in self.team1_ids:
                self.team1_ids.remove(client_id)
            elif client_id in self.team2_ids:
                self.team2_ids.remove(client_id)
            # Check if game should end due to disconnection
            self.check_game_finished()
            # Notify remaining clients
            if not self.finished:
                from server_side import all_clients, clients_lock
                with clients_lock:
                    broadcast({"request_type": "client_disconnected", "client_id": client_id}, self.game_clients, all_clients)

    def update(self):
        if self.game_updates:
            for client_package in self.game_updates:
                for fighter in self.fighters:
                    if client_package["client_id"] == fighter.fighter_id:
                        fighter.client_input.extend(client_package["inputs"])
                        if client_package["shoots"]:
                            for shot in client_package["shoots"]:
                                projectile = fighter.shoot()
                                self.projectiles.add(projectile)
            self.game_updates.clear()
        self.fighters.update()
        self.projectiles.update()
        self.power_ups.update()
        self.platforms.update()
        self.handle_collisions()
        self.check_game_finished()