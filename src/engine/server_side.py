from _thread import * # For threading, to handle multiple clients at once
from src.engine.server_classes import Client, Lobby, Game  # <-- new import
import pickle  # To serialize Python objects to send over the network
import time  # added for game world update timing
from src.config.server_config import create_server_socket  # New import for server configuration
import threading
from src.engine.server_helper import generate_unique_client_id, broadcast, send_to_client,serialize_fighters, serialize_projectiles, serialize_power_ups, serialize_platforms
import traceback
import queue  # new import for pending requests
import pygame

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

def handle_game_finished(game):
    losing_team = 2 if game.winning_team == 1 else 1
    game_over_package = {
        "request_type": "game_finished",
        "winning_team": game.winning_team,
        "losing_team": losing_team,
        "game_id": game.game_id
    }
    print(f"Game finished: winning_team={game.winning_team}, losing_team={losing_team}")
    with clients_lock:
        broadcast(game_over_package, game.game_clients, all_clients)
        for client in all_clients:
            if client.client_id in game.game_clients:
                client.connected_game_id = ""  # Clear game ID
                client.state = "lobby" if client.connected_lobby_id else "menu"  # Return to lobby if in one
    with games_lock:
        if game in all_games:
            all_games.remove(game)

    # Find the lobby and update its state to allow players to rejoin/start again
    with lobbies_lock, clients_lock:
        lobby_to_update = None
        for l in all_lobbies:
            if l.lobby_id == game.game_id:
                lobby_to_update = l
                break
        
        if lobby_to_update:
            lobby_to_update.state = "waiting"
            info_package = {
                "request_type": "info",
                "lobby_id": lobby_to_update.lobby_id,
                "game_mode": lobby_to_update.game_mode,
                "members": lobby_to_update.members,
                "host_id": lobby_to_update.host_id,
                "lobby_members_id": lobby_to_update.members
            }
            
            for client in all_clients:
                if client.client_id in lobby_to_update.members:
                    client.state = "lobby"
                    client.is_host = (client.client_id == lobby_to_update.host_id)
                    info_package["is_host"] = client.is_host
                    send_to_client(info_package, client.client_id, all_clients)

def threaded_game(game):
    target_frame_duration = 1.0 / 60
    while True:
        start_time = time.perf_counter()
        try:
            game.update()
            if game.finished:
                handle_game_finished(game)
                break
            
            # send game update if not finished
            server_package = {
                "request_type": "game_update",
                "game_world": {
                    "platforms": serialize_platforms(game.platforms),
                    "fighters": serialize_fighters(game.fighters, game.usernames),
                    "projectiles": serialize_projectiles(game.projectiles),
                    "power_ups": serialize_power_ups(game.power_ups),
                    "sounds": game.sounds
                }
            }
            game.sounds = []
            with clients_lock:
                broadcast(server_package, game.game_clients, all_clients)
        except Exception as e:
            print(f"Exception in threaded_game {game.game_id}: {e}")
            traceback.print_exc()
            break
        next_frame_time = start_time + target_frame_duration
        sleep_time = next_frame_time - time.perf_counter()
        if sleep_time > 0:
            time.sleep(sleep_time)

def handle_client_disconnection(client, conn):
    global all_clients, all_lobbies, all_games, waiting_clients
    client_id = client.client_id
    print(f"Client {client_id} disconnected")
    with clients_lock:
        # Remove from all_clients
        for i, c in enumerate(all_clients):
            if c.client_id == client_id:
                del all_clients[i]
                break

        # Remove from lobby if in one
        with lobbies_lock:
            for lobby in list(all_lobbies):
                if client_id in lobby.members:
                    lobby.remove_member(client_id)
                    if lobby.is_host(client_id):
                        client_ids_in_lobby = list(lobby.members)
                        for cid in client_ids_in_lobby:
                            for c in all_clients:
                                if c.client_id == cid:
                                    c.connected_lobby_id = ""
                                    c.is_host = False
                                    c.state = "menu"
                        broadcast({"request_type": "lobby_destroyed"}, client_ids_in_lobby, all_clients)
                        print(f"Lobby {lobby.lobby_id} destroyed due to host {client_id} disconnection")
                        all_lobbies.remove(lobby)
                    else:
                        broadcast({"request_type": "client_disconnected", "client_id": client_id}, lobby.members, all_clients)
                    break

        # Remove from game if in one
        with games_lock:
            for game in all_games:
                if client_id in game.game_clients:
                    game.handle_client_disconnect(client_id)
                    break

        # Remove from waiting_clients if in waiting room
        with waiting_clients_lock:
            if client_id in waiting_clients:
                waiting_clients.pop(client_id, None)
                print(f"Client {client_id} removed from waiting_clients")

    try:
        conn.close()
    except Exception as e:
        print(f"Error closing connection for {client_id}: {e}")
        traceback.print_exc()

def threaded_client(conn):
    global pending_requests, all_games, all_lobbies, waiting_clients
    client_id = generate_unique_client_id()
    client = Client(client_id, conn)
    with clients_lock:
        all_clients.append(client)
    try:
        conn.sendall(pickle.dumps(client_id))
    except Exception as e:
        print(f"Error sending client ID to {client_id}: {e}")
        traceback.print_exc()
        return

    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            client_package = pickle.loads(data)
            request_type = client_package["request_type"]
            if request_type == "input":
                with games_lock:
                    for game in all_games:
                        if game.game_id == client.connected_game_id:
                            game.game_updates.append(client_package)
            elif request_type == "set_username":
                with clients_lock:
                    for c in all_clients:
                        if c.client_id == client_package["client_id"]:
                            c.username = client_package["username"]
                            print(f"Username set for {client_id}: {client_package['username']}")
                            break
            else:
                pending_requests.put((client, client_package))
        except Exception as e:
            print(f"Exception in threaded_client for {client_id}: {e}")
            traceback.print_exc()
            break

    # Handle client disconnection (refactored)
    handle_client_disconnection(client, conn)
    return

def threaded_handle_waiting_clients():
    global waiting_clients, all_games, all_clients
    while True:
        try:
            with waiting_clients_lock:
                one_vs_one_clients = [cid for cid, mode in waiting_clients.items() if mode == "1vs1"]
                while len(one_vs_one_clients) >= 2:
                    ids = one_vs_one_clients[:2]
                    game_id = "_".join(ids)
                    # Get usernames for the clients
                    usernames = {}
                    with clients_lock:
                        for cid in ids:
                            for c in all_clients:
                                if c.client_id == cid:
                                    usernames[cid] = c.username if hasattr(c, 'username') else "Unknown"
                                    break
                    new_game = Game(game_id, "1vs1", ids[0], ids[1], usernames=usernames)
                    with games_lock:
                        all_games.append(new_game)
                    for cid in ids:
                        waiting_clients.pop(cid, None)
                    with clients_lock:
                        for c in all_clients:
                            if c.client_id in ids:
                                c.connected_game_id = game_id
                                c.state = "countdown"
                    # Start countdown
                    for i in range(3, 0, -1):
                        countdown_package = {"request_type": "countdown", "count": i}
                        broadcast(countdown_package, ids, all_clients)
                        time.sleep(1)
                    # Send game start
                    for cid in ids:
                        send_to_client({"request_type": "game_started", "game_id": game_id, "members": ids}, cid, all_clients)
                    start_new_thread(threaded_game, (new_game,))
                    one_vs_one_clients = [cid for cid, mode in waiting_clients.items() if mode == "1vs1"]

                two_vs_two_clients = [cid for cid, mode in waiting_clients.items() if mode == "2vs2"]
                while len(two_vs_two_clients) >= 4:
                    ids = two_vs_two_clients[:4]
                    game_id = "_".join(ids)
                    # Get usernames for the clients
                    usernames = {}
                    with clients_lock:
                        for cid in ids:
                            for c in all_clients:
                                if c.client_id == cid:
                                    usernames[cid] = c.username if hasattr(c, 'username') else "Unknown"
                                    break
                    new_game = Game(game_id, "2vs2", ids[0], ids[1], ids[2], ids[3], usernames=usernames)
                    with games_lock:
                        all_games.append(new_game)
                    for cid in ids:
                        waiting_clients.pop(cid, None)
                    with clients_lock:
                        for c in all_clients:
                            if c.client_id in ids:
                                c.connected_game_id = game_id
                                c.state = "countdown"
                    # Start countdown
                    for i in range(3, 0, -1):
                        countdown_package = {"request_type": "countdown", "count": i}
                        broadcast(countdown_package, ids, all_clients)
                        time.sleep(1)
                    # Send game start
                    for cid in ids:
                        send_to_client({"request_type": "game_started", "game_id": game_id, "members": ids}, cid, all_clients)
                    start_new_thread(threaded_game, (new_game,))
                    two_vs_two_clients = [cid for cid, mode in waiting_clients.items() if mode == "2vs2"]
            time.sleep(0.2)
        except Exception as e:
            print(f"Exception in threaded_handle_waiting_clients: {e}")
            traceback.print_exc()
            time.sleep(0.2)
def threaded_handle_general_request():
    global all_lobbies, all_games, waiting_clients
    while True:
        try:
            client, client_package = pending_requests.get(timeout=0.1)
            request_type = client_package["request_type"]
            
            if request_type == "find_random_game":
                with waiting_clients_lock:
                    if client_package["client_id"] not in waiting_clients:
                        waiting_clients[client_package["client_id"]] = client_package["game_mode"]
            elif request_type == "join_lobby":
                lobby_joined = None
                with clients_lock, lobbies_lock:
                    if client.connected_lobby_id == "":
                        print(1)
                        lobby_found = False
                        for lobby in all_lobbies:
                            print(2)
                            if client_package["room_id"] == lobby.lobby_id and lobby.state == "waiting" and lobby.game_mode == client_package["game_mode"]:
                                if lobby.state == "waiting":
                                    print(3)
                                if lobby.add_member(client.client_id):
                                    print(4) # it dosen't reach here
                                        client.connected_lobby_id = client_package["room_id"]
                                    client.state = "lobby"
                                        lobby_joined = lobby
                                    print(lobby_joined)
                #print(lobby_joined) # it gives None 
                print("wtf man")
                if lobby_joined:
                    print(f"Joined lobby: {lobby_joined.lobby_id}")
                    print(lobby_joined)
                    info_package = {
                        "request_type": "info", 
                        "lobby_id": lobby_joined.lobby_id, 
                        "game_mode": lobby_joined.game_mode, 
                        "members": lobby_joined.members, 
                        "host_id": lobby_joined.lobby_id,
                        "is_host": False, 
                        "lobby_members_id": lobby_joined.members
                    }
                    with clients_lock:
                        broadcast(info_package, lobby_joined.members, all_clients)
                else:
                    send_to_client({"request_type": "lobby_not_found"}, client.client_id, all_clients)

                                    lobby_found = True
                                    break
                        if not lobby_found:
                            send_to_client({"request_type": "lobby_join_failed", "message": "Lobby not found or game mode mismatch"}, client.client_id, all_clients)
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
                        info_package = {
                            "request_type": "info", 
                            "lobby_id": lobby_id, 
                            "game_mode": game_mode, 
                            "members": new_lobby.members, 
                            "host_id": new_lobby.host_client_id,
                            "is_host": True, 
                            "lobby_members_id": new_lobby.members
                        }
                        send_to_client(info_package, client.client_id, all_clients)
            elif request_type == "destroy_lobby":
                lobby_to_remove = None
                with clients_lock, lobbies_lock:
                    for lobby in all_lobbies:
                        if lobby.is_host(client.client_id):
                            lobby_to_remove = lobby
                            break
                    if lobby_to_remove:
                        client_ids_in_lobby = list(lobby_to_remove.members)
                        for cid in client_ids_in_lobby:
                            for c in all_clients:
                                if c.client_id == cid:
                                    c.connected_lobby_id = ""
                                    c.is_host = False
                                    c.state = "menu"
                        broadcast({"request_type": "lobby_destroyed"}, client_ids_in_lobby, all_clients)
                        all_lobbies.remove(lobby_to_remove)
                        print(f"Lobby {lobby_to_remove.lobby_id} destroyed by host {client.client_id}")
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
                    # Get usernames for the clients
                    usernames = {}
                    with clients_lock:
                        for cid in ids:
                            for c in all_clients:
                                if c.client_id == cid:
                                    usernames[cid] = c.username if hasattr(c, 'username') else "Unknown"
                                    break
                    if game_mode == "1vs1":
                        new_game = Game(game_id, game_mode, ids[0], ids[1], usernames=usernames)
                    else:
                        if len(ids) < 4:
                            continue
                        new_game = Game(game_id, game_mode, ids[0], ids[1], ids[2], ids[3], usernames=usernames)
                    with games_lock:
                        all_games.append(new_game)
                    with clients_lock:
                        for cid in ids:
                            for c in all_clients:
                                if c.client_id == cid:
                                    c.connected_game_id = game_id
                                    c.state = "countdown"
                    # Start countdown
                    for i in range(3, 0, -1):
                        countdown_package = {"request_type": "countdown", "count": i}
                        broadcast(countdown_package, ids, all_clients)
                        time.sleep(1)
                    # Send game start
                    for cid in ids:
                        send_to_client({"request_type": "game_started", "game_id": game_id, "members": ids}, cid, all_clients)
                    # Do not remove lobby here, keep it for after game ends
                    start_new_thread(threaded_game, (new_game,))
        
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Exception in threaded_handle_general_request: {e}")
            traceback.print_exc()
            time.sleep(0.5)

pygame.init() 
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