import socket
import pickle
import threading
import time
import pygame  # added import
from src.engine.dynamic_objects import *

# transformation general templates
"""  
example of full packages:

client_package = {
    "room_id" : "12345678"
    "client_id": "12345678"
    "game_mode": "1vs1" or "2vs2"
    "request_type" : "input" or "find_random_game" or "join_lobby" or "make_lobby" or "start_the_game_as_host"
    "state": "menu" or "waiting" or "lobby" or "in_game"
    
    "shoots" " [] 
    "inputs" : [] 
}

server_package = {
    "request_type": "game_update", "first_time"

    "game_world":
        "platforms": platforms,
        "fighters": fighters,
        "projectiles": projectiles, 
        "power_ups": power_ups, 
        "sounds": []
}
"""

# Global game state variable to store server updates
game_state = None
shared_lock = threading.Lock()

def threaded_receive_update(sock):
    global game_state
    
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("Disconnected from server.")
                break
            message = pickle.loads(data)
            # Update game state if message is a game update, else print it.
            if message.get("request_type") == "game_update":
                with shared_lock:
                    game_state = message.get("game_world")
            else:
                print("Server message:", message)

        except Exception as e:
            print("Error receiving message:", e)
            break

# Inlined main function code at global scope.
pygame.init()  # initialize pygame
screen = pygame.display.set_mode((1200,600))
pygame.display.set_caption("Pixelhala Client")
clock = pygame.time.Clock()

server_ip = "127.0.0.1"
server_port = 5555  # ensure this matches your server configuration
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    conn.connect((server_ip, server_port))
except Exception as e:
    print("Could not connect to the server:", e)
    exit()

try:
    client_id_data = conn.recv(4096)
    client_id = pickle.loads(client_id_data)
    print("Connected to server. Your client ID is:", client_id)
except Exception as e:
    print("Error receiving client ID:", e)
    conn.close()
    exit()

# Start thread to listen for server messages
recv_thread = threading.Thread(target=threaded_receive_update, args=(conn,))
recv_thread.daemon = True
recv_thread.start()

# Add a new function for drawing the game state.
def draw_game_state(screen):
    """
    "game_world":
        "platforms": platforms,
        "fighters": fighters,
        "projectiles": projectiles, 
        "power_ups": power_ups, 
        "sounds": []
    """
    screen.fill((0, 0, 0))
    with shared_lock:
        if game_state:
            for key in ['platforms', 'fighters', 'projectiles', 'power_ups']:
                group = game_state.get(key, [])
                # If group has a .draw method (like pygame.sprite.Group), use it
                if hasattr(group, 'draw'):
                    group.draw(screen)
                else:
                    for obj in group:
                        if hasattr(obj, 'draw'):
                            obj.draw(screen)
    pygame.display.flip()

def send_request_to_server(client_package):
    global running
    """
    Sends a request (client_package) to the server using the given connection.
    """
    try:
        conn.sendall(pickle.dumps(client_package))
    except Exception as e:
        print("Error sending data:", e)
        running = False
        return False
    return True

running = True
while running:
    inputs = []  # list to capture keyboard events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            inputs.append(pygame.key.name(event.key))
            print(event.key==49) # ++ 48
            if event.key - 48 == 1: # "find_random_game"
                client_package = {
            "client_id": client_id,
            "request_type": "find_random_game",
            "game_mode": "1vs1",
            "inputs": inputs,
            "shoots": []
        }
                send_request_to_server(client_package)
            elif event.key - 48 == 2:
                print(2)
            elif event.key - 48 == 3:
                print(3)
            elif event.key - 48 == 4:
                print(4)



            print(event.key)
    if inputs:
        client_package = {
            "client_id": client_id,
            "request_type": "input",
            "game_mode": "1vs1",
            "inputs": inputs,
            "shoots": []
        }
        send_request_to_server(client_package)
    
    draw_game_state(screen)  # Call the new drawing function
    clock.tick(60)

pygame.quit()
conn.close()
