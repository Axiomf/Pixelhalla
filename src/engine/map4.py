from .platforms import *
from .dynamic_objects import *
from .base import CustomGroup
from .animation_loader import *




scene = pygame.display.set_mode((config.SCENE_WIDTH, config.SCENE_HEIGHT))  # Set up the main game window
# Load a background image located in the assets folder
background = pygame.image.load("src/assets/images/background/twilightgrove.png")
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
    powerup = PowerUp(500, config.SCENE_HEIGHT - 50,"double_jump",5, width=50, height=50, color=(255,255,0), image_path="src/assets/images/inused_single_images/damage.png")
    powerup2 = PowerUp(100, config.SCENE_HEIGHT - 30,"damage",20, width=10, height=10, color=(150,0,0))
    powerup3 = PowerUp(300, config.SCENE_HEIGHT - 30,"shield",20, width=10, height=10, color=(150,0,0))
    powerup4 = PowerUp(900, config.SCENE_HEIGHT - 30,"supershot",4, width=10, height=10, color=(75,75,75))
    static_platform1 = Platform(config.SCENE_WIDTH*2/8 + 140, config.SCENE_HEIGHT*3/5 + 63, 
                            355,config.SCENE_HEIGHT*1/200, 
                            color=(0,0,0))#this is the main platform


    static_platform4 = Platform(config.SCENE_WIDTH*2/8 + 530, config.SCENE_HEIGHT*3/5 - 70, 
                            240,config.SCENE_HEIGHT*1/200, 
                            color=(0,0,0))#this is the main platform

    static_platform2 = Platform(config.SCENE_WIDTH*2/8 - 60, config.SCENE_HEIGHT*2/5 - 20, 
                            355,config.SCENE_HEIGHT*1/200, 
                            color=(0,0,0))
    static_platform3 = Platform(693, config.SCENE_HEIGHT*2/5 - 6, 
                            153,config.SCENE_HEIGHT*1/200, 
                            color=(0,0,0))
    static_platform5 = Platform(935, config.SCENE_HEIGHT*2/5 - 70, 
                            130,config.SCENE_HEIGHT*1/200, 
                            color=(0,0,0))
    
    if fighter1_id == "fighter1":
            fighter1 = Fighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   animations=load_animations_Elf_Archer())
    elif fighter1_id == "fighter2":
        fighter1 = MeleeFighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, health=20, platforms=platforms, enemies=enemies, fighters=fighters,
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
        all_sprites.add(static_platform1, static_platform2,static_platform3, static_platform4, fighter1, fighter2)
        platforms.add(static_platform1, static_platform2, static_platform3, static_platform4)
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

        # Add each object to the appropriate sprite groups for updating and drawing
        all_sprites.add(static_platform1, static_platform2,static_platform3, static_platform4, fighter1, enemy, static_platform5,powerup,powerup2,powerup3,powerup4)
        platforms.add(static_platform1, static_platform2, static_platform3, static_platform4, static_platform5)
        enemies.add(enemy)
        melee.add(enemy)
        fighters.add(fighter1)
        power_ups.add(powerup,powerup2,powerup3,powerup4)

def draw_background():
    scene.fill((0, 0, 0))
    scene.blit(background, (0, 0))
        