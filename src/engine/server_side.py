from _thread import *  # For threading, to handle multiple clients at once
from src.engine.server_classes import Client, Lobby, Game
import pickle  # To serialize Python objects to send over the network
import time  # Added for game world update timing
from src.config.server_config import create_server_socket  # New import for server configuration
import threading
from src.engine.server_helper import generate_unique_client_id, broadcast, send_to_client
import traceback

all_clients = []  # List of Client objects
all_lobbies = []  # Connected clients and created lobbies
all_games = []  # To track all the current playing games
pending_requests = []  # New global list for client requests that are not input or shoot
waiting_clients = {}  # To track clients waiting for a random game
shared_lock = threading.Lock()

def threaded_client(conn):
    """Handle individual client connection."""
    global pending_requests, all_games, all_lobbies
    client_id = generate_unique_client_id()
    client = Client(client_id, conn)
    with shared_lock:
        all_clients.append(client)
        print(f"Added client {client_id} to all_clients")
    try:
        conn.sendall(pickle.dumps(client_id))  # Send client ID as first message
        print(f"Sent client_id to {client_id}: {client_id}")
    except Exception as e:
        print(f"Error sending client ID to {client_id}: {e}")
        traceback.print_exc()
        return

    while True:
        try:
            data = conn.recv(4096)
            if not data:
                print(f"Client {client_id} disconnected")
                break
            client_package = pickle.loads(data)
            print(f"Received request from client {client_id}: {client_package}")
            request_type = client_package["request_type"]

            # Handle requests based on their type
            if request_type == "input":  # Append the client's package to game_updates if it is input
                with shared_lock:
                    for game in all_games:
                        if game.game_id == client.connected_game_id:
                            game.game_updates.append(client_package)
                            print(f"Appended input for game {game.game_id}: {client_package}")
            else:
                with shared_lock:
                    pending_requests.append((client, client_package))  # Pass client object for context
                    print(f"Added to pending_requests: {client_package}")
        except pickle.UnpicklingError as e:
            print(f"Unpickling error for client {client_id}: {e}")
            send_to_client({"request_type": "error", "message": f"Invalid data received: {str(e)}"}, client_id, all_clients)
            break
        except Exception as e:
            print(f"Exception in threaded_client for {client_id}: {e}")
            traceback.print_exc()
            send_to_client({"request_type": "error", "message": f"Server error: {str(e)}"}, client_id, all_clients)
            break

    print(f"{client_id} Lost connection")
    with shared_lock:
        # Remove client safely
        for i, c in enumerate(all_clients):
            if c.client_id == client_id:
                del all_clients[i]
                print(f"Removed client {client_id} from all_clients")
                break
        waiting_clients.pop(client_id, None)
        print(f"Removed client {client_id} from waiting_clients")
    try:
        conn.close()
    except Exception as e:
        print(f"Error closing connection for {client_id}: {e}")

def threaded_handle_general_request():
    """Handle general requests from clients."""
    while True:
        try:
            with shared_lock:
                if not pending_requests:
                    time.sleep(0.05)
                    continue
                client, client_package = pending_requests.pop(0)
                client_id = client.client_id
                print(f"Processing request from client {client_id}: {client_package}")
                request_type = client_package.get("request_type")

                if request_type == "find_random_game":
                    waiting_clients[client_id] = client_package["game_mode"]
                    print(f"Added client {client_id} to waiting_clients with mode {client_package['game_mode']}")
                    # Check for 1vs1 match
                    one_vs_one_clients = [cid for cid, mode in waiting_clients.items() if mode == "1vs1"]
                    if len(one_vs_one_clients) >= 2:
                        ids = one_vs_one_clients[:2]
                        game_id = "_".join(ids)
                        new_game = Game(game_id, "1vs1", ids[0], ids[1])
                        all_games.append(new_game)
                        print(f"Created game {game_id} with clients {ids}")
                        for cid in ids:
                            waiting_clients.pop(cid, None)
                            print(f"Removed client {cid} from waiting_clients for game {game_id}")
                        for c in all_clients:
                            if c.client_id in ids:
                                c.connected_game_id = game_id
                                print(f"Set connected_game_id for client {c.client_id} to {game_id}")
                        for cid in ids:
                            try:
                                send_to_client({"request_type": "game_started", "game_id": game_id, "members": ids}, cid, all_clients)
                                print(f"Sent game_started to {cid}: {{'request_type': 'game_started', 'game_id': '{game_id}', 'members': {ids}}}")
                            except Exception as e:
                                print(f"Failed to send game_started to {cid}: {e}")
                                send_to_client({"request_type": "error", "message": f"Failed to start game: {str(e)}"}, cid, all_clients)
                        start_new_thread(new_game.update, ())
                    # Check for 2vs2 match
                    two_vs_two_clients = [cid for cid, mode in waiting_clients.items() if mode == "2vs2"]
                    if len(two_vs_two_clients) >= 4:
                        ids = two_vs_two_clients[:4]
                        game_id = "_".join(ids)
                        new_game = Game(game_id, "2vs2", ids[0], ids[1], ids[2], ids[3])
                        all_games.append(new_game)
                        print(f"Created game {game_id} with clients {ids}")
                        for cid in ids:
                            waiting_clients.pop(cid, None)
                            print(f"Removed client {cid} from waiting_clients for game {game_id}")
                        for c in all_clients:
                            if c.client_id in ids:
                                c.connected_game_id = game_id
                                print(f"Set connected_game_id for client {c.client_id} to {game_id}")
                        for cid in ids:
                            try:
                                send_to_client({"request_type": "game_started", "game_id": game_id, "members": ids}, cid, all_clients)
                                print(f"Sent game_started to {cid}: {{'request_type': 'game_started', 'game_id': '{game_id}', 'members': {ids}}}")
                            except Exception as e:
                                print(f"Failed to send game_started to {cid}: {e}")
                                send_to_client({"request_type": "error", "message": f"Failed to start game: {str(e)}"}, cid, all_clients)
                        start_new_thread(new_game.update, ())
                elif request_type == "make_lobby":
                    lobby_id = client_package["room_id"]
                    game_mode = client_package["game_mode"]
                    new_lobby = Lobby(lobby_id, client_id, game_mode)
                    all_lobbies.append(new_lobby)
                    client.connected_lobby_id = lobby_id
                    client.is_host = True
                    print(f"Client {client_id} created lobby {lobby_id} with mode {game_mode}")
                    send_to_client({"request_type": "lobby_created", "lobby_id": lobby_id, "members": [client_id]}, client_id, all_clients)
                elif request_type == "join_lobby":
                    lobby_id = client_package["room_id"]
                    for lobby in all_lobbies:
                        if lobby.lobby_id == lobby_id and lobby.state != "full":
                            lobby.add_member(client_id)
                            client.connected_lobby_id = lobby_id
                            print(f"Client {client_id} joined lobby {lobby_id}")
                            send_to_client({"request_type": "lobby_joined", "lobby_id": lobby_id, "members": lobby.members}, client_id, all_clients)
                            broadcast({"request_type": "lobby_update", "lobby_id": lobby_id, "members": lobby.members}, lobby.members, all_clients)
                            break
                    else:
                        send_to_client({"request_type": "error", "message": "Lobby not found or full"}, client_id, all_clients)
                elif request_type == "start_the_game_as_host":
                    for lobby in all_lobbies:
                        if lobby.lobby_id == client.connected_lobby_id and lobby.is_host(client_id):
                            ids = lobby.members
                            game_id = "_".join(ids)
                            game_mode = lobby.game_mode
                            new_game = Game(game_id, game_mode, *ids)
                            all_games.append(new_game)
                            print(f"Created game {game_id} with clients {ids}")
                            for cid in ids:
                                for c in all_clients:
                                    if c.client_id == cid:
                                        c.connected_game_id = game_id
                                        print(f"Set connected_game_id for client {c.client_id} to {game_id}")
                            for cid in ids:
                                try:
                                    send_to_client({"request_type": "game_started", "game_id": game_id, "members": ids}, cid, all_clients)
                                    print(f"Sent game_started to {cid}: {{'request_type': 'game_started', 'game_id': '{game_id}', 'members': {ids}}}")
                                except Exception as e:
                                    print(f"Failed to send game_started to {cid}: {e}")
                                    send_to_client({"request_type": "error", "message": f"Failed to start game: {str(e)}"}, cid, all_clients)
                            all_lobbies.remove(lobby)
                            print(f"Removed lobby {lobby.lobby_id} after starting game")
                            start_new_thread(new_game.update, ())
                            break
            time.sleep(0.05)
        except Exception as e:
            print(f"Exception in threaded_handle_general_request: {e}")
            traceback.print_exc()
            time.sleep(0.05)

s = create_server_socket()
start_new_thread(threaded_handle_general_request, ())  # Start the request handler thread
while True:
    try:
        conn, addr = s.accept()
        print("Connected to:", addr)
        start_new_thread(threaded_client, (conn,))  # Start new thread for each client
    except Exception as e:
        print(f"Exception in main server loop: {e}")
        traceback.print_exc()