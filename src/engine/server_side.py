from _thread import * # For threading, to handle multiple clients at once
from src.engine.server_classes import Client, Lobby, Game  # <-- new import
import pickle  # To serialize Python objects to send over the network
import time  # added for game world update timing
from src.config.server_config import create_server_socket  # New import for server configuration
import threading
from src.engine.server_helper import generate_unique_client_id, broadcast, send_to_client  # <-- updated import
import traceback

# There is no mechanism to clean up threads or games when clients disconnect but we can fix it later now we need a minimal functioning server and client that can play a 1vs1 game.
def threaded_client(conn):
    global pending_requests, all_games, all_lobbies
    client_id = generate_unique_client_id()
    client = Client(client_id, conn)
    with shared_lock:
        all_clients.append(client)
    try:
        conn.sendall(pickle.dumps(client_id)) # sends clients ID as a first time massage
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
            print(f" request recived: {request_type} ")
            # handle requests based on their type:
            if request_type == "input":  # Append the client's package to game_updates if it is input.  
                with shared_lock:
                    for game in all_games:
                        if game.game_id == client.connected_game_id:
                            game.game_updates.append(client_package)
            else:
                with shared_lock:
                    pending_requests.append((client, client_package))  # Pass client object for context

        except Exception as e:
            print(f"Exception in threaded_client for {client_id}: {e}")
            traceback.print_exc()
            break

    print(f"{client_id} Lost connection")

    with shared_lock:
        # Remove client safely
        for i, c in enumerate(all_clients):
            if c.client_id == client_id:
                del all_clients[i]
                break
    try:
        conn.close()
    except Exception as e:
        print(f"Error closing connection for {client_id}: {e}")
        traceback.print_exc()
def threaded_game(game):# it sees only the game_updates then Processes the pending game changes then sends it to all clients, input and shooting
    while True:
        try:
            game.update()
            server_package = {
                "request_type": "game_update",
                "platforms": game.platforms,
                "fighters": game.fighters,
                "projectiles": game.projectiles, 
                "power_ups": game.power_ups, 
                "sounds": []
                }
        
            if game.mode == "1vs1":
                with shared_lock:
                    broadcast(server_package, game.game_clients, all_clients)
            else:
                with shared_lock:
                    broadcast(server_package, game.game_clients, all_clients)
    
            if game.finished:
                with shared_lock:
                    if game in all_games:
                        all_games.remove(game)
                break
        
            time.sleep(0.05)
        except Exception as e:
            print(f"Exception in threaded_game {game.game_id}: {e}")
            traceback.print_exc()
            break
def threaded_handle_waiting_clients(): # actively reads waiting_clients if a game is possible creates it and adds it to all_games
    global waiting_clients, all_games , all_clients
    while True:
        try:
            with shared_lock:
                # Find possible 1vs1 games
                one_vs_one_clients = [cid for cid, mode in waiting_clients.items() if mode == "1vs1"]
                #print (f" number of one_vs_one_clients: {len(one_vs_one_clients)}")
                while len(one_vs_one_clients) >= 2:
                    ids = one_vs_one_clients[:2]

                    game_id = "_".join(ids)
                    print (f"game id:  {game_id}")

                    new_game = Game(game_id, "1vs1", ids[0], ids[1])
                    all_games.append(new_game)
                    
                    # Remove clients from waiting_clients
                    for cid in ids:
                        waiting_clients.pop(cid, None)
                    # Start game thread
                    start_new_thread(threaded_game, (new_game,))
                    # Update connected_game_id for clients
                    for c in all_clients:
                        if c.client_id in ids:
                            c.connected_game_id = game_id
                    # Notify clients
                    for cid in ids:
                        send_to_client({"request_type": "game_started", "game_id": game_id, "members": ids}, cid, all_clients)
                    # Update list for next iteration
                    one_vs_one_clients = [cid for cid, mode in waiting_clients.items() if mode == "1vs1"]

                # Find possible 2vs2 games
                two_vs_two_clients = [cid for cid, mode in waiting_clients.items() if mode == "2vs2"]
                while len(two_vs_two_clients) >= 4:
                    ids = two_vs_two_clients[:4]
                    game_id = "_".join(ids)
                    new_game = Game(game_id, "2vs2", ids[0], ids[1], ids[2], ids[3])
                    all_games.append(new_game)
                    # Remove clients from waiting_clients
                    for cid in ids:
                        waiting_clients.pop(cid, None)
                    # Start game thread
                    start_new_thread(threaded_game, (new_game,))
                    # Update connected_game_id for clients
                    for c in all_clients:
                        if c.client_id in ids:
                            c.connected_game_id = game_id
                    # Notify clients
                    for cid in ids:
                        send_to_client({"request_type": "game_started", "game_id": game_id, "members": ids}, cid, all_clients)
                    # Update list for next iteration
                    two_vs_two_clients = [cid for cid, mode in waiting_clients.items() if mode == "2vs2"]
            time.sleep(0.1) # avoid busy loop
        except Exception as e:
            print(f"Exception in threaded_handle_waiting_clients: {e}")
            traceback.print_exc()
            time.sleep(0.1)
def threaded_handle_general_request(): # need more details
    global pending_requests, all_lobbies, all_games, waiting_clients
    while True:
        try:
            with shared_lock:
                if not pending_requests:
                    time.sleep(0.05)
                    continue
                client, client_package = pending_requests.pop(0)
                print (client_package)

            request_type = client_package["request_type"]

            if request_type == "find_random_game":
                with shared_lock:
                    if not client_package["client_id"] in waiting_clients:
                        waiting_clients[client_package["client_id"]] = client_package["game_mode"]
                    

            elif request_type == "join_lobby":
                with shared_lock:
                    if client.connected_lobby_id == "":
                        for lobby in all_lobbies:
                            if client_package["room_id"] == lobby.lobby_id:
                                lobby.add_member(client.client_id)
                                client.connected_lobby_id = client_package["room_id"]

            elif request_type == "make_lobby":
                with shared_lock:
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
                with shared_lock:
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
                        all_games.append(new_game)
                        for cid in ids:
                            for c in all_clients:
                                if c.client_id == cid:
                                    c.connected_game_id = game_id
                        for cid in ids:
                            send_to_client({"request_type": "game_started", "game_id": game_id, "members": ids}, cid, all_clients)
                        all_lobbies.remove(lobby)
            # ...add more request types as needed...
            time.sleep(0.05)
        except Exception as e:
            print(f"Exception in threaded_handle_general_request: {e}")
            traceback.print_exc()
            time.sleep(0.05)

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
    "request_type": "game_update", "first_time"

    "game_world":
        "platforms": platforms,
        "fighters": fighters,
        "projectiles": projectiles, 
        "power_ups": power_ups, 
        "sounds": []
}
"""

all_clients = []  # list of Client objects
all_lobbies = []  # connected clients and created lobbies 
all_games   = []  # to track all the current playing games

pending_requests = []  # new global list for client requests that are not input or shoot (client_package)
waiting_clients  = {} 
shared_lock = threading.Lock()

s = create_server_socket()
start_new_thread(threaded_handle_general_request, ())  # Start the request handler thread
start_new_thread(threaded_handle_waiting_clients, ())
while True:
    try:
        conn, addr = s.accept()# The accept() method blocks until a client connects. It returns a new connection object (conn) and the client's address (addr).
        print("Connected to:", addr)
        start_new_thread(threaded_client, (conn,)) # When a client connects, we start a new thread for them with a new generated ID. This allows the server to handle multiple clients simultaneously without blocking
    except Exception as e:
        print(f"Exception in main server loop: {e}")
        traceback.print_exc()




