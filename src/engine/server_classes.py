import pygame
from src.engine.dynamic_objects import *
from .base import CustomGroup
class Client:
    def __init__(self, client_id, conn, state="menu"):
        self.client_id = client_id
        self.conn = conn
        self.state = state

        self.connected_lobby_id = ""
        self.connected_game_id = ""
        self.is_host = False
        self.hero = None # add later
        self.game_mode = None # add later

class Lobby:
    def __init__(self, lobby_id, host_client_id, game_mode):
        self.lobby_id = lobby_id
        self.host_client_id = host_client_id
        self.members = [host_client_id]  # List of client IDs in the lobby
        self.game_mode = game_mode
        self.state = "waiting"  # could be "waiting", "full", "started"

    def add_member(self, client_id):
        if client_id not in self.members:
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
    def __init__(self,id, mode, ID1, ID2, ID3 = None, ID4 = None, world = None): # "world" has info about fighters
        self.game_clients = [ID1, ID2] if mode == "1vs1" else [ID1, ID2, ID3, ID4]
        self.game_id = id
        self.platforms = CustomGroup()
        self.fighters = CustomGroup()
        self.projectiles = CustomGroup()
        self.power_ups = CustomGroup()
        self.game_updates = []
        self.mode = mode
        self.finished = False
        
        # Team assignment: team1 and team2 are lists of fighter IDs
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
                if (hasattr(projectile, "team") and fighter.team != projectile.team) :
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

    def check_game_finished(self):
        # Get current fighter IDs in the group
        alive_ids = set(getattr(f, "fighter_id", None) for f in self.fighters)
        team1_alive = any(fid in alive_ids for fid in self.team1_ids if fid is not None)
        team2_alive = any(fid in alive_ids for fid in self.team2_ids if fid is not None)
        
        if not team1_alive or not team2_alive:
            self.finished = True

    def update(self):
        if self.game_updates:
            for client_package in self.game_updates:
                for fighter in self.fighters:
                    if client_package["fighter_id"] == fighter.fighter_id:
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