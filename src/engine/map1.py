from .platforms import *
from .dynamic_objects import *
from .base import CustomGroup
from .animation_loader import *
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
                           config.SCENE_WIDTH*3/8,config.SCENE_HEIGHT*1/200, 
                           color=(139,69,19))
static_platform2 = Platform(config.SCENE_WIDTH*2/8 + 88, config.SCENE_HEIGHT*2/5 + 13, 
                           130,config.SCENE_HEIGHT*1/200, 
                           color=(139,69,19))
static_platform3 = Platform(680, config.SCENE_HEIGHT*2/5 + 13, 
                           130,config.SCENE_HEIGHT*1/200, 
                           color=(139,69,19))
path_list = {"idle" : "src/assets/images/inused_sheets/Goblin/Idle.png",
             "walk" : "src/assets/images/inused_sheets/Goblin/Run.png",
             "death" : "src/assets/images/inused_sheets/Goblin/Death.png",
             "hurt" : "src/assets/images/inused_sheets/Goblin/Take Hit.png",
             "attack" : "src/assets/images/inused_sheets/Goblin/Attack.png"}

# Two fighter objects using custom control keys for movement, jumping, and shooting.
fighter1 = Fighter(static_platform1.rect.x + 30, static_platform1.rect.y, 32, 32, platforms=platforms,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   animations=load_animations_Goblin(path_list, 150,150,crop_x= 60,crop_y= 65, crop_width=30, crop_height=35))
fighter2 = Fighter(static_platform1.rect.x + 30, static_platform1.rect.y, 32, 32,platforms=platforms,
                   controls={"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP},
                   animations=load_animations_Suicide_Bomber("src/assets/images/inused_sheets/death_bomb.png", 40, 32))

# An enemy that patrols horizontally and bounces at screen edges
enemy = Melee(static_platform1.rect.x + 60,  
            static_platform1.rect.y, 30, 35,
            speed=config.NPC_SPEED, 
            platforms=platforms, 
            projectiles=projectiles, 
            all_sprites=all_sprites,fighter=fighter1,
            animations=load_animations_Goblin(path_list, 150,150,crop_x= 60,crop_y= 65, crop_width=30, crop_height=35))

# Add each object to the appropriate sprite groups for updating and drawing
all_sprites.add(static_platform1, static_platform2,static_platform3, fighter1, fighter2, enemy)
platforms.add(static_platform1, static_platform2, static_platform3)
enemies.add(enemy)
fighters.add(fighter1, fighter2)

def draw_background():
    scene.fill((0, 0, 0))
    scene.blit(background, (0, 0))
    