import socket
import pickle
import threading
import time
import pygame
from src.engine.dynamic_objects import *
from src.engine.animation_loader import load_animations_Arcane_Archer

pygame.init()
screen = pygame.display.set_mode((1200, 600))
pygame.display.set_caption("Pixelhala Client")
clock = pygame.time.Clock()

# تعریف سطح شفاف به عنوان تصویر پیش‌فرض
transparent_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
transparent_surface.fill((0, 0, 0, 0))

images = {
    "Fighter": transparent_surface
}
try:
    fighter_animations = load_animations_Arcane_Archer()
    print(f"Loaded animations: {list(fighter_animations.keys())}")
except Exception as e:
    print(f"Error loading animations: {e}")
    fighter_animations = {}

# دیکشنری برای مدیریت فریم‌های انیمیشن هر فایتر
fighter_animation_states = {}  # کلید: fighter_id، مقدار: {"current_frame": int, "last_update": float}

game_state = None
previous_game_state = None
last_update_time = 0
network_interval = 0.1
shared_lock = threading.Lock()
animation_frame_duration = 0.1  # مدت زمان هر فریم انیمیشن (100 میلی‌ثانیه)

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
            elif client_package.get("request_type") == "report":
                print("Server report:", client_package.get("report"))
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

def update_animation_state(fighter_id, state):
    """به‌روزرسانی فریم انیمیشن برای یک فایتر بر اساس state"""
    now = time.time()
    if fighter_id not in fighter_animation_states:
        fighter_animation_states[fighter_id] = {"current_frame": 0, "last_update": now}
    
    anim_state = fighter_animation_states[fighter_id]
    if anim_state["last_update"] + animation_frame_duration < now:
        if state in fighter_animations and fighter_animations[state]:
            anim_state["current_frame"] = (anim_state["current_frame"] + 1) % len(fighter_animations[state])
            anim_state["last_update"] = now
            print(f"Updated animation for fighter {fighter_id}: state={state}, frame={anim_state['current_frame']}")

def draw_game_state(screen):
    screen.fill((0, 0, 0))
    now = time.time()
    with shared_lock:
        current_state = game_state
        prev_state = previous_game_state
        last_time = last_update_time
    print(f"Current game_state: {current_state}")
    if current_state:
        alpha = 1.0
        if prev_state and last_time:
            alpha = min(1, (now - last_time) / network_interval)
        for key in ['platforms', 'fighters', 'projectiles', 'power_ups']:
            current_group = current_state.get(key, [])
            print(f"Rendering {key}: {len(current_group)} items")
            if prev_state and len(prev_state.get(key, [])) == len(current_group):
                prev_group = prev_state.get(key, [])
                for idx, obj in enumerate(current_group):
                    curr_rect = obj.get("rect")
                    prev_rect = prev_group[idx].get("rect")
                    sprite_type = obj.get("type", "Fighter")
                    color = obj.get("color", (255, 255, 255))
                    if sprite_type == "Fighter":
                        fighter_id = obj.get("fighter_id", "unknown")
                        state = obj.get("state", "idle")
                        facing_right = obj.get("facing_right", True)
                        update_animation_state(fighter_id, state)
                        current_frame = fighter_animation_states.get(fighter_id, {"current_frame": 0})["current_frame"]
                    else:
                        state = "idle"
                        current_frame = 0
                        facing_right = True
                    print(f"Rendering {sprite_type}: rect={curr_rect}, state={state}, frame={current_frame}, facing_right={facing_right}")
                    if curr_rect and prev_rect:
                        interp_rect = tuple(int(prev_rect[i] + alpha * (curr_rect[i] - prev_rect[i])) for i in range(4))
                    else:
                        interp_rect = curr_rect
                    if interp_rect:
                        if sprite_type == "Fighter":
                            if fighter_animations and state in fighter_animations:
                                frame = fighter_animations[state][current_frame % len(fighter_animations[state])]
                                if not facing_right:
                                    frame = pygame.transform.flip(frame, True, False)
                                scaled_frame = pygame.transform.scale(frame, (interp_rect[2], interp_rect[3]))
                                screen.blit(scaled_frame, (interp_rect[0], interp_rect[1]))
                                print(f"Rendered animation for Fighter {fighter_id}: state={state}, frame={current_frame}")
                            else:
                                print(f"Animation {state} not found for Fighter {fighter_id}, using transparent fallback")
                                scaled_frame = pygame.transform.scale(images[sprite_type], (interp_rect[2], interp_rect[3]))
                                screen.blit(scaled_frame, (interp_rect[0], interp_rect[1]))
                        else:
                            pygame.draw.rect(screen, color, interp_rect)
                            print(f"Rendered rect for {sprite_type}: color={color}")
            else:
                for obj in current_group:
                    rect = obj.get("rect")
                    sprite_type = obj.get("type", "Fighter")
                    color = obj.get("color", (255, 255, 255))
                    if sprite_type == "Fighter":
                        fighter_id = obj.get("fighter_id", "unknown")
                        state = obj.get("state", "idle")
                        facing_right = obj.get("facing_right", True)
                        update_animation_state(fighter_id, state)
                        current_frame = fighter_animation_states.get(fighter_id, {"current_frame": 0})["current_frame"]
                    else:
                        state = "idle"
                        current_frame = 0
                        facing_right = True
                    print(f"Rendering {sprite_type}: rect={rect}, state={state}, frame={current_frame}, facing_right={facing_right}")
                    if rect:
                        if sprite_type == "Fighter":
                            if fighter_animations and state in fighter_animations:
                                frame = fighter_animations[state][current_frame % len(fighter_animations[state])]
                                if not facing_right:
                                    frame = pygame.transform.flip(frame, True, False)
                                scaled_frame = pygame.transform.scale(frame, (rect[2], rect[3]))
                                screen.blit(scaled_frame, (rect[0], rect[1]))
                                print(f"Rendered animation for Fighter {fighter_id}: state={state}, frame={current_frame}")
                            else:
                                print(f"Animation {state} not found for Fighter {fighter_id}, using transparent fallback")
                                scaled_frame = pygame.transform.scale(images[sprite_type], (rect[2], rect[3]))
                                screen.blit(scaled_frame, (rect[0], rect[1]))
                        else:
                            pygame.draw.rect(screen, color, rect)
                            print(f"Rendered rect for {sprite_type}: color={color}")
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
                print(f"KEYDOWN: {event.key}")
            if event.key - 48 == 1:  # find_random_game
                print(f"I pressed: 1  {event.key==49}")
            elif event.key - 48 == 2:  # join_lobby
                print(2)
            elif event.key - 48 == 3:  # make_lobby
                print(3)
            elif event.key - 48 == 4:  # start_the_game_as_host
                print(4)
        elif event.type == pygame.KEYUP:
            if event.key in key_pressed:
                key_pressed[event.key] = False
                inputs.append(("up", event.key))
                print(f"KEYUP: {event.key}")

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
try:
    conn.close()
except:
    pass
