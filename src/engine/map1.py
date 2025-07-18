from .platforms import *
from .dynamic_objects import *
from .base import CustomGroup
scene = pygame.display.set_mode((config.SCENE_WIDTH, config.SCENE_HEIGHT))  # Set up the main game window
# Load a background image located in the assets folder
background = pygame.image.load("src/assets/images/background/map-ShorwindFishingPort.png")
background = pygame.transform.scale(background, (config.SCENE_WIDTH, config.SCENE_HEIGHT))

# Create sprite groups to better organize and manage game objects.
all_sprites = CustomGroup()      # Contains all objects for global update and drawing
platforms = pygame.sprite.Group()          # Contains all platform objects
enemies = pygame.sprite.Group()            # Contains all enemy objects
projectiles = pygame.sprite.Group()        # Contains all projectile objects
fighters = pygame.sprite.Group()        # Contains all fighter objects


static_platform1 = Platform(config.SCENE_WIDTH*2/8 + 73, config.SCENE_HEIGHT*3/5 - 15, 
                           config.SCENE_WIDTH*3/8,config.SCENE_HEIGHT*1/100, 
                           color=(139,69,19))
static_platform2 = Platform(config.SCENE_WIDTH*2/8, config.SCENE_HEIGHT*1/5 - 15, 
                           100,config.SCENE_HEIGHT*1/100, 
                           color=(139,69,19))


# Two fighter objects using custom control keys for movement, jumping, and shooting.
fighter1 = Fighter(450,  
                   static_platform1.rect.y, 
                   color=(0, 0, 255), 
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   image_path="src/assets/images/fighter.png",
                   platforms=platforms)
fighter2 = Fighter(650, static_platform1.rect.y, 
                   color=(255, 255, 0), 
                   controls={"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP},
                   platforms=platforms)
# An enemy that patrols horizontally and bounces at screen edges
enemy = NPC(static_platform1.rect.x + 30,  
            static_platform1.rect.y, 30, 35,
            speed=config.NPC_SPEED, 
            platforms=platforms, 
            projectiles=projectiles, 
            all_sprites=all_sprites)
enemy.add_animation("idle", "src/assets/images/enemies/Goblin/Run.png",150,150,crop_x= 60,crop_y= 65, crop_width=30, crop_height=35)
enemy.add_animation("death", "src/assets/images/enemies/Goblin/Death.png",150,150,crop_x= 60,crop_y= 65, crop_width=30, crop_height=35)
# Add each object to the appropriate sprite groups for updating and drawing
all_sprites.add(static_platform1, static_platform2, fighter1, fighter2, enemy)
platforms.add(static_platform1, static_platform2)
enemies.add(enemy)
fighters.add(fighter1, fighter2)

def draw_background():
    scene.fill((0, 0, 0))
    scene.blit(background, (0, 0))
    