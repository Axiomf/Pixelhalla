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
# transformation general templates
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
pygame.init()
screen = pygame.display.set_mode((1200, 600))
pygame.display.set_caption("Pixelhala Client")
clock = pygame.time.Clock()


key_pressed = {
    pygame.K_a: False,
    pygame.K_d: False,
    pygame.K_w: False,
    pygame.K_SPACE: False
}


def threaded_receive_update(sock):
    global game_state, previous_game_state, last_update_time, game_over, winning_team, losing_team, client_state
    while True:
        try:
            data = sock.recv(4096)
            if not data:
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
            print(f"Error receiving message: {e}")
            break

conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Apply socket options for performance, similar to the server
conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
conn.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
conn.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)

try:
    conn.connect((SERVER_IP, SERVER_PORT))
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

recv_thread = threading.Thread(target=threaded_receive_update, args=(conn,))
recv_thread.daemon = True
recv_thread.start()

transparent_surface = pygame.Surface((32, 32), pygame.SRCALPHA)  
transparent_surface.fill((0, 0, 0, 0))  
images = {
    "fighter": transparent_surface,
    "projectiles" :  pygame.image.load("src/assets/images/inused_single_images/projectile_Arcane.png")
}
try:
    fighter_animations = load_animations_Elf_Archer()
    # print(f"Loaded animations: {list(fighter_animations.keys())}")
except Exception as e:
    # print(f"Error loading animations: {e}")
    fighter_animations = {}

game_state = None
previous_game_state = None
last_update_time = 0
network_interval = 0.1  # How often we expect updates from server (in seconds)
shared_lock = threading.Lock()  # For thread-safe access to game state

# Add global dictionary to track per-object animation state
client_anim_states = {}  # key: object id, value: dict with current_animation, current_frame, last_update

# متغیرهای جدید برای پایان بازی
game_over = False
winning_team = None
losing_team = None
client_state = "menu"  # "menu", "lobby", "in_game", "searching", "waiting"

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
    inputs = []
    shoots = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Handle menu/lobby actions
            if event.key == pygame.K_1: # find_random_game
                client_package = {"client_id": client_id, 
                                  "request_type": "find_random_game", 
                                  "game_mode": "1vs1"}
                if send_request_to_server(client_package):
                    client_state = "searching"
            elif event.key == pygame.K_2: # make_lobby
                client_package = {"client_id": client_id, 
                                  "request_type": "make_lobby", 
                                  "game_mode": "1vs1"}
                if send_request_to_server(client_package):
                    client_state = "lobby"
            elif event.key == pygame.K_3: # join_lobby
                # For simplicity, we'll try to join a lobby with our own client_id as room_id
                # In a real scenario, you'd get this from user input or a lobby list.
                client_package = {"client_id": client_id, 
                                  "request_type": "join_lobby", 
                                  "room_id": client_id}
                if send_request_to_server(client_package):
                    # may not join to the lobby, full or invalid
                    #client_state = "lobby"
                    pass
            elif event.key == pygame.K_4: # start_the_game_as_host
                client_package = {"client_id": client_id, 
                                  "request_type": "start_the_game_as_host"}
                send_request_to_server(client_package)
            elif event.key == pygame.K_5: # destroy_lobby
                client_package = {"client_id": client_id,
                                  "request_type": "destroy_lobby"}
                send_request_to_server(client_package)

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
                # print(f"KEYUP: {event.key}")

    if inputs:
        client_package = {
            "client_id": client_id,
            "request_type": "input",
            "game_mode": "1vs1",
            "inputs": inputs,
            "shoots": shoots
        }
        send_request_to_server(client_package)
    
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
    clock.tick(60)

pygame.quit()
conn.close()