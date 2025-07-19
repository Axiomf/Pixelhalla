# map jesus
from .platforms import *
from .dynamic_objects import *
from .base import CustomGroup
from .animation_loader import *

scene = pygame.display.set_mode((config.SCENE_WIDTH, config.SCENE_HEIGHT))  # Set up the main game window
# Load a background image located in the assets folder
#background = pygame.image.load("src/assets/images/background/country-platform-preview.png")
#background = pygame.transform.scale(background, (config.SCENE_WIDTH, config.SCENE_HEIGHT))

background2 = pygame.image.load("src/assets/images/background/jesus/j1.jpg")
background2 = pygame.transform.scale(background2, (config.SCENE_WIDTH/4, config.SCENE_HEIGHT))

background3 = pygame.image.load("src/assets/images/background/jesus/j2.jpg")
background3 = pygame.transform.scale(background3, (config.SCENE_WIDTH/4, config.SCENE_HEIGHT))

background4 = pygame.image.load("src/assets/images/background/jesus/j3.jpg")
background4 = pygame.transform.scale(background4, (config.SCENE_WIDTH/4, config.SCENE_HEIGHT))

background5 = pygame.image.load("src/assets/images/background/jesus/j4.jpg")
background5 = pygame.transform.scale(background5, (config.SCENE_WIDTH/4, config.SCENE_HEIGHT))
# config based approach:


# Create sprite groups to better organize and manage game objects.
all_sprites = CustomGroup()      # Contains all objects for global update and drawing
platforms = pygame.sprite.Group()          # Contains all platform objects
enemies = pygame.sprite.Group()            # Contains all enemy objects
projectiles = pygame.sprite.Group()        # Contains all projectile objects
fighters = pygame.sprite.Group()        # Contains all fighter objects

#static_platform = Platform(config.SCENE_WIDTH/4, config.SCENE_HEIGHT*3/5, 500, 100, color=(139, 69, 19))
#static_platform2 = Platform(config.SCENE_WIDTH/4 + 450, config.SCENE_HEIGHT*3/5 - 50, 50, 50, color=(139, 78, 45))

static_platform3 = Platform(0, config.SCENE_HEIGHT - 20, 
                           1200, 20, 
                           color=(139, 140, 78))

# MovingPlatform moves horizontally within a given range and speed
moving_platform = MovingPlatform(config.SCENE_WIDTH/8, config.SCENE_HEIGHT/4,
                                 config.SCENE_WIDTH/4, 10, range_x=150, range_y=0, speed=1)

# Two fighter objects using custom control keys, now passing animations during construction.
fighter1 = Fighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   animations=load_animations_Arcane_Archer("src/assets/images/inused_sheets/Arcane_Archer.png", 64, 64,scale=1))
#fighter2 = Fighter(650, 450, 32, 32,platforms=platforms,controls={"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP}, animations=load_animations_Suicide_Bomber("src/assets/images/inused_sheets/death_bomb.png", 40, 32))

# Existing enemy instance
enemy = NPC(config.SCENE_WIDTH/4 + (500 / 2) - (30 / 2),  config.SCENE_HEIGHT*3/5 - 30, 32, 32,
            speed=config.NPC_SPEED, platforms=platforms, projectiles=projectiles, all_sprites=all_sprites, fighter=fighter1,
            animations=load_animations_Arcane_Archer("src/assets/images/inused_sheets/Arcane_Archer.png", 64, 64))
            
# New enemy variants using added classes
melee_enemy = Melee(config.SCENE_WIDTH/4 + 100, config.SCENE_HEIGHT*3/5 - 32, 32, 32,
                    speed=config.NPC_SPEED, platforms=platforms, projectiles=projectiles,
                    all_sprites=all_sprites, fighter=fighter1,
                    animations=load_animations_Arcane_Archer("src/assets/images/inused_sheets/Arcane_Archer.png", 64, 64))
ranged_enemy = Ranged(config.SCENE_WIDTH/4 + 200, config.SCENE_HEIGHT*3/5 - 32, 32, 32,
                      speed=config.NPC_SPEED, platforms=platforms, projectiles=projectiles,
                      all_sprites=all_sprites, fighter=fighter1,
                      animations=load_animations_NightBorne("src/assets/images/inused_sheets/NightBorne.png", 80, 80))

powerup = PowerUp(500, config.SCENE_HEIGHT - 30,"double_jump",5, width=10, height=10, color=(255,255,0),image_path=None)
powerup2 = PowerUp(100, config.SCENE_HEIGHT - 30,"damage",20, width=10, height=10, color=(150,0,0),image_path=None)
powerup3 = PowerUp(300, config.SCENE_HEIGHT - 30,"shield",20, width=10, height=10, color=(150,0,0),image_path=None)



# Add each object to the appropriate sprite groups for updating and drawing
all_sprites.add(moving_platform, fighter1, enemy, static_platform3,powerup,powerup2, melee_enemy, ranged_enemy)
platforms.add(moving_platform, static_platform3)
enemies.add(enemy, melee_enemy, ranged_enemy)
fighters.add(fighter1)

def draw_background():
    scene.fill((0, 0, 0))
    #scene.blit(background, (0, 0))
    
    scene.blit(background2, (config.SCENE_WIDTH/2, 0))
    scene.blit(background3, (config.SCENE_WIDTH/4, 0))
    scene.blit(background4, (config.SCENE_WIDTH*3/4, 0))
    scene.blit(background5, (0, 0))