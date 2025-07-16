from .platforms import *
from .dynamic_objects import *
from .base import CustomGroup
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



# MovingPlatform moves horizontally within a given range and speed
moving_platform = MovingPlatform(config.SCENE_WIDTH/8, config.SCENE_HEIGHT/4,
                                 config.SCENE_WIDTH/4, 10, range_x=150, range_y=0, speed=1)
# Two fighter objects using custom control keys for movement, jumping, and shooting.
fighter1 = Fighter(450,  
                   config.SCENE_HEIGHT*3/5 - 70, 32, 32,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   platforms=platforms)
fighter1.add_animation("idle", "src/assets/images/Bloody_Eye.png", 32, 32)
fighter2 = Fighter(650, 450, 32, 32,
                   controls={"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP},
                   platforms=platforms)
fighter2.add_animation("idle", "src/assets/images/Bloody_Eye.png", 32, 32)
# An enemy that patrols horizontally and bounces at screen edges
enemy = NPC(config.SCENE_WIDTH/4 + (500 / 2) - (30 / 2),  
            config.SCENE_HEIGHT*3/5 - 30, 32, 32,
            speed=config.NPC_SPEED,
            platforms=platforms, 
            projectiles=projectiles, 
            all_sprites=all_sprites)
enemy.add_animation("idle", "src/assets/images/Bloody_Eye.png", 32, 32)

# Add each object to the appropriate sprite groups for updating and drawing
all_sprites.add(static_mid_platform_1,static_mid_platform_2,static_mid_platform_3, static_left_platform, static_right_platform, moving_platform, fighter1, fighter2, enemy)
platforms.add(static_mid_platform_1,static_mid_platform_2,static_mid_platform_3, static_left_platform,static_right_platform, moving_platform)
enemies.add(enemy)
fighters.add(fighter1, fighter2)

def draw_background():
    scene.fill((0, 0, 0))
    scene.blit(background, (0, 0))