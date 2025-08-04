import socket
import pickle
import threading
from _thread import start_new_thread

server = "127.0.0.1"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind((server, port))
except socket.error as e:
    print(f"Bind failed: {e}")
    exit()
s.listen(4)
print("Waiting for a connection, Server Started")

clients = []
waiting_players = []
games = {}

def threaded_client(conn, client_id):
    try:
        while True:
            data = pickle.loads(conn.recv(2048))
            print(data)
            print(f"Received request from client {client_id}: {data}")
            if not data:
                break
            request_type = data.get("request_type")
            if request_type == "join":
                print("YES. we are here.")
                waiting_players.append({
                    "client_id": client_id,
                    "conn": conn,
                    "username": data.get("username"),
                    "fighter_id": data.get("fighter_id"),
                    "map_name": data.get("map_name")
                })
                conn.send(pickle.dumps({"request_type": "joined", "client_id": client_id}))
                print(f"Player {client_id} joined waiting room. Waiting players: {len(waiting_players)}")
            elif request_type == "check_match":
                print(f"Checking match for client {client_id}, map: {data.get('map_name')}, Waiting players: {[p['map_name'] for p in waiting_players]}")
                if len(waiting_players) >= 2:
                    player1 = None
                    player2 = None
                    for player in waiting_players:
                        if player["map_name"] == data.get("map_name"):
                            if not player1:
                                player1 = player
                            elif not player2 and player["client_id"] != client_id:
                                player2 = player
                        if player1 and player2:
                            break
                    if player1 and player2:
                        waiting_players.remove(player1)
                        waiting_players.remove(player2)
                        game_id = f"game_{client_id}_{int(threading.get_ident())}"
                        games[game_id] = [player1, player2]
                        response = {
                            "request_type": "matched",
                            "game_id": game_id,
                            "opponent": {
                                "username": player2["username"],
                                "fighter_id": player2["fighter_id"],
                                "map_name": player2["map_name"]
                            }
                        }
                        player1["conn"].send(pickle.dumps(response))
                        player2["conn"].send(pickle.dumps({
                            "request_type": "matched",
                            "game_id": game_id,
                            "opponent": {
                                "username": player1["username"],
                                "fighter_id": player1["fighter_id"],
                                "map_name": player1["map_name"]
                            }
                        }))
                        print(f"Matched players {player1['client_id']} and {player2['client_id']} on map {player1['map_name']}")
                    else:
                        conn.send(pickle.dumps({"request_type": "waiting"}))
                        print(f"No match found for client {client_id}. Waiting players: {[p['map_name'] for p in waiting_players]}")
                else:
                    conn.send(pickle.dumps({"request_type": "waiting"}))
                    print(f"Not enough players for client {client_id}. Waiting players: {[p['map_name'] for p in waiting_players]}")
            elif request_type == "input":
                game_id = data.get("game_id")
                if game_id in games:
                    for player in games[game_id]:
                        if player["client_id"] != client_id:
                            player["conn"].send(pickle.dumps(data))
    except Exception as e:
        print(f"Error in threaded_client for client {client_id}: {e}")
    finally:
        if any(client["client_id"] == client_id for client in clients):
            clients[:] = [client for client in clients if client["client_id"] != client_id]
        if any(player["client_id"] == client_id for player in waiting_players):
            waiting_players[:] = [player for player in waiting_players if player["client_id"] != client_id]
        for game_id in list(games.keys()):
            if any(player["client_id"] == client_id for player in games[game_id]):
                games.pop(game_id, None)
                break
        conn.close()
        print(f"Client {client_id} disconnected")

client_id = 0
while True:
    conn, addr = s.accept()
    print(f"Connected to: {addr}")
    clients.append({"client_id": client_id, "conn": conn})
    start_new_thread(threaded_client, (conn, client_id))
    client_id += 1