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
    global game_state, previous_game_state, last_update_time, game_over, winning_team, losing_team, is_waiting
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
                    is_waiting = False 
                    for fighter in game_state.get("fighters", []):
                        health = fighter.get("health", 100)
                        max_health = fighter.get("max_health", 100)
                        # print(f"Received fighter: id={fighter['id']}, health={health}/{max_health}, state={fighter.get('state', 'N/A')}, raw_data={fighter}")
            elif client_package.get("request_type") == "game_started":
                is_waiting = False 
            elif client_package.get("request_type") == "game_finished":
                winning_team = client_package.get("winning_team")
                losing_team = client_package.get("losing_team")
                game_over = True
                print(f"Game finished: winning_team={winning_team}, losing_team={losing_team}")
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
is_waiting = True  # حالت انتظار در ابتدا فعاله

def get_full_rect(rect):
    # Ensure rect is (x, y, width, height), default width and height = 32 if missing
    return rect if len(rect) == 4 else (rect[0], rect[1], 64, 64)

def interpolate_rect(prev_rect, curr_rect, alpha):
    # Ensure both rects are (x, y, width, height)
    prev_rect = get_full_rect(prev_rect)
    curr_rect = get_full_rect(curr_rect)
    # Interpolate each component (x, y, w, h) between previous and current rects
    return tuple(int(prev_rect[i] + alpha * (curr_rect[i] - prev_rect[i])) for i in range(4))

def draw_health_bar(screen, rect, health, max_health):
    bar_width = rect[2] 
    bar_height = 10  
    bar_x = rect[0]
    bar_y = rect[1] - bar_height - 5  
    health_ratio = health / max_health
    health_width = bar_width * health_ratio
    pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height)) 
    pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, health_width, bar_height))  

def static_render(screen, rect, obj, sprite_type):
    image = images.get(sprite_type)
    if image:
        # facing_right = obj.get("facing_right", True)
        if sprite_type == "projectiles":
            w = 10
            h = 10
        # if not facing_right:
        #     image = pygame.transform.flip(image, True, False)
        scaled_image = pygame.transform.scale(image, (w, h))
        screen.blit(scaled_image, (rect[0], rect[1]))
    else:
        pygame.draw.rect(screen, (255, 255, 255), rect)

def dynamic_render(screen, rect, obj):
    facing_right = obj.get("facing_right", True)
    anim = fighter_animations.get(obj.get("state"), None)
    if anim:
        state = client_anim_states.get(
            obj["id"],
            {"current_animation": obj.get("state"), "current_frame": 0, "last_update": time.time()}
        )
        if state["current_animation"] != obj.get("state"):
            state = {"current_animation": obj.get("state"), "current_frame": 0, "last_update": time.time()}
        now = time.time()
        if now - state["last_update"] > 0.1:
            state["current_frame"] = (state["current_frame"] + 1) % len(anim)
            state["last_update"] = now
        client_anim_states[obj["id"]] = state
        image = anim[state["current_frame"]]
        if not facing_right:
            image = pygame.transform.flip(image, True, False)
        scaled_image = pygame.transform.scale(image, (rect[2], rect[3]))
        screen.blit(scaled_image, (rect[0], rect[1]))
        health = obj.get("health",100)
        max_health = obj.get("max_health", 100)
        draw_health_bar(screen, rect, health, max_health)
        # print(f"Rendered fighter: id={obj['id']}, state={state}, health={health}/{max_health}")
    else:
        image = images.get("fighter")
        if image:
            if not facing_right:
                image = pygame.transform.flip(image, True, False)
            scaled_image = pygame.transform.scale(image, (rect[2], rect[3]))
            screen.blit(scaled_image, (rect[0], rect[1]))
        else:
            pygame.draw.rect(screen, (255, 255, 255), rect)

def render_obj(screen, rect, obj, sprite_type):
    rect = get_full_rect(rect)
    if sprite_type == "fighters":
        dynamic_render(screen, rect, obj)
    else:
        static_render(screen, rect, obj, sprite_type)

def draw_waiting_screen(screen):
    waiting_background = pygame.image.load("src/assets/images/background/blue-preview.png").convert_alpha()
    waiting_background = pygame.transform.scale(waiting_background, (config.SCENE_WIDTH, config.SCENE_HEIGHT))
    screen.blit(waiting_background, (0, 0))
    font = pygame.font.SysFont('arial', 50)
    text = font.render("Waiting for game to start...", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()

def draw_game_state(screen):
    # Clear the screen to black before drawing anything
    screen.fill((0, 0, 0))
    now = time.time()
    # Safely copy the shared game state for this frame
    with shared_lock:
        current_state = game_state
        prev_state = previous_game_state
        last_time = last_update_time

    # If we have a current game state, proceed to draw it
    if current_state:
        alpha = 1.0  # Default: no interpolation
        # If we have a previous state and timestamp, calculate interpolation alpha
        if prev_state and last_time:
            alpha = min(1, (now - last_time) / network_interval)
        # Draw each group of objects (platforms, fighters, projectiles, power_ups)
        for key in ['platforms', 'fighters', 'projectiles', 'power_ups']:
            current_group = current_state.get(key, [])
            # If previous state exists and group lengths match, interpolate positions
            if prev_state and len(prev_state.get(key, [])) == len(current_group):
                prev_group = prev_state.get(key, [])
                for idx, obj in enumerate(current_group):
                    curr_rect = obj.get("rect")
                    prev_rect = prev_group[idx].get("rect")
                    # Interpolate rect if both current and previous rects exist
                    if curr_rect and prev_rect:
                        interp_rect = interpolate_rect(prev_rect, curr_rect, alpha)
                    else:
                        interp_rect = curr_rect
                        
                    render_obj(screen, interp_rect, obj,key)
            else:
                # If no previous state or group size mismatch, just draw current positions
                for obj in current_group:
                    rect = obj.get("rect")
                    if rect:
                        render_obj(screen, rect, obj,key)
    # Update the display with everything drawn this frame
    pygame.display.flip()

def draw_game_over(screen, winning_team, losing_team):
    screen.fill((0, 0, 0))  
    font = pygame.font.SysFont('arial', 50) 
    win_text = font.render(f"Team {winning_team} Won!", True, (0, 255, 0)) 
    lose_text = font.render(f"Team {losing_team} Lost!", True, (255, 0, 0)) 
    screen.blit(win_text, (400, 250)) 
    screen.blit(lose_text, (400, 350)) 
    pygame.display.flip()
    time.sleep(5)

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
    elif is_waiting:
        draw_waiting_screen(screen)
    else:
        draw_game_state(screen)
    clock.tick(60)

pygame.quit()
conn.close()