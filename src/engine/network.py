# network.py
import socket
import pickle

class Network:
    """
    This class manages the client's connection to the server.
    """
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # The server's IP address. For local testing, this is "127.0.0.1".
        # If the server is on another computer on your network, find its local IP.
        # If the server is on the internet, you'll need its public IP and port forwarding.
        self.server = "127.0.0.1" 
        self.port = 5555 # The port must match the server's port.
        self.addr = (self.server, self.port)
        # When we connect, the server sends back this client's starting Player object.
        self.p = self.connect()

    def get_player(self):
        """
        Returns the initial player object received from the server.
        """
        return self.p

    def connect(self):
        """
        Connects to the server and returns the initial data sent by the server.
        """
        try:
            self.client.connect(self.addr)
            # When we connect, we expect the server to send us our player object.
            # We use pickle to "un-serialize" the object from bytes back into a Player object.
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)
            return None

    def send(self, data):
        """
        Sends data to the server and receives a response.
        'data' is the client's own player object.
        The response will be the list of all other players.
        """
        try:
            # We send our player object, serialized into bytes using pickle.
            self.client.send(pickle.dumps(data))
            # We receive the list of other players from the server.
            # The buffer size 2048 might need to be increased if we send more data.
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)
            return None