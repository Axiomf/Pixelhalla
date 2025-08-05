import socket
import pickle
import threading
import time
import pygame  # added import

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

# Global game state variable to store server updates
game_state = None

def threaded_receive_messages(sock):
    global game_state
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("Disconnected from server.")
                break
            message = pickle.loads(data)
            # Update game state if message is a game update, else print it.
            if message.get("request_type") == "game_update":
                game_state = message
            else:
                print("Server message:", message)
        except Exception as e:
            print("Error receiving message:", e)
            break

def main():
    pygame.init()  # initialize pygame
    screen = pygame.display.set_mode((1200,600))
    pygame.display.set_caption("Pixelhala Client")
    clock = pygame.time.Clock()

    server_ip = "127.0.0.1"
    server_port = 5555  # ensure this matches your server configuration
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        conn.connect((server_ip, server_port))
    except Exception as e:
        print("Could not connect to the server:", e)
        return

    try:
        client_id_data = conn.recv(4096)
        client_id = pickle.loads(client_id_data)
        print("Connected to server. Your client ID is:", client_id)
    except Exception as e:
        print("Error receiving client ID:", e)
        conn.close()
        return

    # Start thread to listen for server messages
    recv_thread = threading.Thread(target=threaded_receive_messages, args=(conn,))
    recv_thread.daemon = True
    recv_thread.start()

    running = True
    while running:
        inputs = []  # list to capture keyboard events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                inputs.append(pygame.key.name(event.key))
                
        # Send captured inputs to server if any
        if inputs:
            client_package = {
                "client_id": client_id,
                "request_type": "input",
                "game_mode": "1vs1",   # default value
                "inputs": inputs,
                "shoots": []
            }
            try:
                conn.sendall(pickle.dumps(client_package))
            except Exception as e:
                print("Error sending data:", e)
                running = False

        # Simple display: clear screen and show counts from server game update.
        screen.fill((0, 0, 0))
        if game_state:
            font = pygame.font.SysFont("Arial", 20)
            text_lines = [
                f"Platforms: {len(game_state.get('platforms', []))}",
                f"Fighters: {len(game_state.get('fighters', []))}",
                f"Projectiles: {len(game_state.get('projectiles', []))}",
                f"Power-ups: {len(game_state.get('power_ups', []))}"
            ]
            for i, line in enumerate(text_lines):
                text_surface = font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (20, 20 + i * 25))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    conn.close()

if __name__ == '__main__':
    main()
