# slut_client.py

import socket
import pickle
import threading
import time
import pygame
from src.config.server_config import SERVER_IP, SERVER_PORT
from src.engine.dynamic_objects import *
from src.engine.animation_loader import load_animations_Arcane_Archer
from src.engine.client_media import (
    draw_game_state, draw_game_over, draw_lobby_screen, 
    draw_menu_screen, draw_waiting_screen
)
"""  
example of full packages:

objets_serialized:
        "rect": (sprite.rect.x, sprite.rect.y, sprite.rect.width, sprite.rect.height),
        "state": getattr(sprite, "state", "idle"),
        "id": getattr(sprite, "fighter_id", "id not given"),
        "is_doing" : getattr(sprite, "is_doing", "is_doing not given"), # complete cycle animations like: death, shoot, attack, hurt 
        "facing_right": getattr(sprite, "facing_right", True)

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
    "request_type": "game_update", "first_time", "report"
    "report" : "sfsfsdfs"
    "game_world":
        "platforms": platforms,
        "fighters": fighters,
        "projectiles": projectiles, 
        "power_ups": power_ups, 
        "sounds": []
}
"""

# --- Pygame and Display Setup ---
pygame.init()
screen = pygame.display.set_mode((1200, 600))
pygame.display.set_caption("Pixelhala Client")
clock = pygame.time.Clock()

# --- Global State and Configuration ---
# Input state
key_pressed = {
    pygame.K_a: False, pygame.K_d: False, pygame.K_w: False, pygame.K_SPACE: False
}

# Game state
game_state = None
previous_game_state = None
last_update_time = 0
network_interval = 0.1  # How often we expect updates from server (in seconds)
shared_lock = threading.Lock()
client_anim_states = {}  # key: object id, value: dict with current_animation, current_frame, last_update

# Client/Game status
client_state = "menu"  # "menu", "lobby", "in_game", "searching", "waiting"
game_over = False
winning_team = None
losing_team = None
running = True

# Network variables
conn = None
client_id = None

# --- Asset Loading ---
try:
    fighter_animations = load_animations_Arcane_Archer()
except Exception as e:
    fighter_animations = {}

transparent_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
transparent_surface.fill((0, 0, 0, 0))
images = {
    "fighter": transparent_surface,
    "projectiles": pygame.image.load("src/assets/images/inused_single_images/projectile_Arcane.png")
}


def threaded_receive_update(sock):
    global game_state, previous_game_state, last_update_time, game_over, winning_team, losing_team, client_state
    while running:
        try:
            data = sock.recv(4096)
            if not data:
                if running:
                    print("Disconnected from server.")
                break
            client_package = pickle.loads(data)
            #print(f"Received package: {client_package}")
            if client_package.get("request_type") == "game_update":
                with shared_lock:
                    previous_game_state = game_state
                    game_state = client_package.get("game_world")
                    last_update_time = time.time()
                    client_state = "in_game" 
                    for fighter in game_state.get("fighters", []):
                        health = fighter.get("health", 100)
                        max_health = fighter.get("max_health", 100)
                        # print(f"Received fighter: id={fighter['id']}, health={health}/{max_health}, state={fighter.get('state', 'N/A')}, raw_data={fighter}")
            elif client_package.get("request_type") == "game_started":
                client_state = "in_game" 
            elif client_package.get("request_type") == "game_finished":
                winning_team = client_package.get("winning_team")
                losing_team = client_package.get("losing_team")
                game_over = True
                print(f"Game finished: winning_team={winning_team}, losing_team={losing_team}")
            elif client_package.get("request_type") == "lobby_destroyed":
                print("Lobby has been destroyed by the host.")
                client_state = "menu" # Go back to a waiting/menu state
        except Exception as e:
            if running:
                print(f"Error receiving message: {e}")
            break

def send_request_to_server(client_package):
    global running
    try:
        conn.sendall(pickle.dumps(client_package))
        #print(f"Sent client_package: {client_package}")
    except Exception as e:
        print(f"Error sending data: {e}")
        running = False
        return False
    return True

def handle_input():
    """Processes user input events and returns lists of inputs and shoots."""
    global running, client_state
    inputs = []
    shoots = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Menu/Lobby actions
            if event.key == pygame.K_1:  # find_random_game
                pkg = {"client_id": client_id, "request_type": "find_random_game", "game_mode": "1vs1"}
                if send_request_to_server(pkg):
                    client_state = "searching"
            elif event.key == pygame.K_2:  # make_lobby
                pkg = {"client_id": client_id, "request_type": "make_lobby", "game_mode": "1vs1"}
                if send_request_to_server(pkg):
                    client_state = "lobby"
            elif event.key == pygame.K_3:  # join_lobby
                pkg = {"client_id": client_id, "request_type": "join_lobby", "room_id": client_id}
                send_request_to_server(pkg)
            elif event.key == pygame.K_4:  # start_the_game_as_host
                pkg = {"client_id": client_id, "request_type": "start_the_game_as_host"}
                send_request_to_server(pkg)
            elif event.key == pygame.K_5:  # destroy_lobby
                pkg = {"client_id": client_id, "request_type": "destroy_lobby"}
                send_request_to_server(pkg)

            # In-game actions
            if event.key in key_pressed and not key_pressed[event.key]:
                if event.key == pygame.K_SPACE:
                    shoots.append("arcane") 
                    # print(f"Shoot input added: arcane")
                key_pressed[event.key] = True
                inputs.append(("down", event.key))
                # print(f"KEYDOWN: {event.key}")
        elif event.type == pygame.KEYUP:
            if event.key in key_pressed:
                key_pressed[event.key] = False
                inputs.append(("up", event.key))
    return inputs, shoots

def update_and_render():
    """Renders the correct screen based on the current client state."""
    global running
    if game_over:
        draw_game_over(screen, winning_team, losing_team)
        running = False
    elif client_state == "in_game":
        draw_game_state(screen, shared_lock, game_state, previous_game_state, last_update_time, network_interval, fighter_animations, client_anim_states, images)
    elif client_state in ["searching", "waiting"]:
        draw_waiting_screen(screen)
    elif client_state == "lobby":
        draw_lobby_screen(screen)
    elif client_state == "menu":
        draw_menu_screen(screen)
    else: # Fallback
        print("Unknown client_state:", client_state)
        draw_waiting_screen(screen)
    
    pygame.display.flip()
    clock.tick(60)

def main():
    """Main function to initialize and run the client."""
    global conn, client_id, running

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    conn.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
    conn.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)

    try:
        conn.connect((SERVER_IP, SERVER_PORT))
    except Exception as e:
        print("Could not connect to the server:", e)
        return

    try:
        client_id_data = conn.recv(4096)
        client_id = pickle.loads(client_id_data)
        print("Connected to server. Your client ID is:", client_id)
    except Exception as e:
        print("Error receiving client ID:", e)
        conn.close()
        return

    recv_thread = threading.Thread(target=threaded_receive_update, args=(conn,))
    recv_thread.daemon = True
    recv_thread.start()

    # Initial request to find a game
    client_first_package = {
        "client_id": client_id, "request_type": "find_random_game", "game_mode": "1vs1",
        "inputs": [], "shoots": []
    }
    send_request_to_server(client_first_package)

    while running:
        inputs, shoots = handle_input()

        if inputs or shoots:
            client_package = {
                "client_id": client_id,
                "request_type": "input",
                "game_mode": "1vs1",
                "inputs": inputs,
                "shoots": shoots
            }
            send_request_to_server(client_package)
        
        update_and_render()

    # Cleanup
    running = False
    conn.close()
    pygame.quit()
    print("Connection closed and Pygame quit.")

if __name__ == "__main__":
    main()