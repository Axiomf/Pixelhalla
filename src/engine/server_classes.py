# server_classes.py
import pygame
from src.engine.dynamic_objects import *
from src.engine.platforms import *
from .base import CustomGroup
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
    def __init__(self, id, mode, ID1, ID2, ID3=None, ID4=None, world=None):
        self.game_clients = [ID1, ID2] if mode == "1vs1" else [ID1, ID2, ID3, ID4]
        self.game_id = id

        self.platforms = CustomGroup()
        self.fighters = CustomGroup()
        self.projectiles = CustomGroup()
        self.power_ups = CustomGroup()
        self.sounds = []

        self.game_updates = []
        self.mode = mode
        self.finished = False

        # print("Creating platforms...")
        platform1 = Platform(0, config.SCENE_HEIGHT - 20, 1200, 20, color=(139, 140, 78))
        moving_platform = MovingPlatform(config.SCENE_WIDTH/8, config.SCENE_HEIGHT/4, config.SCENE_WIDTH/4, 10, range_x=500, range_y=0, speed=1, color=(139, 120, 78))
        self.platforms.add(platform1, moving_platform)
        # print(f"Platforms created: {len(self.platforms)}")

        # print("Creating fighters...")
        fighter1 = Fighter(
            x=700, 
            y=config.SCENE_HEIGHT*3/5 - 70, 
            width=32, 
            height=32, 
            platforms=self.platforms,
            controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
            id=ID1, 
            team=1, 
            color=(200, 120, 78),
            multiplayer=True
        )
        fighter2 = Fighter(
            x=450, 
            y=config.SCENE_HEIGHT*3/5 - 70, 
            width=32, 
            height=32, 
            platforms=self.platforms,
            controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
            id=ID2, 
            team=2, 
            color=(200, 120, 120),
            multiplayer=True
        )
        self.fighters.add(fighter1, fighter2)
        # print(f"Fighters created: {len(self.fighters)}")

        if mode == "1vs1":
            self.team1_ids = [ID1]
            self.team2_ids = [ID2]
        else:
            self.team1_ids = [ID1, ID2]
            self.team2_ids = [ID3, ID4]

    def handle_collisions(self):
        for projectile in self.projectiles:
            hit_fighters = pygame.sprite.spritecollide(projectile, self.fighters, False)
            for fighter in hit_fighters:
                if hasattr(projectile, "team") and fighter.team != projectile.team:
                    fighter.take_damage(projectile.damage)
                    projectile.kill()
                    self.sounds.append("blood")
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

    def check_game_finished(self):
        alive_ids = set(getattr(f, "fighter_id", None) for f in self.fighters)
        team1_alive = any(fid in alive_ids for fid in self.team1_ids if fid is not None)
        team2_alive = any(fid in alive_ids for fid in self.team2_ids if fid is not None)
        if not team1_alive or not team2_alive:
            self.finished = True

    def update(self):
        if self.game_updates:
            for client_package in self.game_updates:
                # print(f"Processing client_package: {client_package}")
                for fighter in self.fighters:
                    if client_package["client_id"] == fighter.fighter_id:
                        fighter.client_input.extend(client_package["inputs"])
                        # print(f"Inputs for fighter {fighter.fighter_id}: {client_package['inputs']}")
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