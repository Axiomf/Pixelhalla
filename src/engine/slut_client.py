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
    draw_menu_screen, draw_waiting_screen, draw_enter_lobby_screen, draw_game_mode_screen
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

info_package = {
                        "request_type": "info", 
                        "lobby_id": lobby_joined.lobby_id, 
                        "game_mode": lobby_joined.game_mode, 
                        "members": lobby_joined.members, 
                        "host_id": lobby_joined.host_id,
                        "is_host": False, 
                        "lobby_members_id": lobby_joined.members
                    }
"""

# --- Pygame and Display Setup ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((1200, 600))
pygame.display.set_caption("Pixelhala Client")
clock = pygame.time.Clock()

# --- Global State and Configuration ---
key_pressed = {
    pygame.K_a: False, pygame.K_d: False, pygame.K_w: False, pygame.K_SPACE: False
}

# Game state
game_lock = threading.Lock()
game_state = None
previous_game_state = None
last_update_time = 0
network_interval = 0.1  # How often we expect updates from server (in seconds)
client_anim_states = {}  # key: object id, value: dict with current_animation, current_frame, last_update

# Client status
info_lock = threading.Lock()
client_state = "menu"  # "menu", "lobby", "in_game", "searching", "waiting", "typing_room_id"
game_over = False
winning_team = None
losing_team = None
running = True 
input_text = ""

is_host = False # True if the client is the host
game_mode = "1vs1" # or 2vs2 

lobby_id = None # id of the lobby or id of the lobby's host
lobby_members_id = [] # ids of clients in the lobby


conn = None
client_id = None
lobby_id = None
entered_lobby_id = ""

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
    global game_state, previous_game_state, last_update_time, game_over, winning_team, losing_team, client_state, lobby_id
    global is_host, lobby_id, lobby_members_id, game_mode
    while running:
        try:
            data = sock.recv(4096)
            if not data:
                if running:
                    print("Disconnected from server.")
                break
            client_package = pickle.loads(data)
            if client_package.get("request_type") == "game_update":
                with game_lock:
                    previous_game_state = game_state
                    game_state = client_package.get("game_world")
                    last_update_time = time.time()
                with info_lock:
                    client_state = "in_game"                 
            elif client_package.get("request_type") == "game_started":
                with info_lock:
                    client_state = "in_game" 
            elif client_package.get("request_type") == "game_finished":
                with info_lock:
                    winning_team = client_package.get("winning_team")
                    losing_team = client_package.get("losing_team")
                    game_over = True
                print(f"Game finished: winning_team={winning_team}, losing_team={losing_team}")
            elif client_package.get("request_type") == "lobby_destroyed":
                print("Lobby has been destroyed by the host.")
                with info_lock:
                    client_state = "menu" # Go back to a waiting/menu state
            elif client_package.get("request_type") == "info":
                #print(f"Received info package: {client_package}")
                with info_lock: # host_id
                    
                    is_host = client_package.get("is_host")
                    lobby_id = client_package.get("lobby_id")
                    print(f"Joined lobby: {lobby_id} this is important")
                    lobby_members_id = client_package.get("lobby_members_id")
                    game_mode = client_package.get("game_mode")
                    client_state = "lobby"
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
    global running, client_state, game_over, winning_team, losing_team, is_host, lobby_id, lobby_members_id, game_mode, input_text, entered_lobby_id
    inputs = []
    shoots = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # --- Keyboard input for typing lobby id ---
        elif client_state in ["typing_room_id", "enter_lobby_id"]:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Use input_text or entered_lobby_id depending on state
                    room_id = input_text if client_state == "typing_room_id" else entered_lobby_id
                    pkg = {"client_id": client_id, "request_type": "join_lobby", "room_id": room_id}
                    send_request_to_server(pkg)
                    with info_lock:
                        client_state = "lobby"
                    input_text = ""
                    entered_lobby_id = ""
                elif event.key == pygame.K_BACKSPACE:
                    if client_state == "typing_room_id":
                        input_text = input_text[:-1]
                    else:
                        entered_lobby_id = entered_lobby_id[:-1]
                elif event.key == pygame.K_ESCAPE:
                    with info_lock:
                        client_state = "menu"
                    input_text = ""
                    entered_lobby_id = ""
                else:
                    if client_state == "typing_room_id":
                        input_text += event.unicode
                    else:
                        entered_lobby_id += event.unicode
        # --- Keyboard menu/lobby/game actions ---
        elif event.type == pygame.KEYDOWN:
            # Menu/Lobby actions
            if event.key == pygame.K_1:  # find_random_game
                pkg = {"client_id": client_id, "request_type": "find_random_game", "game_mode": game_mode}
                if send_request_to_server(pkg):
                    with info_lock:
                        client_state = "searching"
            elif event.key == pygame.K_2:  # make_lobby
                pkg = {"client_id": client_id, "request_type": "make_lobby", "game_mode": game_mode}
                if send_request_to_server(pkg):
                    with info_lock:
                        client_state = "lobby"
                        is_host = True
                        lobby_id = client_id
                        lobby_members_id = [client_id]
                        game_over = False
                        winning_team = None
                        losing_team = None
            elif event.key == pygame.K_3:  # join_lobby
                with info_lock:
                    client_state = "typing_room_id"
                input_text = ""
            elif event.key == pygame.K_4:  # start_the_game_as_host
                pkg = {"client_id": client_id, "request_type": "start_the_game_as_host"}
                send_request_to_server(pkg)
            elif event.key == pygame.K_5:  # destroy_lobby
                pkg = {"client_id": client_id, "request_type": "destroy_lobby"}
                send_request_to_server(pkg)
            elif event.key == pygame.K_p:
                with info_lock:
                    if game_mode == "1vs1":
                        game_mode = "2vs2"
                    else:
                        game_mode = "1vs1"
                    print(f"Game mode switched to: {game_mode}")
            else:
                print(f"Unknown key pressed: {event.key}")
            # In-game actions
            if event.key in key_pressed and not key_pressed[event.key]:
                if event.key == pygame.K_SPACE:
                    shoots.append("arcane")
                key_pressed[event.key] = True
                inputs.append(("down", event.key))
        elif event.type == pygame.KEYUP:
            if event.key in key_pressed:
                key_pressed[event.key] = False
                inputs.append(("up", event.key))
        # --- Mouse input for menu/game mode/lobby id ---
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
                            with info_lock:
                                client_state = "enter_lobby_id"
                            entered_lobby_id = ""
                    elif client_state == "enter_lobby_id":
                        # Optionally, could have a button to confirm entry
                        pass
    return inputs, shoots

def update_and_render():
    global running, game_over, winning_team, losing_team, client_state, lobby_id, input_text, entered_lobby_id
    mouse_pos = pygame.mouse.get_pos()
    option_rects = []
    if game_over:
        draw_game_over(screen, winning_team, losing_team)
        pygame.display.flip()
        time.sleep(2)
        with info_lock:
            game_over = False # Reset for next game
            print(lobby_id)
            if lobby_id:
                client_state = "lobby"
            else:
                client_state = "menu"
    elif client_state == "in_game":
        draw_game_state(screen, game_lock, game_state, previous_game_state, last_update_time, network_interval, fighter_animations, client_anim_states, images)
    elif client_state in ["searching", "waiting"]:
        draw_waiting_screen(screen)
    elif client_state == "lobby":
        draw_lobby_screen(screen, lobby_id)
    elif client_state == "typing_room_id":
        draw_menu_screen(screen)
        font = pygame.font.Font(None, 50)
        text_surface = font.render("Enter Room ID: " + input_text, True, (255, 255, 255))
        screen.blit(text_surface, (400, 300))
    elif client_state == "menu":
        option_rects = draw_menu_screen(screen, mouse_pos)
    elif client_state == "enter_lobby_id":
        draw_enter_lobby_screen(screen, entered_lobby_id)
        font = pygame.font.Font(None, 50)
        text_surface = font.render("Enter Room ID: " + entered_lobby_id, True, (255, 255, 255))
        screen.blit(text_surface, (400, 300))
    elif client_state == "select_game_mode":
        option_rects = draw_game_mode_screen(screen, mouse_pos)
    else:
        print("Unknown client_state:", client_state)
        draw_waiting_screen(screen)
    pygame.display.flip()
    clock.tick(60)
    return option_rects

def main():
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
        pygame.display.set_caption("Client: " + str(client_id))
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
        #print(client_state)
        #print(lobby_id)
        if (inputs or shoots) and client_state == "in_game" and not game_over:
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