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
melee = pygame.sprite.Group()
power_ups = pygame.sprite.Group()

def load_map(level_state, fighter1_id, fighter2_id, fighter_select_phase):
    static_platform1 = Platform(config.SCENE_WIDTH*2/8 + 73, config.SCENE_HEIGHT*3/5 - 11, 
                            config.SCENE_WIDTH*3/8,config.SCENE_HEIGHT*1/200, 
                            color=None)#this is the main platform

    static_platform2 = Platform(config.SCENE_WIDTH*2/8 + 88, config.SCENE_HEIGHT*2/5 + 13, 
                            130,config.SCENE_HEIGHT*1/200, 
                            color=None)
    static_platform3 = Platform(680, config.SCENE_HEIGHT*2/5 + 14, 
                            130,config.SCENE_HEIGHT*1/200, 
                            color=None)
    powerup = PowerUp(500, config.SCENE_HEIGHT - 30,"double_jump",5, width=50, height=50, color=(255,255,0), image_path="src/assets/images/inused_single_images/double_jump.png", all_sprites=all_sprites, power_ups=power_ups, platforms=platforms)
    powerup2 = PowerUp(100, config.SCENE_HEIGHT - 30,"damage",20, width=50, height=50, color=(150,0,0), image_path="src/assets/images/inused_single_images/damage.png", all_sprites=all_sprites, power_ups=power_ups, platforms=platforms)
    powerup3 = PowerUp(300, config.SCENE_HEIGHT - 30,"shield",20, width=50, height=50, color=(150,0,0), image_path="src/assets/images/inused_single_images/shield.png", all_sprites=all_sprites, power_ups=power_ups, platforms=platforms)
    powerup4 = PowerUp(900, config.SCENE_HEIGHT - 30,"supershot",4, width=50, height=50, color=(75,75,75), image_path="src/assets/images/inused_single_images/supershot.png",all_sprites=all_sprites, power_ups=power_ups, platforms=platforms)

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
        all_sprites.add(static_platform1, static_platform2,static_platform3, fighter1, fighter2)
        platforms.add(static_platform1, static_platform2, static_platform3)
        fighters.add(fighter1, fighter2)
    else:    

        if(level_state == 0):
            enemy_animation = load_animations_Arcane_Archer(scale=1)
            enemy_type = Ranged
        elif(level_state == 1):
            enemy_animation = load_animations_Goblin(150,150,crop_x= 60,crop_y= 65, crop_width=30, crop_height=35)
            enemy_type = Melee
        elif(level_state == 2):
            enemy_animation = load_animations_Goblin(150,150,crop_x= 60,crop_y= 65, crop_width=30, crop_height=35)
            enemy_type = Melee
        elif(level_state == 3):
            enemy_animation = load_animations_Goblin(150,150,crop_x= 60,crop_y= 65, crop_width=30, crop_height=35)
            enemy_type = Melee

        # An enemy that patrols horizontally and bounces at screen edges
        enemy = enemy_type(static_platform1.rect.x + 250,  
                    static_platform1.rect.y, 30, 35,
                    speed=config.NPC_SPEED, 
                    platforms=platforms, 
                    projectiles=projectiles, 
                    all_sprites=all_sprites,fighter=fighter1, fighters=fighters,
                    animations=enemy_animation)
        enemy2 = enemy_type(static_platform2.rect.x,  
                    static_platform2.rect.y, 30, 35,
                    speed=config.NPC_SPEED, 
                    platforms=platforms, 
                    projectiles=projectiles, 
                    all_sprites=all_sprites,fighter=fighter1, fighters=fighters,
                    animations=enemy_animation)
        enemy3 = enemy_type(static_platform3.rect.x,  
                    static_platform3.rect.y, 30, 35,
                    speed=config.NPC_SPEED, 
                    platforms=platforms, 
                    projectiles=projectiles, 
                    all_sprites=all_sprites,fighter=fighter1, fighters=fighters,
                    animations=enemy_animation)

        # Add each object to the appropriate sprite groups for updating and drawing
        all_sprites.add(static_platform1, static_platform2,static_platform3, fighter1, enemy,powerup,powerup2,powerup3,powerup4, enemy2, enemy3)
        platforms.add(static_platform1, static_platform2, static_platform3)
        enemies.add(enemy, enemy3, enemy2)
        melee.add(enemy)
        fighters.add(fighter1)
        power_ups.add(powerup,powerup2,powerup3,powerup4)

def draw_background():
    scene.fill((0, 0, 0))
    scene.blit(background, (0, 0))
        