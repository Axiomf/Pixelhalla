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
power_ups = pygame.sprite.Group()

#static_platform = Platform(config.SCENE_WIDTH/4, config.SCENE_HEIGHT*3/5, 500, 100, color=(139, 69, 19))
#static_platform2 = Platform(config.SCENE_WIDTH/4 + 450, config.SCENE_HEIGHT*3/5 - 50, 50, 50, color=(139, 78, 45))

def load_map(level_state, fighter1_id, fighter2_id, fighter_select_phase):
    
    static_platform3 = Platform(0, config.SCENE_HEIGHT - 20, 
                            1200, 20, 
                            color=(139, 140, 78))
    
    static_platform2 = Platform(693, config.SCENE_HEIGHT*2/5 - 6, 
                            153,config.SCENE_HEIGHT*1/200, 
                            color=(0,0,0))

    moving_platform = MovingPlatform(config.SCENE_WIDTH/8, config.SCENE_HEIGHT/4,
                                    config.SCENE_WIDTH/4, 10, range_x=150, range_y=0, speed=1)
    powerup = PowerUp(500, config.SCENE_HEIGHT - 30,"double_jump",5, width=30, height=30, color=(255,255,0), image_path="src/assets/images/inused_single_images/double_jump.png", all_sprites=all_sprites, power_ups=power_ups, platforms=platforms)
    powerup2 = PowerUp(100, config.SCENE_HEIGHT - 30,"damage",20, width=30, height=30, color=(150,0,0), image_path="src/assets/images/inused_single_images/damage.png", all_sprites=all_sprites, power_ups=power_ups, platforms=platforms)
    powerup3 = PowerUp(300, config.SCENE_HEIGHT - 30,"shield",20, width=30, height=30, color=(150,0,0), image_path="src/assets/images/inused_single_images/shield.png", all_sprites=all_sprites, power_ups=power_ups, platforms=platforms)
    powerup4 = PowerUp(900, config.SCENE_HEIGHT - 30,"supershot",4, width=30, height=30, color=(75,75,75), image_path="src/assets/images/inused_single_images/supershot.png",all_sprites=all_sprites, power_ups=power_ups, platforms=platforms)

    if fighter1_id == "fighter1":
            fighter1 = Fighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   animations=load_animations_Elf_Archer())
    elif fighter1_id == "fighter2":
        fighter1 = MeleeFighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms, enemies=enemies, fighters=fighters,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "attack": pygame.K_SPACE},
                   animations=load_animations_Samurai(scale=1))
    elif fighter1_id == "fighter3":
        fighter1 = MeleeFighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms, enemies=enemies, fighters=fighters,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "attack": pygame.K_SPACE},
                   animations=load_animations_Knight(scale=1))
    elif fighter1_id == "fighter4":
        fighter1 = Fighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   animations=load_animations_Arcane_Archer(scale=1))
        
    ##############
    if fighter_select_phase == 2:
        if fighter2_id == "fighter1":
           fighter2 = Fighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   animations=load_animations_Elf_Archer())
        elif fighter2_id == "fighter2":
            fighter2 = MeleeFighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms,  enemies=enemies, fighters=fighters,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "attack": pygame.K_SPACE},
                   animations=load_animations_Samurai(scale=1))
        elif fighter2_id == "fighter3":
            fighter2 = MeleeFighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms,  enemies=enemies, fighters=fighters,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "attack": pygame.K_SPACE},
                   animations=load_animations_Knight(scale=1))
        elif fighter2_id == "fighter4":
            fighter2 = Fighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   animations=load_animations_Arcane_Archer(scale=1))
        all_sprites.add(static_platform3,moving_platform, fighter1, fighter2)
        platforms.add(static_platform3, moving_platform)
        fighters.add(fighter1, fighter2)
    else:    
        x = 30
        y = 35
        if(level_state == 0):
            enemy_animation = load_animations_Suicide_Bomber()
            enemy_type = Suicide_Bomb
            roam = True
        elif(level_state == 1):
            enemy_animation = load_animations_Arcane_Archer(64, 64)
            enemy_type = Ranged
            roam = True
        elif(level_state == 2):
            enemy_animation = load_animations_Medusa(crop_x= 40,crop_y= 55, crop_width=88, crop_height=73)
            enemy_type = Medusa
            roam = False
            x = 88
            y = 73
        elif(level_state == 3):
            enemy_animation = load_animations_Goblin(150,150,crop_x= 60,crop_y= 65, crop_width=30, crop_height=35)
            enemy_type = Melee
            roam = True

        # An enemy that patrols horizontally and bounces at screen edges
        enemy = enemy_type(static_platform2.rect.x,  
                    static_platform2.rect.y, x, y,
                    speed=config.NPC_SPEED, 
                    platforms=platforms, 
                    projectiles=projectiles, 
                    all_sprites=all_sprites,fighter=fighter1, fighters=fighters,
                    animations=enemy_animation, roam=roam)
        if enemy_type == Medusa:
            enemy_animation = load_animations_Goblin(150,150,crop_x= 60,crop_y= 65, crop_width=30, crop_height=35)
            enemy_type = Melee
            roam = True
            x = 30
            y = 35
        enemy2 = enemy_type(static_platform3.rect.x + 1000,  
                    static_platform3.rect.y, x, y,
                    speed=config.NPC_SPEED, 
                    platforms=platforms, 
                    projectiles=projectiles, 
                    all_sprites=all_sprites,fighter=fighter1, fighters=fighters,
                    animations=enemy_animation, roam=roam)
        enemy3 = enemy_type(static_platform3.rect.x + 900,  
                    static_platform3.rect.y, x, y,
                    speed=config.NPC_SPEED, 
                    platforms=platforms, 
                    projectiles=projectiles, 
                    all_sprites=all_sprites,fighter=fighter1, fighters=fighters,
                    animations=enemy_animation, roam=roam)
        if enemy_type == Melee:
            support = Eye(static_platform3.rect.x + 1000, config.SCENE_HEIGHT*3/5 - 32
                    ,width=20, height=20, speed=0, animations=load_animations_Eye(32,32), platforms=platforms)
            all_sprites.add(static_platform3, moving_platform, static_platform2, fighter1, enemy,powerup,powerup2,powerup3,powerup4, enemy2, enemy3, support)
            enemies.add(enemy, enemy3, enemy2, support)
        else:
            # Add each object to the appropriate sprite groups for updating and drawing
            all_sprites.add(static_platform3, moving_platform, static_platform2, fighter1, enemy,powerup,powerup2,powerup3,powerup4, enemy2, enemy3)
            enemies.add(enemy, enemy3, enemy2)
        platforms.add(static_platform3, moving_platform, static_platform2)
        fighters.add(fighter1)
        power_ups.add(powerup,powerup2,powerup3,powerup4)

def draw_background():
    scene.fill((0, 0, 0))    
    scene.blit(background2, (config.SCENE_WIDTH/2, 0))
    scene.blit(background3, (config.SCENE_WIDTH/4, 0))
    scene.blit(background4, (config.SCENE_WIDTH*3/4, 0))
    scene.blit(background5, (0, 0))