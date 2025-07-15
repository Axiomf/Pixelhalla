from .platforms import *
from .dynamic_objects import *


# Set up the main game window using dimensions from config
scene = pygame.display.set_mode((config.SCENE_WIDTH, config.SCENE_HEIGHT)) 
GAME_STATE_LOADING = 1
GAME_STATE_PLAYING = 0

game_state = GAME_STATE_LOADING  # Start in loading screen

# Loading screen setup
font = pygame.font.Font(None, 74)  # Use default font, size 74 for button text
start_button = pygame.Rect(480, 250, 200, 80)  # Button position and size (x, y, width, height)
button_color = (0, 128, 255)  # Blue button
button_text = font.render("Start", True, (255, 255, 255))  # White text for button
button_text_rect = button_text.get_rect(center=start_button.center)  # Center text in button

# Draw loading screen

loading_background = pygame.image.load("src/assets/images/background/blue-preview.png")
loading_background = pygame.transform.scale(loading_background, (config.SCENE_WIDTH, config.SCENE_HEIGHT))
