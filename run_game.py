import pygame  # Import pygame for game functionality
import config  # Import configuration settings like scene dimensions and FPS
from src.engine.game import *  # Import all game classes (Platform, Fighter, Enemy, etc.)

pygame.init()  # Initialize all imported pygame modules

# Set up the main game window using dimensions from config
scene = pygame.display.set_mode((config.scene_WIDTH, config.scene_HEIGHT)) 

# Load a background image located in the assets folder
background = pygame.image.load("src/assets/images/blue-preview.png")

# Set the window title using the caption defined in config
pygame.display.set_caption(config.CAPTION)

# Create a clock to manage the game's frame rate
clock = pygame.time.Clock()

# Create sprite groups to better organize and manage game objects.
all_sprites = pygame.sprite.Group()  # Contains all objects for global update and drawing
platforms = pygame.sprite.Group()      # Contains all platform objects
enemies = pygame.sprite.Group()        # Contains all enemy objects

# Create game objects with specified positions, sizes, and behaviors
static_platform = Platform(config.scene_WIDTH/4, config.scene_HEIGHT*3/5, config.scene_WIDTH/2, config.scene_HEIGHT/3)
# MovingPlatform moves horizontally within a given range and speed
moving_platform = MovingPlatform(config.scene_WIDTH/8, config.scene_HEIGHT/4, config.scene_WIDTH/4, 10, range_x=150, range_y=0, speed=1)
# Two fighter objects using custom control keys for movement and jumping
fighter1 = Fighter(150, 450, color=(0, 0, 255), controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w})
fighter2 = Fighter(350, 450, color=(255, 255, 0), controls={"left": pygame.K_LEFT, "Protocolright": pygame.K_RIGHT, "jump": pygame.K_UP})
# An enemy that patrols horizontally and bounces at screen edges
enemy = Enemy(50, 300, speed=2)

# Add each object to the appropriate sprite groups for updating and drawing
all_sprites.add(static_platform, moving_platform, fighter1, fighter2, enemy)
platforms.add(static_platform, moving_platform)
enemies.add(enemy)

# Main game loop that runs until the player exits the game
running = True
while running:
    # Process input events (such as closing the window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update all game objects (calls update() on each sprite in all_sprites)
    all_sprites.update()

    # Handle collisions for dynamic objects so that they can stand on platforms.
    # (Assumes that objects like Fighter and Enemy inherit from DynamicObject.)
    for sprite in all_sprites:
        # Check if the sprite is a dynamic object by confirming it has the collision handler.
        if isinstance(sprite, DynamicObject):
            sprite.handle_platform_collision(platforms)

    # Draw phase: clear the screen, draw background, and then all sprites
    scene.fill((0, 0, 0))  # Clear the screen by filling it with black
    # Draw the background image centered based on predetermined offsets
    scene.blit(background, (config.scene_WIDTH/2-408, config.scene_HEIGHT/2-240))
    all_sprites.draw(scene)  # Draw all sprites onto the scene

    pygame.display.flip()  # Refresh the display surface to show new drawings
    clock.tick(config.FPS)  # Maintain the FPS defined in config

pygame.quit()  # Clean up and close the pygame window
