from .platforms import *
from .dynamic_objects import *
from .base import CustomGroup

# Set up the main game window using dimensions from config
scene = pygame.display.set_mode((config.SCENE_WIDTH, config.SCENE_HEIGHT)) 
# Load a background image located in the assets folder
background = pygame.image.load("src/assets/images/background/country-platform-preview.png")
background = pygame.transform.scale(background, (config.SCENE_WIDTH, config.SCENE_HEIGHT))

# Create sprite groups to better organize and manage game objects.
all_sprites = CustomGroup()      # Contains all objects for global update and drawing
platforms = pygame.sprite.Group()          # Contains all platform objects
enemies = pygame.sprite.Group()            # Contains all enemy objects
projectiles = pygame.sprite.Group()        # Contains all projectile objects
fighters = pygame.sprite.Group()        # Contains all fighter objects


static_platform = Platform(config.SCENE_WIDTH/8, config.SCENE_HEIGHT*4/5, 
                           config.SCENE_WIDTH*6/8,config.SCENE_HEIGHT*1/5, 
                           color=(139,69,19))



# Two fighter objects using custom control keys for movement, jumping, and shooting.
fighter1 = Fighter(450,  
            static_platform.rect.y - 70, color=(0, 0, 255), 
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   image_path="src/assets/images/fighter.png")
print(fighter1.rect.top)
print(fighter1.rect.bottom)
fighter2 = Fighter(650, 450, color=(255, 255, 0), 
                   controls={"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP})
# An enemy that patrols horizontally and bounces at screen edges
enemy = NPC(static_platform.rect.x + (static_platform.rect.width / 2) - (30 / 2),  
            static_platform.rect.y - 30, 
            speed=config.NPC_SPEED, image_path="src/assets/images/death-lamp-walk6.png")


# Add each object to the appropriate sprite groups for updating and drawing
all_sprites.add(static_platform, fighter1, fighter2, enemy)
platforms.add(static_platform)
enemies.add(enemy)
fighters.add(fighter1, fighter2)

def draw_background():
    scene.fill((0, 0, 0))
    scene.blit(background, (0, 0))
    