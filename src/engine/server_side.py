# it handles server requsts, clients add requests and server updates the game opbjects and sends them to all clients
import socket
from _thread import * # For threading, to handle multiple clients at once
from src.engine.dynamic_objects import *
import pickle  # To serialize Python objects to send over the network
import pygame  # (if not already imported for sprite groups)
import time  # added for game world update timing
import uuid  # added for generating unique random client IDs

server = "127.0.0.1"  # The IP address the server will run on (localhost)
port = 5555          # The port the server will listen on
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# AF_INET specifies we are using IPv4 # SOCK_STREAM specifies we are using TCP (a reliable connection-based protocol)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)# This line allows us to reuse the address when you restart the server quickly. It prevents the "address already in use" error
try:# Bind the socket to the IP and port
    s.bind((server, port))
except socket.error as e:
    # We also improve the error message here to be more helpful.
    print(f"Server could not bind to {server}:{port}, error: {e}")
    exit() # Exit the program if we can't bind.
s.listen(2)# Start listening for incoming connections. The number (2) is the max number of queued connections.
print("Waiting for a connection, Server Started")
###################################################################################################################

platforms = pygame.sprite.Group()
fighters = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
power_ups = pygame.sprite.Group()


""" client_package = {"fighter_id": n-1,
                      "request_type" : "find",    
                      "state": "lobby",
                      "shoots" " [] ,
                      "inputs" : [] }
"""



server_package = {
    "request_type": "game_update",
    "platforms": platforms,
    "fighters": fighters,
    "projectiles": projectiles, 
    "power_ups": power_ups, 
    "sounds": []
}

clients = {}  
pending_requests = []  # new global list for client requests that are not input or shoot (client_package)
game_updates = [] # Append the input and shoot request to this 

def broadcast(server_package):
    """Sends the updated game state server_package to all connected clients."""
    disconnected_ids = []
    for client_id, client in list(clients.items()):
        try:
            client.sendall(pickle.dumps(server_package))
        except:
            disconnected_ids.append(client_id)
    # Remove disconnected clients
    for client_id in disconnected_ids:
        if client_id in clients:
            del clients[client_id]

def send_to_client(server_package, client_id):
    """Sends a package to a specific client identified by client_id."""
    client = clients.get(client_id)
    if client is None:
        print(f"Client {client_id} not found.")
        return
    try:
        client.sendall(pickle.dumps(server_package))
    except Exception as e:
        print(f"Error sending to client {client_id}: {e}")

def handle_collisions():
    global server_package
    
    # Handle collisions for projectiles with fighters
    for projectile in server_package["projectiles"]:
        hit_fighters = pygame.sprite.spritecollide(projectile, server_package["fighters"], False)
        for fighter in hit_fighters:
            # Ensure that projectiles do not hit their owners
            if hasattr(projectile, "owner") and fighter != projectile.owner:
                fighter.take_damage(projectile.damage)
                projectile.kill()
    # Handle collisions for power-ups with fighters
    for power in server_package["power_ups"]:
        hit_fighters = pygame.sprite.spritecollide(power, server_package["fighters"], False)
        for fighter in hit_fighters:
            fighter.upgrade(power.upgrade_type, power.amount)
            power.kill()
    # handle_platform_collision
    for sprite in server_package["fighters"]:
        sprite.handle_platform_collision(server_package["platforms"])
    for sprite in server_package["projectiles"]:
        sprite.handle_platform_collision(server_package["platforms"])
    for sprite in server_package["power_ups"]:
        sprite.handle_platform_collision(server_package["platforms"])

def threaded_client(conn, player_id):
    global server_package, pending_requests, game_updates
    # Add connection to dictionary with its ID
    clients[player_id] = conn
    conn.send(pickle.dumps(server_package)) # we need to send a custom first-time package, change this later.
    
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            client_package = pickle.loads(data)

            if client_package["request_type"] == "input":  # Append the client's package to game_updates if it is input.  
                game_updates.append(client_package)
            else:
                pending_requests.append((player_id, client_package)) # Append to the global request list.

        except:
            break

    print("Lost connection")
    if player_id in clients:
        del clients[player_id]
    conn.close()


def threaded_update_game_world():# it sees only the game_updates then Processes the pending game changes then sends it to all clients, input and shooting
    global game_updates, server_package
    while True:
        if game_updates:
            for client_package in game_updates: # select a patch
                for fighter in server_package["fighters"]: 
                    if client_package["fighter_id"] == fighter: # find the fighter corresponding to the given package
                        fighter.client_input.extend(client_package["inputs"])
                        if client_package["shoots"]: # if it shoots then handle it
                            for shots in client_package["shoots"]:
                                projectile = fighter.shoot()
                                server_package["projectiles"].add(projectile)

            game_updates.clear()
        # Update game objects in the current server_package and handle collision
        server_package["fighters"].update()
        server_package["projectiles"].update()
        server_package["power_ups"].update()
        server_package["platforms"].update()  # In case platforms are dynamic
        handle_collisions()

        broadcast(server_package)
        time.sleep(0.05)  # small delay to reduce CPU usage

def threaded_handle_general_request(): 
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
        handle_collisions()        
        broadcast(server_package)
        time.sleep(0.05)  # small delay to reduce CPU usage

def generate_unique_client_id():
    # Generate a random 8-character ID and ensure it is unique among connected clients.
    client_id = str(uuid.uuid4())[:8]
    while client_id in clients:
        client_id = str(uuid.uuid4())[:8]
    return client_id

# Start the game world updater in its own thread.
start_new_thread(threaded_update_game_world, ())


while True:
    conn, addr = s.accept()# The accept() method blocks until a client connects. It returns a new connection object (conn) and the client's address (addr).
    print("Connected to:", addr)
    
    client_id = generate_unique_client_id()  # use the new function for unique ID generation
    start_new_thread(threaded_client, (conn, client_id )) # When a client connects, we start a new thread for them with a new generated ID. This allows the server to handle multiple clients simultaneously without blocking




