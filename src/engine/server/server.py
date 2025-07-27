# server.py
import socket
from _thread import * # For threading, to handle multiple clients at once
from player import Player # Import our Player class
import pickle # To serialize Python objects to send over the network

# Server configuration
server = "127.0.0.1"  # The IP address the server will run on (localhost)
port = 5555          # The port the server will listen on

# Create a socket object
# AF_INET specifies we are using IPv4
# SOCK_STREAM specifies we are using TCP (a reliable connection-based protocol)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the IP and port
try:
    s.bind((server, port))
except socket.error as e:
    str(e)

# Start listening for incoming connections. The number (2) is the max number of queued connections.
s.listen(2)
print("Waiting for a connection, Server Started")

# This is our master list of players. The server holds the "true" state of all players.
# We create two starting player objects. The first client will get players[0], the second will get players[1].
players = [Player(0,0,50,50,(255,0,0)), Player(100,100,50,50,(0,0,255))]

def threaded_client(conn, player_id):
    """
    This function runs in a separate thread for each connected client.
    """
    # When a client first connects, send them their own player object.
    conn.send(pickle.dumps(players[player_id]))

    reply = ""
    while True:
        try:
            # Receive data from the client (their updated player object).
            # The 2048 is the buffer size (how much data we receive at once).
            data = pickle.loads(conn.recv(2048))
            
            # Update the server's master copy of this player's state.
            players[player_id] = data

            if not data:
                print("Disconnected")
                break
            else:
                # The reply to the client will be the list of all players.
                reply = players

                # print("Received: ", data)
                # print("Sending : ", reply)

            # Send the complete list of players back to the client.
            # pickle.dumps serializes the list into a byte stream.
            conn.sendall(pickle.dumps(reply))
        except:
            # If there's an error (e.g., client disconnects), break the loop.
            break

    print("Lost connection")
    conn.close()

# Main server loop to accept new connections
current_player = 0
while True:
    # The accept() method blocks until a client connects.
    # It returns a new connection object (conn) and the client's address (addr).
    conn, addr = s.accept()
    print("Connected to:", addr)

    # When a client connects, we start a new thread for them.
    # This allows the server to handle multiple clients simultaneously without blocking.
    start_new_thread(threaded_client, (conn, current_player))
    current_player += 1 # Increment for the next player


