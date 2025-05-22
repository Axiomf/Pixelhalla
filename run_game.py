# my h & g keys are broken so I put them here
import pygame  # Import pygame for game functionality
import config  # Import configuration settings like scene dimensions and FPS

# Import platform and dynamic object classes from the new files
from src.engine.platforms import Platform, MovingPlatform
from src.engine.dynamic_objects import Fighter, NPC, DynamicObject

pygame.init()  # Initialize all imported pygame modules

# Set up the main game window using dimensions from config
scene = pygame.display.set_mode((config.SCENE_WIDTH, config.SCENE_HEIGHT)) 

# Load a background image located in the assets folder
background = pygame.image.load("src/assets/images/blue-preview.png")

# Set the window title using the caption defined in config
pygame.display.set_caption(config.CAPTION)

# Create a clock to manage the game's frame rate
clock = pygame.time.Clock()

# Create sprite groups to better organize and manage game objects.
all_sprites = pygame.sprite.Group()      # Contains all objects for global update and drawing
platforms = pygame.sprite.Group()          # Contains all platform objects
enemies = pygame.sprite.Group()            # Contains all enemy objects
projectiles = pygame.sprite.Group()        # Contains all projectile objects

# Create game objects with specified positions, sizes, and behaviors
static_platform = Platform(config.SCENE_WIDTH/4, config.SCENE_HEIGHT*3/5, 
                           384,224, 
                           image_path="src/assets/images/country-platform-preview.png")
# MovingPlatform moves horizontally within a given range and speed
moving_platform = MovingPlatform(config.SCENE_WIDTH/8, config.SCENE_HEIGHT/4,
                                 config.SCENE_WIDTH/4, 10, range_x=150, range_y=0, speed=1)
# Two fighter objects using custom control keys for movement, jumping, and shooting.
fighter1 = Fighter(350, 450,width=32, color=(0, 0, 255), 
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   image_path="src/assets/images/death-lamp-walk6.png")
fighter2 = Fighter(650, 450, color=(255, 255, 0), 
                   controls={"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP})
# An enemy that patrols horizontally and bounces at screen edges
enemy = NPC(400, 450, speed=1)

# Add each object to the appropriate sprite groups for updating and drawing
all_sprites.add(static_platform, moving_platform, fighter1, fighter2, enemy)
platforms.add(static_platform, moving_platform)
enemies.add(enemy)

running = True
while running:
    # Process input events (such as closing the window or shooting projectiles)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # If the shoot key for fighter1 is pressed, spawn a projectile.
            if event.key == fighter1.controls.get("shoot"):
                projectile = fighter1.shoot()
                all_sprites.add(projectile)
                projectiles.add(projectile)

    # Update all game objects (calls update() on each sprite in all_sprites)
    all_sprites.update()

    # Handle collisions so dynamic objects can stand on platforms.
    for sprite in all_sprites:
        if isinstance(sprite, DynamicObject):
            sprite.handle_platform_collision(platforms)

    # Draw phase: clear the screen, draw background, and then all sprites
    scene.fill((0, 0, 0))
    scene.blit(background, (config.SCENE_WIDTH/2 - 408, config.SCENE_HEIGHT/2 - 240))
    all_sprites.draw(scene)

    pygame.display.flip()  # Refresh the display
    clock.tick(config.FPS)  # Maintain the FPS defined in config

pygame.quit()  # Clean up and close the pygame window
