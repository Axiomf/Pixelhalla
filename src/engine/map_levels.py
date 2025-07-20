from .platforms import *
from .dynamic_objects import *
from .base import CustomGroup
from .animation_loader import *

scene = pygame.display.set_mode((config.SCENE_WIDTH, config.SCENE_HEIGHT))  # Set up the main game window
# Load a background image located in the assets folder
background = pygame.image.load("src/assets/images/nature_3/origbig.png")
background = pygame.transform.scale(background, (config.SCENE_WIDTH, config.SCENE_HEIGHT))




# Create sprite groups to better organize and manage game objects.
all_sprites = CustomGroup()      # Contains all objects for global update and drawing
platforms = pygame.sprite.Group()          # Contains all platform objects
enemies = pygame.sprite.Group()            # Contains all enemy objects
projectiles = pygame.sprite.Group()        # Contains all projectile objects
fighters = pygame.sprite.Group()        # Contains all fighter objects

static_mid_platform_3 = Platform(250, 150, 
                           700, 5, 
                           color=(77, 115, 81))
static_mid_platform_2 = Platform(250, 300, 
                           700, 5, 
                           color=(77, 115, 81))
static_mid_platform_1 = Platform(250, 450, 
                           700, 5, 
                           color=(77, 115, 81))

static_left_platform = Platform(50, 375, 
                           100, 10, 
                           color=(77, 115, 81))
static_right_platform = Platform(1050, 225, 
                           100, 10, 
                           color=(77, 115, 81))



# Two fighter objects using custom control keys for movement, jumping, and shooting.
fighter1 = Fighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   animations=load_animations_Arcane_Archer(64, 64,scale=1))


death_bomb = Suicide_Bomb(500, config.SCENE_HEIGHT*3/5 - 300
                          , speed=1, health=50, 
                 damage=20, platforms=platforms, projectiles=projectiles, 
                 all_sprites=all_sprites, fighter=fighter1, animations=load_animations_Suicide_Bomber(), roam=True)

# Add each object to the appropriate sprite groups for updating and drawing
all_sprites.add(static_mid_platform_1,static_mid_platform_2,static_mid_platform_3, static_left_platform, static_right_platform,  fighter1, death_bomb)
platforms.add(static_mid_platform_1,static_mid_platform_2,static_mid_platform_3, static_left_platform,static_right_platform)
enemies.add(death_bomb)
fighters.add(fighter1)

def draw_background():
    scene.fill((0, 0, 0))
    scene.blit(background, (0, 0))