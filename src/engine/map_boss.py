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

def load_map(fighter1_id):

    static_platform1 = Platform(0, 550, 
                            1200,config.SCENE_HEIGHT*1/200, 
                            color=None)#this is the main platform
    # Two fighter objects using custom control keys for movement, jumping, and shooting.
    if fighter1_id == "fighter1":
            fighter1 = Fighter(150, 150, 32, 32, platforms=platforms,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   animations=load_animations_Elf_Archer())
    elif fighter1_id == "fighter2":
        fighter1 = MeleeFighter(150, 150, 32, 32, platforms=platforms, enemies=enemies, fighters=fighters,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "attack": pygame.K_SPACE},
                   animations=load_animations_Samurai(scale=1))
    elif fighter1_id == "fighter3":
        fighter1 = MeleeFighter(150, 150, 32, 32, platforms=platforms, enemies=enemies, fighters=fighters,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "attack": pygame.K_SPACE},
                   animations=load_animations_Knight(scale=1))
    elif fighter1_id == "fighter4":
        fighter1 = Fighter(150, 150, 32, 32, platforms=platforms,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   animations=load_animations_Arcane_Archer(scale=1))


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
    