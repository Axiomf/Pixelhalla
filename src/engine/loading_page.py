import pygame
import config


# Define game states
GAME_STATE_LOADING = 1
GAME_STATE_PLAYING = 0
game_state = GAME_STATE_LOADING  # Start in loading screen

# Loading screen setup
font = pygame.font.Font(None, 74)  # Use default font, size 74 for button text
start_button = pygame.Rect(450, 250, 300, 100)  # Start button for visual display
button_color = (0, 128, 255)  # Blue button for Start
start_button_text = font.render("Start", True, (255, 255, 255))  # White text for Start
start_button_text_rect = start_button_text.get_rect(center=start_button.center)  # Center Start text
loading_background = pygame.image.load("src/assets/images/blue-preview.png")  # Load background image
loading_background = pygame.transform.scale(loading_background, (config.SCENE_WIDTH, config.SCENE_HEIGHT))  # Scale to scene size

# Variable to debounce mouse clicks
last_click_time = 0
CLICK_COOLDOWN = 200  # 200ms cooldown between clicks