# it handles server requsts, clients add requests and server updates the game opbjects and sends them to all clients
import socket
from _thread import * # For threading, to handle multiple clients at once
from src.engine.dynamic_objects import *
import pickle  # To serialize Python objects to send over the network
import pygame  # (if not already imported for sprite groups)
import time  # added for game world update timing

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


""" client_package = {"state": "lobby",
                      "request" : "find",    
                      "fighter_id": n-1,  
                      "inputs" : [] }
"""

package = {
    "platforms": platforms,
    "fighters": fighters,
    "projectiles": projectiles, 
    "power_ups": power_ups, 
    "sounds": []
}

# Global list for connections
clients = []
incoming_requests = []  # new global list for client inputs and requests

def broadcast(package):
    """Sends the updated game state package to all connected clients."""
    disconnected_clients = []
    for client in clients:
        try:
            client.sendall(pickle.dumps(package))
        except:
            clients.remove(client)
            disconnected_clients.append(client)
    # remove them sepratly to prevent error
    for client in disconnected_clients:
        if client in clients:
            clients.remove(client)

def handle_collisions():
    global package
    
    # Handle collisions for projectiles with fighters
    for projectile in package["projectiles"]:
        hit_fighters = pygame.sprite.spritecollide(projectile, package["fighters"], False)
        for fighter in hit_fighters:
            # Ensure that projectiles do not hit their owners
            if hasattr(projectile, "owner") and fighter != projectile.owner:
                fighter.take_damage(projectile.damage)
                projectile.kill()
    # Handle collisions for power-ups with fighters
    for power in package["power_ups"]:
        hit_fighters = pygame.sprite.spritecollide(power, package["fighters"], False)
        for fighter in hit_fighters:
            fighter.upgrade(power.upgrade_type, power.amount)
            power.kill()
    # handle_platform_collision
    for sprite in package["fighters"]:
        sprite.handle_platform_collision(package["platforms"])
    for sprite in package["projectiles"]:
        sprite.handle_platform_collision(package["platforms"])
    for sprite in package["power_ups"]:
        sprite.handle_platform_collision(package["platforms"])

def update_game_world():
    global incoming_requests, package
    while True:
        if incoming_requests:
            for player_id, client_package in incoming_requests:
                # Process each client's inputs/requests.
                # For example, update package["fighters"] based on client_package data.
                # ...processing logic for player_id and client_package...
                pass  # Replace with actual game logic updates.
            incoming_requests.clear()
        # Update game objects in the current package
        package["fighters"].update()
        package["projectiles"].update()
        package["power_ups"].update()
        package["platforms"].update()  # In case platforms are dynamic
        # Process collisions similar to playing.py
        handle_collisions()        
        broadcast(package)
        time.sleep(0.05)  # small delay to reduce CPU usage

def threaded_client(conn, player_id):
    global package, incoming_requests
    # Add connection to list
    clients.append(conn)
    conn.send(pickle.dumps(package))
    
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            client_package = pickle.loads(data)
            # Append the client's package along with its ID to the global request list.
            incoming_requests.append((player_id, client_package))
            # Removed direct package updates from here.
        except:
            break

    print("Lost connection")
    if conn in clients:
        clients.remove(conn)
    conn.close()

# Start the game world updater in its own thread.
start_new_thread(update_game_world, ())

current_player = 0
while True:
    conn, addr = s.accept()# The accept() method blocks until a client connects. It returns a new connection object (conn) and the client's address (addr).
    print("Connected to:", addr)
    start_new_thread(threaded_client, (conn, current_player)) # When a client connects, we start a new thread for them. This allows the server to handle multiple clients simultaneously without blocking.
    current_player += 1 # Increment for the next player


