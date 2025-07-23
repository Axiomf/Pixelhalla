from .platforms import *
from .dynamic_objects import *
from .base import CustomGroup
from .animation_loader import *
from src.engine.gpt_api.dummyUI import*

scene = pygame.display.set_mode((config.SCENE_WIDTH, config.SCENE_HEIGHT))  # Set up the main game window
# Load a background image located in the assets folder
background = pygame.image.load("src/assets/images/background/hell_throne.png")
background = pygame.transform.scale(background, (config.SCENE_WIDTH, config.SCENE_HEIGHT))

# Create sprite groups to better organize and manage game objects.
all_sprites = CustomGroup()      # Contains all objects for global update and drawing
platforms = pygame.sprite.Group()          # Contains all platform objects
enemies = pygame.sprite.Group()            # Contains all enemy objects
projectiles = pygame.sprite.Group()        # Contains all projectile objects
fighters = pygame.sprite.Group()        # Contains all fighter objects
melee = pygame.sprite.Group()
enemies_without_boss = pygame.sprite.Group()

def load_map():

    static_platform1 = Platform(0, 550, 
                            1200,config.SCENE_HEIGHT*1/200, 
                            color=None)#this is the main platform
    # Two fighter objects using custom control keys for movement, jumping, and shooting.
    fighter1 = MeleeFighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, health=1000, platforms=platforms, 
            enemies=enemies, fighters=fighters,
                controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "attack": pygame.K_SPACE},
                animations=load_animations_Goblin(150,150,crop_x= 60,crop_y= 65, crop_width=30, crop_height=35))


    # An enemy that patrols horizontally and bounces at screen edges
    enemy = Boss(static_platform1.rect.x + 1100,  
                static_platform1.rect.y, 85, 85,
                platforms=platforms, 
                projectiles=projectiles, 
                all_sprites=all_sprites,fighter=fighter1, enemies=enemies,
                animations=load_animations_Boss(1280, 1280, scale=0.1))

    # Add each object to the appropriate sprite groups for updating and drawing
    all_sprites.add(static_platform1, fighter1, enemy)
    platforms.add(static_platform1)
    enemies.add(enemy)
    melee.add(enemy)
    fighters.add(fighter1)

def draw_background():
    scene.fill((0, 0, 0))
    scene.blit(background, (0, 0))
    display_texts(background)
    