from .platforms import *
from .dynamic_objects import *
from .base import CustomGroup
from .animation_loader import *




scene = pygame.display.set_mode((config.SCENE_WIDTH, config.SCENE_HEIGHT))  # Set up the main game window
# Load a background image located in the assets folder
background2 = pygame.image.load("src/assets/images/background/jesus/j1.jpg")
background2 = pygame.transform.scale(background2, (config.SCENE_WIDTH/4, config.SCENE_HEIGHT))

background3 = pygame.image.load("src/assets/images/background/jesus/j2.jpg")
background3 = pygame.transform.scale(background3, (config.SCENE_WIDTH/4, config.SCENE_HEIGHT))

background4 = pygame.image.load("src/assets/images/background/jesus/j3.jpg")
background4 = pygame.transform.scale(background4, (config.SCENE_WIDTH/4, config.SCENE_HEIGHT))

background5 = pygame.image.load("src/assets/images/background/jesus/j4.jpg")
background5 = pygame.transform.scale(background5, (config.SCENE_WIDTH/4, config.SCENE_HEIGHT))
# Create sprite groups to better organize and manage game objects.
all_sprites = CustomGroup()      # Contains all objects for global update and drawing
platforms = pygame.sprite.Group()          # Contains all platform objects
enemies = pygame.sprite.Group()            # Contains all enemy objects
projectiles = pygame.sprite.Group()        # Contains all projectile objects
fighters = pygame.sprite.Group()        # Contains all fighter objects
melee = pygame.sprite.Group()

def load_map():

    static_platform1 = Platform(0, 550, 
                            1200,config.SCENE_HEIGHT*1/200, 
                            color=None)#this is the main platform
    path_list = {"idle" : "src/assets/images/inused_sheets/Goblin/Idle.png",
                "walk" : "src/assets/images/inused_sheets/Goblin/Run.png",
                "death" : "src/assets/images/inused_sheets/Goblin/Death.png",
                "hurt" : "src/assets/images/inused_sheets/Goblin/Take Hit.png",
                "attack" : "src/assets/images/inused_sheets/Goblin/Attack.png"}

    # Two fighter objects using custom control keys for movement, jumping, and shooting.
    fighter1 = MeleeFighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms, 
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
    scene.blit(background2, (config.SCENE_WIDTH/2, 0))
    scene.blit(background3, (config.SCENE_WIDTH/4, 0))
    scene.blit(background4, (config.SCENE_WIDTH*3/4, 0))
    scene.blit(background5, (0, 0))
    