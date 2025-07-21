from .platforms import *
from .dynamic_objects import *
from .base import CustomGroup
from .animation_loader import *
scene = pygame.display.set_mode((config.SCENE_WIDTH, config.SCENE_HEIGHT))  # Set up the main game window
# Load a background image located in the assets folder
background = pygame.image.load("src/assets/images/nature_1/orig.png")
background = pygame.transform.scale(background, (config.SCENE_WIDTH, config.SCENE_HEIGHT))



# Create sprite groups to better organize and manage game objects.
all_sprites = CustomGroup()      # Contains all objects for global update and drawing
platforms = pygame.sprite.Group()          # Contains all platform objects
enemies = pygame.sprite.Group()            # Contains all enemy objects
projectiles = pygame.sprite.Group()        # Contains all projectile objects
fighters = pygame.sprite.Group()        # Contains all fighter objects

static_platform = Platform(0, 300, 
                           1200, 100, 
                           color=(139, 69, 19))

enemy = Boss(static_platform.rect.x + 60,  
            static_platform.rect.y, 
            platforms=platforms, 
            projectiles=projectiles, 
            all_sprites=all_sprites,
            animations=load_animations_Boss(1280, 1280))
# Add each object to the appropriate sprite groups for updating and drawing
all_sprites.add(static_platform)
platforms.add(static_platform)
enemies.add(enemy)
# fighters.add(fighter1, fighter2)

def draw_background():
    scene.fill((0, 0, 0))
    scene.blit(background, (0, 0))