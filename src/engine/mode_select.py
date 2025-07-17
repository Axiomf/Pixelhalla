import pygame

GAME_STATE_MODE_SELECT = 2
game_mode = None  # Track game mode: "single" or "multiplayer"

# Mode select screen setup
font = pygame.font.Font(None, 65)  # Use default font, size 74 for button text
single_button = pygame.Rect(450, 250, 300, 100)  # Single Player button
two_button = pygame.Rect(450, 430, 300, 100)  # Two Players button
single_button_text = font.render("Single Player", True, (255, 255, 255))  # White text
two_button_text = font.render("Multiplayer", True, (255, 255, 255))  # White text
single_button_text_rect = single_button_text.get_rect(center=single_button.center)  # Center text
two_button_text_rect = two_button_text.get_rect(center=two_button.center)  # Center text