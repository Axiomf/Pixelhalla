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
previous_game_state = None              # New global for interpolation
last_update_time = 0                    # Timestamp of last update
network_interval = 0.1                  # Estimated network update interval (in seconds)
shared_lock = threading.Lock()

def threaded_receive_update(sock):
    global game_state, previous_game_state, last_update_time
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("Disconnected from server.")
                break
            client_package = pickle.loads(data)
            if client_package.get("request_type") == "game_update":
                with shared_lock:
                    previous_game_state = game_state  # store the old state
                    game_state = client_package.get("game_world")
                    last_update_time = time.time()   # update timestamp
            else:
                pass
            #print("Server message:", client_package)

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
    Draws the interpolated game state based on previous and current state.
    """
    screen.fill((0, 0, 0))
    now = time.time()
    with shared_lock:
        current_state = game_state
        prev_state = previous_game_state
        last_time = last_update_time
    if current_state:
        # Calculate interpolation factor
        alpha = 1.0
        if prev_state and last_time:
            alpha = min(1, (now - last_time) / network_interval)
        for key in ['platforms', 'fighters', 'projectiles', 'power_ups']:
            current_group = current_state.get(key, [])
            # Check if we have a previous state with the same key
            if prev_state and len(prev_state.get(key, [])) == len(current_group):
                prev_group = prev_state.get(key, [])
                for idx, obj in enumerate(current_group):
                    curr_rect = obj.get("rect")
                    prev_rect = prev_group[idx].get("rect")
                    if curr_rect and prev_rect:
                        interp_rect = tuple(int(prev_rect[i] + alpha * (curr_rect[i] - prev_rect[i])) for i in range(4))
                    else:
                        interp_rect = curr_rect
                    color = obj.get("color", (255, 255, 255))
                    pygame.draw.rect(screen, color, interp_rect)
            else:
                for obj in current_group:
                    rect = obj.get("rect")
                    color = obj.get("color", (255, 255, 255))
                    pygame.draw.rect(screen, color, rect)
    pygame.display.flip()

def send_request_to_server(client_package):
    global running
    """
    Sends a request (client_package) to the server using the given connection.
    """
    try:
        conn.sendall(pickle.dumps(client_package))
        #print(f"Sent: {client_package}")
    except Exception as e:
        print("Error sending data:", e)
        running = False
        return False
    return True


client_first_package = {
            "client_id": client_id,
            "request_type": "find_random_game",
            "game_mode": "1vs1",
            "inputs": [],
            "shoots": []
        }
send_request_to_server(client_first_package)

running = True
while running:
    inputs = []  # list to capture keyboard events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            inputs.append(event.key)

            
            if event.key - 48 == 1: # "find_random_game"
                print(f" I pressed: 1  {event.key==49}") # ++ 48
            elif event.key - 48 == 2:
                print(2)
            elif event.key - 48 == 3:
                print(3)
            elif event.key - 48 == 4:
                print(4)



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
