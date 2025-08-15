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
from src.engine.server_client_helper import send_request_to_server
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
info_lock = threading.Lock()
game_state = None

previous_game_state = None
last_update_time = 0
network_interval = 0.1  # How often we expect updates from server (in seconds)
client_anim_states = {}  # key: object id, value: dict with current_animation, current_frame, last_update



# --- Client-side state container ---
class Client_Stats:
    """Encapsulate per-client state previously stored as module-level globals."""
    def __init__(self):
        # identity
        self.client_id = None
        self.username = ""
        # UI / flow state
        self.client_state = "menu"  # "menu", "lobby", "in_game", "searching", "waiting", "typing_room_id"
        self.is_host = False
        # lobby / game info
        self.game_mode = "1vs1"
        self.lobby_id = None
        self.lobby_members_id = []
        # runtime flags & inputs
        self.game_over = False
        self.running = True
        self.input_text = ""
        self.entered_lobby_id = ""
        # results / messages
        self.winning_team = None
        self.losing_team = None
        self.error_message = None
        self.error_message_time = None
        self.countdown_value = None

    def update_state(self, update_dict):
        """
        Update the attributes of Client_Stats with the key-value pairs from update_dict.
        Only existing attributes are updated.
        """
        for key, value in update_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

# single shared instance for this client process
Client_stats = Client_Stats()

# --- Network Setup ---



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
    global is_host, lobby_id, lobby_members_id, game_mode
    while Client_stats.running:
        try:
            data = sock.recv(4096)
            if not data:
                if Client_stats.running:
                    print("Disconnected from server.")
                break
            client_package = pickle.loads(data)
            if client_package.get("request_type") == "game_update":
                with game_lock:
                    previous_game_state = game_state
                    game_state = client_package.get("game_world")
                    last_update_time = time.time()
                with info_lock:
                    Client_stats.client_state = "in_game"                 
            elif client_package.get("request_type") == "game_started":
                with info_lock:
                    Client_stats.client_state = "in_game"
                Client_stats.countdown_value = None
                print("Game started!")
            elif client_package.get("request_type") == "game_finished":
                with info_lock:
                    Client_stats.winning_team = client_package.get("winning_team")
                    Client_stats.losing_team = client_package.get("losing_team")
                    Client_stats.game_over = True
                Client_stats.client_state = "lobby"  # Return to lobby
                print(f"Game finished: winning_team={Client_stats.winning_team}, losing_team={Client_stats.losing_team}")
            elif client_package.get("request_type") == "lobby_destroyed":
                print("Lobby has been destroyed by the host.")
                with info_lock:
                    Client_stats.client_state = "menu"
            elif client_package.get("request_type") == "info":
                #print(f"Received info package: {client_package}")
                with info_lock:
                    Client_stats.is_host = client_package.get("is_host")
                    Client_stats.lobby_id = client_package.get("lobby_id")
                    print(f"Joined lobby: {Client_stats.lobby_id} this is important")
                    Client_stats.lobby_members_id = client_package.get("lobby_members_id")
                    Client_stats.game_mode = client_package.get("game_mode")
                    Client_stats.client_state = "lobby"
        except Exception as e:
            if Client_stats.running:
                print(f"Error receiving message: {e}")
            break

def handle_input(option_rects):
    global conn
    inputs = []
    shoots = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Client_stats.running = False
        # --- Keyboard input for typing lobby id ---
        elif Client_stats.client_state in ["typing_room_id", "enter_lobby_id"]:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Use input_text or entered_lobby_id depending on state
                    room_id = Client_stats.input_text if Client_stats.client_state == "typing_room_id" else Client_stats.entered_lobby_id
                    pkg = {"client_id": Client_stats.client_id, "request_type": "join_lobby", "room_id": room_id}
                    send_request_to_server(conn, pkg)
                    with info_lock:
                        Client_stats.client_state = "lobby"
                    Client_stats.input_text = ""
                    Client_stats.entered_lobby_id = ""
                elif event.key == pygame.K_BACKSPACE:
                    if Client_stats.client_state == "typing_room_id":
                        Client_stats.input_text = Client_stats.input_text[:-1]
                    else:
                        Client_stats.entered_lobby_id = Client_stats.entered_lobby_id[:-1]
                elif event.key == pygame.K_ESCAPE:
                    Client_stats.error_message = None
                    Client_stats.error_message_time = None
                    Client_stats.entered_lobby_id = ""
                    Client_stats.client_state = "menu"
                else:
                    if Client_stats.client_state == "typing_room_id":
                        Client_stats.input_text += event.unicode
                    else:
                        Client_stats.entered_lobby_id += event.unicode
        # --- Keyboard menu/lobby/game actions ---
        elif event.type == pygame.KEYDOWN:
            # Menu/Lobby actions
            if event.key == pygame.K_1:  # find_random_game
                pkg = {"client_id": Client_stats.client_id, "request_type": "find_random_game", "game_mode": Client_stats.game_mode}
                if send_request_to_server(conn, pkg):
                    with info_lock:
                        Client_stats.client_state = "searching"
            elif event.key == pygame.K_2:  # make_lobby
                pkg = {"client_id": Client_stats.client_id, "request_type": "make_lobby", "game_mode": Client_stats.game_mode}
                if send_request_to_server(conn, pkg):
                    with info_lock:
                        Client_stats.client_state = "lobby"
                        Client_stats.is_host = True
                        Client_stats.lobby_id = Client_stats.client_id
                        Client_stats.lobby_members_id = [Client_stats.client_id]
                        Client_stats.game_over = False
                        Client_stats.winning_team = None
                        Client_stats.losing_team = None
            elif event.key == pygame.K_3:  # join_lobby
                with info_lock:
                    Client_stats.client_state = "typing_room_id"
                Client_stats.input_text = ""
            elif event.key == pygame.K_4:  # start_the_game_as_host
                pkg = {"client_id": Client_stats.client_id, "request_type": "start_the_game_as_host"}
                send_request_to_server(conn, pkg)
            elif event.key == pygame.K_5:  # destroy_lobby
                pkg = {"client_id": Client_stats.client_id, "request_type": "destroy_lobby"}
                send_request_to_server(conn, pkg)
            elif event.key == pygame.K_v:
                with info_lock:
                    if Client_stats.game_mode == "1vs1":
                        Client_stats.game_mode = "2vs2"
                    else:
                        Client_stats.game_mode = "1vs1"
                    print(f"Game mode switched to: {Client_stats.game_mode}")
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
                    if Client_stats.client_state == "select_game_mode":
                        if i == 0:
                            Client_stats.game_mode = "1vs1"
                            Client_stats.client_state = "menu"
                        elif i == 1:
                            Client_stats.game_mode = "2vs2"
                            Client_stats.client_state = "menu"
                    elif Client_stats.client_state == "menu":
                        if i == 0:
                            pkg = {"client_id": Client_stats.client_id, "request_type": "find_random_game", "game_mode": Client_stats.game_mode}
                            if send_request_to_server(conn, pkg):
                                Client_stats.client_state = "searching"
                        elif i == 1:
                            pkg = {"client_id": Client_stats.client_id, "request_type": "make_lobby", "game_mode": Client_stats.game_mode}
                            if send_request_to_server(conn, pkg):
                                Client_stats.client_state = "lobby"
                        elif i == 2:
                            with info_lock:
                                Client_stats.client_state = "enter_lobby_id"
                            Client_stats.entered_lobby_id = ""
                    elif Client_stats.client_state == "enter_lobby_id":
                        # Optionally, could have a button to confirm entry
                        pass
    return inputs, shoots
def update_and_render():
    global running, game_over, winning_team, losing_team, client_state, lobby_id, input_text, entered_lobby_id, error_message, error_message_time, client_state, countdown_value, username, game_over, winning_team, losing_team, client_state, lobby_id, error_message, error_message_time, countdown_value
    mouse_pos = pygame.mouse.get_pos()
    option_rects = []
    if Client_stats.game_over:
        draw_game_over(screen, Client_stats.winning_team, Client_stats.losing_team)
        pygame.display.flip()
        time.sleep(2)
        with info_lock:
            Client_stats.game_over = False  # Reset for next game
            print(Client_stats.lobby_id)
            if Client_stats.lobby_id:
                Client_stats.client_state = "lobby"
            else:
                Client_stats.client_state = "menu"
    elif Client_stats.client_state == "in_game":
        draw_game_state(screen, game_lock, game_state, previous_game_state, last_update_time, network_interval, fighter_animations, client_anim_states, images)
    elif Client_stats.client_state in ["searching", "waiting"]:
        draw_waiting_screen(screen)
    elif Client_stats.client_state == "lobby":
        draw_lobby_screen(screen, Client_stats.lobby_id)
    elif Client_stats.client_state == "typing_room_id":
        draw_menu_screen(screen)
        font = pygame.font.Font(None, 50)
        text_surface = font.render("Enter Room ID: " + Client_stats.input_text, True, (255, 255, 255))
        screen.blit(text_surface, (400, 300))
    elif Client_stats.client_state == "menu":
        option_rects = draw_menu_screen(screen, mouse_pos)
    elif Client_stats.client_state == "enter_lobby_id":
        draw_enter_lobby_screen(screen, Client_stats.entered_lobby_id, Client_stats.error_message)
        if Client_stats.error_message and Client_stats.error_message_time and (time.time() - Client_stats.error_message_time > 2):
            Client_stats.error_message = None
            Client_stats.error_message_time = None
            Client_stats.client_state = "menu"
        font = pygame.font.Font(None, 50)
        text_surface = font.render("Enter Room ID: " + Client_stats.entered_lobby_id, True, (255, 255, 255))
        screen.blit(text_surface, (400, 300))
    elif Client_stats.client_state == "select_game_mode":
        option_rects = draw_game_mode_screen(screen, mouse_pos)
    elif Client_stats.client_state == "countdown": # change it, it means showing paused game
        draw_countdown_screen(screen, Client_stats.countdown_value)
    elif Client_stats.client_state == "enter_username":
        draw_enter_username_screen(screen, Client_stats.username)
    else:
        print("Unknown client_state:", Client_stats.client_state)
        draw_waiting_screen(screen)
    if Client_stats.error_message and Client_stats.error_message_time and Client_stats.client_state != "enter_lobby_id" and (time.time() - Client_stats.error_message_time > 3):
        Client_stats.error_message = None
        Client_stats.error_message_time = None
    
    pygame.display.flip()
    clock.tick(60)
    return option_rects
def main():
    global conn, Client_stats
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
        received_id = pickle.loads(client_id_data)
        Client_stats.client_id = received_id
        pygame.display.set_caption("Client: " + str(Client_stats.client_id))
        print("Connected to server. Your client ID is:", Client_stats.client_id)
    except Exception as e:
        print("Error receiving client ID:", e)
        conn.close()
        return

    recv_thread = threading.Thread(target=threaded_receive_update, args=(conn,))
    recv_thread.daemon = True
    recv_thread.start()

    while Client_stats.running:
        option_rects = update_and_render()
        inputs, shoots = handle_input(option_rects)
        #print(stats.client_state)
        # print(stats.lobby_id)
        if (inputs or shoots) and Client_stats.client_state == "in_game" and not Client_stats.game_over:
            client_package = {
                "client_id": Client_stats.client_id,
                "request_type": "input",
                "game_mode": Client_stats.game_mode,
                "inputs": inputs,
                "shoots": shoots
            }
            send_request_to_server(conn, client_package)

    Client_stats.running = False
    conn.close()
    pygame.quit()
    print("Connection closed and Pygame quit.")

if __name__ == "__main__":
    main()