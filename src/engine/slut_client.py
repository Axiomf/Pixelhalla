# slut_client.py
import socket
import pickle
import threading
import time
import pygame
from src.engine.dynamic_objects import *
from src.engine.animation_loader import load_animations_Arcane_Archer
# transformation general templates
"""  
example of full packages:

objets_serialized:
        "x": sprite.rect.x,
        "y": sprite.rect.y,
        "state": getattr(sprite, "state", "idle"),
        "id": sprite.id,
        "is_doing" : sprite.is_doing

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

images = {
    "Fighter": pygame.image.load("src/assets/images/inused_single_images/fighter.png").convert_alpha()
}
try:
    fighter_animations = load_animations_Arcane_Archer()
    # print(f"Loaded animations: {list(fighter_animations.keys())}")
except Exception as e:
    # print(f"Error loading animations: {e}")
    fighter_animations = {}

game_state = None
previous_game_state = None
last_update_time = 0
network_interval = 0.1
shared_lock = threading.Lock()

key_pressed = {
    pygame.K_a: False,
    pygame.K_d: False,
    pygame.K_w: False,
    pygame.K_SPACE: False
}

def threaded_receive_update(sock):
    global game_state, previous_game_state, last_update_time
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("Disconnected from server.")
                break
            client_package = pickle.loads(data)
            print(f"Received package: {client_package}")
            if client_package.get("request_type") == "game_update":
                with shared_lock:
                    previous_game_state = game_state
                    game_state = client_package.get("game_world")
                    last_update_time = time.time()
                    print(f"Received game_state: {game_state}")
            elif client_package.get("request_type") == "game_started":
                print(f"Game started: {client_package}")
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

server_ip = "127.0.0.1"
server_port = 5555
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

recv_thread = threading.Thread(target=threaded_receive_update, args=(conn,))
recv_thread.daemon = True
recv_thread.start()

def interpolate_rect(prev_rect, curr_rect, alpha):
    # Interpolates between two rects.
    return tuple(int(prev_rect[i] + alpha * (curr_rect[i] - prev_rect[i])) for i in range(4))

def render_obj(screen, rect, obj):
    sprite_type = obj.get("type", "Fighter")
    color = obj.get("color", (255, 255, 255))
    facing_right = obj.get("facing_right", True)
    # Clients handle animation themselves so omit server animation frames.
    if sprite_type == "Fighter":
        image = images[sprite_type]
        if not facing_right:
            image = pygame.transform.flip(image, True, False)
        scaled_image = pygame.transform.scale(image, (rect[2], rect[3]))
        screen.blit(scaled_image, (rect[0], rect[1]))
    else:
        pygame.draw.rect(screen, color, rect)

def draw_game_state(screen):
    screen.fill((0, 0, 0))
    now = time.time()
    with shared_lock:
        current_state = game_state
        prev_state = previous_game_state
        last_time = last_update_time
    # print(f"Current game_state: {current_state}")
    if current_state:
        alpha = 1.0
        if prev_state and last_time:
            alpha = min(1, (now - last_time) / network_interval)
        for key in ['platforms', 'fighters', 'projectiles', 'power_ups']:
            current_group = current_state.get(key, [])
            # print(f"Rendering {key}: {len(current_group)} items")
            if prev_state and len(prev_state.get(key, [])) == len(current_group):
                prev_group = prev_state.get(key, [])
                for idx, obj in enumerate(current_group):
                    curr_rect = obj.get("rect")
                    prev_rect = prev_group[idx].get("rect")
                    # interp_rect = interpolate_rect(prev_rect, curr_rect, alpha) if (curr_rect and prev_rect) else curr_rect
                    if curr_rect and prev_rect:
                        interp_rect = interpolate_rect(prev_rect, curr_rect, alpha)
                    else:
                        interp_rect = curr_rect
                    if interp_rect:
                        render_obj(screen, interp_rect, obj)
            else:
                for obj in current_group:
                    rect = obj.get("rect")
                    if rect:
                        render_obj(screen, rect, obj)
    pygame.display.flip()

def send_request_to_server(client_package):
    global running
    try:
        conn.sendall(pickle.dumps(client_package))
        print(f"Sent client_package: {client_package}")
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
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in key_pressed and not key_pressed[event.key]:
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
            "shoots": []
        }
        send_request_to_server(client_package)
    
    draw_game_state(screen)
    clock.tick(60)

pygame.quit()
conn.close()