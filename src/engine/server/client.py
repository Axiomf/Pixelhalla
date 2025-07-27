# client.py
import pygame
from network import Network
from player import Player

# Window dimensions
width = 500
height = 500

# Set up the Pygame window
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")


def redraw_window(win, player, other_players):
    """
    This function is responsible for all the drawing.
    """
    # Fill the window with white. This clears the screen from the last frame.
    win.fill((255, 255, 255))
    
    # Draw our own player
    player.draw(win)
    
    # Draw all the other players
    for other_player in other_players:
        other_player.draw(win)
    
    # Update the display to show the new frame
    pygame.display.update()


def main():
    """
    The main game loop for the client.
    """
    run = True
    n = Network() # Create a Network object to handle communication
    p = n.get_player() # Get the initial player object from the server
    clock = pygame.time.Clock()

    while run:
        clock.tick(60) # Limit the frame rate to 60 FPS

        # --- NETWORKING ---
        # 1. Send our player data to the server.
        # 2. Receive the list of other players in return.
        # We send our player `p` and get the list of ALL players back.
        all_players = n.send(p)
        
        # We need to filter out our own player object from the list
        # so we don't draw ourselves twice.
        other_players = [player for player in all_players if player.color != p.color]


        # Event handling loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        # Handle player movement
        p.move()

        # Drawing
        redraw_window(win, p, other_players)

# Run the main function when the script is executed
main()