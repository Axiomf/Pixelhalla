# it handles server requsts, clients add requests and server updates the game opbjects and sends them to all clients
from _thread import * # For threading, to handle multiple clients at once
from src.engine.dynamic_objects import *
import pickle  # To serialize Python objects to send over the network
import pygame  # (if not already imported for sprite groups)
import time  # added for game world update timing
import uuid  # added for generating unique random client IDs
from src.config.server_config import create_server_socket  # New import for server configuration

# New Client class to encapsulate connection and attributes
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

class Game: # need a broadcaster for 
    def __init__(self,id, mode, ID1, ID2, ID3 = None, ID4 = None):# we assume player_3 and player_4 are on the same team
        """  """
        self.ID = id
        self.game_clients = [ID1, ID2, ID3, ID4] # IDs of connected clients
        self.platforms = pygame.sprite.Group()
        self.fighters = pygame.sprite.Group() # handle 2 vs 2 later
        self.projectiles = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()

        self.game_updates = [] # input packages
        self.mode = mode
        
        # Moved server_package inside Game
        
        # ...existing code...

    def handle_collisions(self):
        # Handle collisions for projectiles with fighters
        for projectile in self.projectiles:
            hit_fighters = pygame.sprite.spritecollide(projectile, self.fighters, False)
            for fighter in hit_fighters:
                if hasattr(projectile, "owner") and fighter != projectile.owner:
                    fighter.take_damage(projectile.damage)
                    projectile.kill()
        # Handle collisions for power-ups with fighters
        for power in self.power_ups:
            hit_fighters = pygame.sprite.spritecollide(power, self.fighters, False)
            for fighter in hit_fighters:
                fighter.upgrade(power.upgrade_type, power.amount)
                power.kill()
        # Handle platform collisions
        for sprite in self.fighters:
            sprite.handle_platform_collision(self.platforms)
        for sprite in self.projectiles:
            sprite.handle_platform_collision(self.platforms)
        for sprite in self.power_ups:
            sprite.handle_platform_collision(self.platforms)

    def update(self):
        """ it handles input queues, then collision and updates the world of the game  """
        while True:
            if self.game_updates:
                for client_package in self.game_updates:
                    for fighter in self.fighters:
                        if client_package["fighter_id"] == fighter:
                            fighter.client_input.extend(client_package["inputs"])
                            if client_package["shoots"]:
                                for shot in client_package["shoots"]:
                                    projectile = fighter.shoot()
                                    self.projectiles.add(projectile)
                self.game_updates.clear()
            # Update game objects in the current server_package and handle collisions
            self.fighters.update()
            self.projectiles.update()
            self.power_ups.update()
            self.platforms.update()

            self.handle_collisions()
            
            #broadcast(self.server_package) moved to thread
            #time.sleep(0.05) moved to thread

s = create_server_socket()



""" types of client requests:  find_random_game, join_lobby, make_lobby, start_the_game_as_host 

client_package = {
    "room_id" : "1313132",
    "client_id": "12345678",
    "request_type" : "find",    
    "state": "lobby",
    "shoots" " [] ,
    "inputs" : [] }

server_package = {
    "request_type": "game_update",
    "platforms": platforms,
    "fighters": fighters,
    "projectiles": projectiles, 
    "power_ups": power_ups, 
    "sounds": []
}
"""

all_clients = []  # list of Client objects
all_lobbies = []  # connected clients and created lobbies 


pending_requests = []  # new global list for client requests that are not input or shoot (client_package)
games = [] # to track all the current playing games
waiting_clients = {} 
def broadcast(server_package, ):
    """Sends a package to all connected clients."""
    disconnected_clients = []
    for client in all_clients:
        try:
            client.conn.sendall(pickle.dumps(server_package))
        except:
            disconnected_clients.append(client)
    # Remove disconnected clients
    for client in disconnected_clients:
        all_clients.remove(client)

def send_to_client(server_package, client_id):
    """Sends a package to a specific client identified by client_id."""
    target = None
    for client in all_clients:
        if client.client_id == client_id:
            target = client
            break
    if target is None:
        print(f"Client {client_id} not found.")
        return
    try:
        target.conn.sendall(pickle.dumps(server_package))
    except Exception as e:
        print(f"Error sending to client {client_id}: {e}")
        
def threaded_client(conn):
    global pending_requests, games, waiting_clients
    # Create new Client instance and add to the clients list
    client_id = generate_unique_client_id()  # use the new function for unique ID generation

    client = Client(client_id, conn)
    all_clients.append(client)
    conn.send(pickle.dumps(client_id)) # sends clients ID as a first time massage
    
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            client_package = pickle.loads(data)
            request_type = client_package["request_type"] # always have a type of request in client packages

            if request_type == "input":  # Append the client's package to game_updates if it is input.  
                for game in games:
                    if game.ID == client.connected_game_id:
                        game.game_updates.append(client_package)
            
            elif request_type == "find_random_game": # incomplete
                waiting_clients[client_package["client_id"]] = client_package["room_id"]
                
            
            elif request_type == "join_lobby":# incomplete
                if client.connected_lobby_id == "":
                    all_lobbies.append(client_package["client_id"])


            elif request_type == "make_lobby":
                pass

            elif request_type == "start_the_game_as_host":
                pass






            else:
                pending_requests.append((client_id, client_package)) # Append to the global request list.

        except:
            break

    print("Lost connection")
    # Remove client from the clients list
    for client in all_clients:
        if client.client_id == client_id:
            all_clients.remove(client)
            break
    conn.close()

def threaded_game(game):# it sees only the game_updates then Processes the pending game changes then sends it to all clients, input and shooting
    while True:
        game.update()
        broadcast(server_package)
        time.sleep(0.05)  # small delay to reduce CPU usage

def threaded_handle_general_request(): # what are requests other than input?
    global pending_requests, server_package
    while True:
        if pending_requests:
            for cli_pack in pending_requests: # Process each client's inputs/requests.
                if cli_pack["request_type"] == "input":
                    pass

                
                # For example, update server_package["fighters"] based on client_package data.
                # ...processing logic for player_id and client_package...
                pass  # Replace with actual game logic updates.
            pending_requests.clear()
        # Update game objects in the current server_package
        server_package["fighters"].update()
        server_package["projectiles"].update()
        server_package["power_ups"].update()
        server_package["platforms"].update()  # In case platforms are dynamic
        # Process collisions similar to playing.py
        broadcast(server_package)
        time.sleep(0.05)  # small delay to reduce CPU usage

def generate_unique_client_id():
    # Generate a random 8-character ID and ensure it is unique among connected clients.
    client_id = str(uuid.uuid4())[:8]
    existing_ids = [client.client_id for client in all_clients]
    while client_id in existing_ids:
        client_id = str(uuid.uuid4())[:8]
    return client_id

def threaded_handle_waiting_clients():
    global waiting_clients



start_new_thread(threaded_game, ())# 


while True:
    conn, addr = s.accept()# The accept() method blocks until a client connects. It returns a new connection object (conn) and the client's address (addr).
    print("Connected to:", addr)
    
    start_new_thread(threaded_client, (conn)) # When a client connects, we start a new thread for them with a new generated ID. This allows the server to handle multiple clients simultaneously without blocking




