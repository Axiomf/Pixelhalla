import pygame  # Import pygame for game functionality
import config  # Import configuration settings like scene dimensions and FPS
import math    # Import math for sin function in pulse effect
from src.engine.state_manager import StateManager

# Initialize pygame
pygame.init()  # Initialize all imported pygame modules
pygame.font.init()  # Explicitly initialize font module
pygame.display.set_caption(config.CAPTION)  # Set the window title
scene = pygame.display.set_mode((config.SCENE_WIDTH, config.SCENE_HEIGHT))  # Set up the main game window
clock = pygame.time.Clock()  # Create a clock to manage the game's frame rate

# Initialize state manager
state_manager = StateManager(scene)

running = True
while running:
    current_time = pygame.time.get_ticks()  # Get current time for debounce
    config.PULSE_TIME += config.PULSE_SPEED  # Update pulse animation
    scale = config.PULSE_SCALE * abs(math.sin(config.PULSE_TIME))  # Calculate scale for pulse

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        state_manager.handle_event(event, current_time, scale)

    # Update and draw the current state
    state_manager.update(current_time, scale)
    state_manager.draw(scale)
    pygame.display.flip()  # Refresh the display
    clock.tick(config.FPS)  # Maintain the FPS defined in config

pygame.quit()  # Clean up and close the pygame window