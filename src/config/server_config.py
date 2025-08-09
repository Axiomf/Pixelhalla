import socket

SERVER = "127.0.0.1"  # Server IP
PORT = 5555           # Server port

def create_server_socket():# the comments on how it works are in previous commits when there was no server_config.py
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)

    try:
        s.bind((SERVER, PORT))
    except socket.error as e:
        print(f"Server could not bind to {SERVER}:{PORT}, error: {e}")
        exit()
    s.listen(2)
    print("Waiting for a connection, Server Started")
    return s

