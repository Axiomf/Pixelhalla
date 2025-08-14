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
    draw_menu_screen, draw_waiting_screen, draw_enter_lobby_screen, draw_game_mode_screen, draw_countdown_screen, draw_enter_username_screen
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
key_pressed = {
    pygame.K_a: False, pygame.K_d: False, pygame.K_w: False, pygame.K_SPACE: False
}

game_state = None
previous_game_state = None
last_update_time = 0
network_interval = 0.1
shared_lock = threading.Lock()
client_anim_states = {}
client_state = "enter_username"  # Start with username entry
game_over = False
winning_team = None
losing_team = None
running = True
game_mode = None
error_message = None
error_message_time = None
countdown_value = None
username = ""
entered_lobby_id = ""

conn = None
client_id = None
lobby_id = None

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
    global game_state, previous_game_state, last_update_time, game_over, winning_team, losing_team, client_state, lobby_id, error_message, error_message_time, countdown_value
    while running:
        try:
            data = sock.recv(4096)
            if not data:
                if running:
                    print("Disconnected from server.")
                break
            client_package = pickle.loads(data)
            if client_package.get("request_type") == "game_update":
                with shared_lock:
                    previous_game_state = game_state
                    game_state = client_package.get("game_world")
                    last_update_time = time.time()
                    client_state = "in_game"
            elif client_package.get("request_type") == "game_started":
                client_state = "in_game"
                countdown_value = None
                print("Game started!")
            elif client_package.get("request_type") == "game_finished":
                winning_team = client_package.get("winning_team")
                losing_team = client_package.get("losing_team")
                game_over = True
                print(f"Game finished: winning_team={winning_team}, losing_team={losing_team}")
            elif client_package.get("request_type") == "lobby_destroyed":
                print("Lobby has been destroyed by the host.")
                client_state = "menu"
            elif client_package.get("request_type") == "lobby_created":
                lobby_id = client_package.get("lobby_id")
                client_state = "lobby"
                print(f"Lobby created with ID: {lobby_id}")
            elif client_package.get("request_type") == "lobby_joined":
                lobby_id = client_package.get("lobby_id")
                client_state = "lobby"
                entered_lobby_id = ""
                print(f"Joined lobby with ID: {lobby_id}")
            elif client_package.get("request_type") == "lobby_join_failed":
                error_message = client_package.get("message", "Lobby not found")
                error_message_time = time.time()
                print(f"Lobby join failed: {error_message}")
            elif client_package.get("request_type") == "client_disconnected":
                print(f"Client {client_package.get('client_id')} disconnected from the game or lobby")
            elif client_package.get("request_type") == "countdown":
                countdown_value = client_package.get("count")
                client_state = "countdown"
                print(f"Countdown: {countdown_value}")
        except Exception as e:
            if running:
                print(f"Error receiving message: {e}")
            break

def send_request_to_server(client_package):
    global running
    try:
        conn.sendall(pickle.dumps(client_package))
    except Exception as e:
        print(f"Error sending data: {e}")
        running = False
        return False
    return True

def handle_input(option_rects):
    global running, client_state, game_mode, entered_lobby_id, error_message, error_message_time, username
    inputs = []
    shoots = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if client_state == "enter_username":
                if event.key == pygame.K_RETURN:
                    if username:  # Proceed to game mode selection if username is not empty
                        client_state = "select_game_mode"
                        # Send username to server
                        pkg = {"client_id": client_id, "request_type": "set_username", "username": username}
                        send_request_to_server(pkg)
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.unicode.isalnum() or event.unicode in ['_']:  # Allow alphanumeric and underscore
                    if len(username) < 15:  # Limit username length
                        username += event.unicode
            elif client_state == "select_game_mode":
                if event.key == pygame.K_1:
                    game_mode = "1vs1"
                    client_state = "menu"
                elif event.key == pygame.K_2:
                    game_mode = "2vs2"
                    client_state = "menu"
            elif client_state == "enter_lobby_id":
                if event.key == pygame.K_RETURN:
                    if entered_lobby_id and not error_message:  # Only send if no error message
                        pkg = {"client_id": client_id, "request_type": "join_lobby", "room_id": entered_lobby_id, "game_mode": game_mode}
                        send_request_to_server(pkg)
                    elif error_message:  # Clear error and return to menu
                        error_message = None
                        error_message_time = None
                        client_state = "menu"
                elif event.key == pygame.K_BACKSPACE:
                    entered_lobby_id = entered_lobby_id[:-1]
                elif event.key == pygame.K_ESCAPE:  # Return to menu on Escape
                    error_message = None
                    error_message_time = None
                    entered_lobby_id = ""
                    client_state = "menu"
                elif event.unicode.isalnum():
                    entered_lobby_id += event.unicode
            else:
                if event.key == pygame.K_1:
                    pkg = {"client_id": client_id, "request_type": "find_random_game", "game_mode": game_mode}
                    if send_request_to_server(pkg):
                        client_state = "searching"
                elif event.key == pygame.K_2:
                    pkg = {"client_id": client_id, "request_type": "make_lobby", "game_mode": game_mode}
                    if send_request_to_server(pkg):
                        client_state = "lobby"
                elif event.key == pygame.K_3:
                    client_state = "enter_lobby_id"
                elif event.key == pygame.K_4:
                    pkg = {"client_id": client_id, "request_type": "start_the_game_as_host"}
                    send_request_to_server(pkg)
                elif event.key == pygame.K_5:
                    pkg = {"client_id": client_id, "request_type": "destroy_lobby"}
                    send_request_to_server(pkg)
                if event.key in key_pressed and not key_pressed[event.key]:
                    if event.key == pygame.K_SPACE:
                        shoots.append("arcane")
                    key_pressed[event.key] = True
                    inputs.append(("down", event.key))
        elif event.type == pygame.KEYUP:
            if event.key in key_pressed:
                key_pressed[event.key] = False
                inputs.append(("up", event.key))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for i, rect in enumerate(option_rects):
                if rect.collidepoint(mouse_pos):
                    if client_state == "select_game_mode":
                        if i == 0:
                            game_mode = "1vs1"
                            client_state = "menu"
                        elif i == 1:
                            game_mode = "2vs2"
                            client_state = "menu"
                    elif client_state == "menu":
                        if i == 0:
                            pkg = {"client_id": client_id, "request_type": "find_random_game", "game_mode": game_mode}
                            if send_request_to_server(pkg):
                                client_state = "searching"
                        elif i == 1:
                            pkg = {"client_id": client_id, "request_type": "make_lobby", "game_mode": game_mode}
                            if send_request_to_server(pkg):
                                client_state = "lobby"
                        elif i == 2:
                            client_state = "enter_lobby_id"
    return inputs, shoots

def update_and_render():
    global running, error_message, error_message_time, client_state, countdown_value, username
    mouse_pos = pygame.mouse.get_pos()
    option_rects = []
    if game_over:
        draw_game_over(screen, winning_team, losing_team)
        running = False
    elif client_state == "in_game":
        draw_game_state(screen, shared_lock, game_state, previous_game_state, last_update_time, network_interval, fighter_animations, client_anim_states, images)
    elif client_state in ["searching", "waiting"]:
        draw_waiting_screen(screen)
    elif client_state == "lobby":
        draw_lobby_screen(screen, lobby_id)
    elif client_state == "menu":
        option_rects = draw_menu_screen(screen, mouse_pos)
    elif client_state == "enter_lobby_id":
        draw_enter_lobby_screen(screen, entered_lobby_id, error_message)
        # Automatically return to menu after 3 seconds if error message exists
        if error_message and error_message_time and (time.time() - error_message_time > 2):
            error_message = None
            error_message_time = None
            client_state = "menu"
    elif client_state == "select_game_mode":
        option_rects = draw_game_mode_screen(screen, mouse_pos)
    elif client_state == "countdown":
        draw_countdown_screen(screen, countdown_value)
    elif client_state == "enter_username":
        draw_enter_username_screen(screen, username)
    else:
        print("Unknown client_state:", client_state)
        draw_waiting_screen(screen)
    
    # Clear error message after 3 seconds in menu or enter_lobby_id
    if error_message and error_message_time and client_state != "enter_lobby_id" and (time.time() - error_message_time > 3):
        error_message = None
        error_message_time = None
    
    pygame.display.flip()
    clock.tick(60)
    return option_rects

def main():
    global conn, client_id, running, username

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

    while running:
        option_rects = update_and_render()
        inputs, shoots = handle_input(option_rects)

        if inputs or shoots:
            client_package = {
                "client_id": client_id,
                "request_type": "input",
                "game_mode": game_mode,
                "inputs": inputs,
                "shoots": shoots
            }
            send_request_to_server(client_package)

    running = False
    conn.close()
    pygame.quit()
    print("Connection closed and Pygame quit.")

if __name__ == "__main__":
    main()