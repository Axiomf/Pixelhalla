from _thread import * # For threading, to handle multiple clients at once
from src.engine.server_classes import Client, Lobby, Game  # <-- new import
import pickle  # To serialize Python objects to send over the network
import time  # added for game world update timing
from src.config.server_config import create_server_socket  # New import for server configuration
import threading
from src.engine.server_helper import generate_unique_client_id, broadcast, send_to_client  # <-- updated import
import traceback
#import pygame  # Add pygame if needed for accessing Rect
import queue  # new import for pending requests
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
# Updated helper to include sprite color in serialized data.
def serialize_group(group, type):
    
    serialized = []
    for sprite in group.sprites():
        serialized.append({
            "rect": (sprite.rect.x, sprite.rect.y),  # modified: only x and y coordinates
            "state": getattr(sprite, "state", "idle"),
            "id": getattr(sprite, "fighter_id", "id not given"),
            "is_doing": getattr(sprite, "is_doing", "is_doing not given"),  # cycle animations info
            "facing_right": getattr(sprite, "facing_right", True),
            #"type": type
        })
    return serialized

def threaded_game(game):
    target_frame_duration = 1.0 / 60
    while True:
        start_time = time.perf_counter()
        try:
            game.update()
            server_package = {
                "request_type": "game_update",
                "game_world": {
                    "platforms": serialize_group(game.platforms,"platform"),
                    "fighters": serialize_group(game.fighters,"fighter"),
                    "projectiles": serialize_group(game.projectiles,"projectile"),
                    "power_ups": serialize_group(game.power_ups,"power_up"),
                    "sounds": game.sounds
                }
            }
            game.sounds = [] # Clear the sounds list
            # print(f"Sending server_package: {server_package}")
            with clients_lock:
                broadcast(server_package, game.game_clients, all_clients)
    
            if game.finished:
                with games_lock:
                    if game in all_games:
                        all_games.remove(game)
                break
        except Exception as e:
            # print(f"Exception in threaded_game {game.game_id}: {e}")
            traceback.print_exc()
            break
        next_frame_time = start_time + target_frame_duration
        sleep_time = next_frame_time - time.perf_counter()
        if sleep_time > 0:
            time.sleep(sleep_time)

# There is no mechanism to clean up threads or games when clients disconnect but we can fix it later now we need a minimal functioning server and client that can play a 1vs1 game.
def threaded_client(conn):
    global pending_requests, all_games, all_lobbies
    client_id = generate_unique_client_id()
    client = Client(client_id, conn)
    with clients_lock:  # replaced shared_lock
        all_clients.append(client)
    try:
        conn.sendall(pickle.dumps(client_id)) # sends clients ID as a first time massage
    except Exception as e:
        # print(f"Error sending client ID to {client_id}: {e}")
        traceback.print_exc()
        return

    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            client_package = pickle.loads(data)
            request_type = client_package["request_type"]
            # Removed per-request logging to reduce overhead
            # print(f" request recived: {request_type} ")
            # handle requests based on their type:
            if request_type == "input":  # Append the client's package to game_updates if it is input.  
                with games_lock:  # replaced shared_lock for game updates
                    for game in all_games:
                        if game.game_id == client.connected_game_id:
                            game.game_updates.append(client_package)
            else:
                pending_requests.put((client, client_package))
        except Exception as e:
            # print(f"Exception in threaded_client for {client_id}: {e}")
            traceback.print_exc()
            break

    # print(f"{client_id} Lost connection")
    with clients_lock:
        for i, c in enumerate(all_clients):
            if c.client_id == client_id:
                del all_clients[i]
                break
    try:
        conn.close()
    except Exception as e:
        # print(f"Error closing connection for {client_id}: {e}")
        traceback.print_exc()


def threaded_handle_waiting_clients():
    global waiting_clients, all_games, all_clients
    while True:
        try:
            with waiting_clients_lock:
                one_vs_one_clients = [cid for cid, mode in waiting_clients.items() if mode == "1vs1"]
                # print(f"1vs1 clients waiting: {one_vs_one_clients}")
                while len(one_vs_one_clients) >= 2:
                    ids = one_vs_one_clients[:2]
                    game_id = "_".join(ids)
                    # print(f"Creating game: {game_id}")
                    new_game = Game(game_id, "1vs1", ids[0], ids[1])
                    with games_lock:
                        all_games.append(new_game)
                    for cid in ids:
                        waiting_clients.pop(cid, None)
                    start_new_thread(threaded_game, (new_game,))
                    with clients_lock:
                        for c in all_clients:
                            if c.client_id in ids:
                                c.connected_game_id = game_id
                    for cid in ids:
                        # print(f"Sending game_started to {cid}")
                        send_to_client({"request_type": "game_started", "game_id": game_id, "members": ids}, cid, all_clients)
                    one_vs_one_clients = [cid for cid, mode in waiting_clients.items() if mode == "1vs1"]

                two_vs_two_clients = [cid for cid, mode in waiting_clients.items() if mode == "2vs2"]
                while len(two_vs_two_clients) >= 4:
                    ids = two_vs_two_clients[:4]
                    game_id = "_".join(ids)
                    new_game = Game(game_id, "2vs2", ids[0], ids[1], ids[2], ids[3])
                    with games_lock:
                        all_games.append(new_game)
                    for cid in ids:
                        waiting_clients.pop(cid, None)
                    start_new_thread(threaded_game, (new_game,))
                    with clients_lock:
                        for c in all_clients:
                            if c.client_id in ids:
                                c.connected_game_id = game_id
                    for cid in ids:
                        # print(f"Sending game_started to {cid}")
                        send_to_client({"request_type": "game_started", "game_id": game_id, "members": ids}, cid, all_clients)
                    two_vs_two_clients = [cid for cid, mode in waiting_clients.items() if mode == "2vs2"]
            time.sleep(0.2)
        except Exception as e:
            # print(f"Exception in threaded_handle_waiting_clients: {e}")
            traceback.print_exc()
            time.sleep(0.2)

def threaded_handle_general_request():
    global all_lobbies, all_games, waiting_clients
    while True:
        try:
            client, client_package = pending_requests.get(timeout=0.1)
            request_type = client_package["request_type"]
            # print(f"Processing request: {client_package}")
            if request_type == "find_random_game":
                with waiting_clients_lock:
                    if client_package["client_id"] not in waiting_clients:
                        waiting_clients[client_package["client_id"]] = client_package["game_mode"]
                        # print(f"Added to waiting clients: {client_package['client_id']}")
                        
            elif request_type == "join_lobby":
                with clients_lock, lobbies_lock:
                    if client.connected_lobby_id == "":
                        for lobby in all_lobbies:
                            if client_package["room_id"] == lobby.lobby_id:
                                lobby.add_member(client.client_id)
                                client.connected_lobby_id = client_package["room_id"]
            elif request_type == "make_lobby":
                with clients_lock, lobbies_lock:
                    if client.connected_lobby_id == "":
                        lobby_id = client_package.get("client_id")
                        game_mode = client_package.get("game_mode")
                        new_lobby = Lobby(lobby_id, client.client_id, game_mode)
                        all_lobbies.append(new_lobby)
                        client.connected_lobby_id = lobby_id
                        client.is_host = True
                        client.game_mode = game_mode
                        send_to_client({"request_type": "lobby_created", "lobby_id": lobby_id, "game_mode": game_mode}, client.client_id, all_clients)
            elif request_type == "start_the_game_as_host":
                lobby = None
                with lobbies_lock:
                    for l in all_lobbies:
                        if l.lobby_id == client.connected_lobby_id and l.is_host(client.client_id):
                            lobby = l
                            break
                if lobby and lobby.state == "full":
                    game_id = lobby.lobby_id
                    ids = lobby.members
                    game_mode = lobby.game_mode
                    if game_mode == "1vs1":
                        new_game = Game(game_id, game_mode, ids[0], ids[1])
                    else:
                        if len(ids) < 4:
                            continue
                        new_game = Game(game_id, game_mode, ids[0], ids[1], ids[2], ids[3])
                    with games_lock:
                        all_games.append(new_game)
                    with clients_lock:
                        for cid in ids:
                            for c in all_clients:
                                if c.client_id == cid:
                                    c.connected_game_id = game_id
                    for cid in ids:
                        # print(f"Sending game_started to {cid}")
                        send_to_client({"request_type": "game_started", "game_id": game_id, "members": ids}, cid, all_clients)
                    with lobbies_lock:
                        if lobby in all_lobbies:
                            all_lobbies.remove(lobby)
                # Start game thread
                start_new_thread(threaded_game, (new_game,))
        except queue.Empty:
            continue
        except Exception as e:
            # print(f"Exception in threaded_handle_general_request: {e}")
            traceback.print_exc()
            time.sleep(0.5)

all_clients = []
all_lobbies = []
all_games = []
pending_requests = queue.Queue()
waiting_clients = {}

clients_lock = threading.Lock()
games_lock = threading.Lock()
lobbies_lock = threading.Lock()
waiting_clients_lock = threading.Lock()

s = create_server_socket()
start_new_thread(threaded_handle_general_request, ())
start_new_thread(threaded_handle_waiting_clients, ())
while True:
    try:
        conn, addr = s.accept()
        print("Connected to:", addr)
        start_new_thread(threaded_client, (conn,))
    except Exception as e:
        print(f"Exception in main server loop: {e}")
        traceback.print_exc()