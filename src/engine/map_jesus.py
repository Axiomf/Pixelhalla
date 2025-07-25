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

moving_platform = MovingPlatform(config.SCENE_WIDTH/8, config.SCENE_HEIGHT/4,
                                 config.SCENE_WIDTH/4, 10, range_x=150, range_y=0, speed=1)





def load_map(level_state, fighter1_id, fighter2_id, fighter_select_phase):
    powerup = PowerUp(500, config.SCENE_HEIGHT - 30,"double_jump",5, width=10, height=10, color=(255,255,0))
    powerup2 = PowerUp(100, config.SCENE_HEIGHT - 30,"damage",20, width=10, height=10, color=(150,0,0))
    powerup3 = PowerUp(300, config.SCENE_HEIGHT - 30,"shield",20, width=10, height=10, color=(150,0,0))
    powerup4 = PowerUp(900, config.SCENE_HEIGHT - 30,"supershot",4, width=10, height=10, color=(75,75,75))
    static_platform3 = Platform(0, config.SCENE_HEIGHT - 20, 
                            1200, 20, 
                            color=(139, 140, 78))

    moving_platform = MovingPlatform(config.SCENE_WIDTH/8, config.SCENE_HEIGHT/4,
                                    config.SCENE_WIDTH/4, 10, range_x=150, range_y=0, speed=1)
    
    if fighter1_id == "fighter1":
            fighter1 = Fighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   animations=load_animations_Elf_Archer())
    elif fighter1_id == "fighter2":
        fighter1 = MeleeFighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms,  enemies=enemies, fighters=fighters,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "attck": pygame.K_SPACE},
                   animations=load_animations_Samurai(scale=1))
    elif fighter1_id == "fighter3":
        fighter1 = MeleeFighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms,  enemies=enemies, fighters=fighters,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "attack": pygame.K_SPACE},
                   animations=load_animations_Knight(scale=1))
    elif fighter1_id == "fighter4":
        fighter1 = Fighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   animations=load_animations_Arcane_Archer(scale=1))
        
    ##############
    if fighter_select_phase == "multi":
        if fighter2_id == "fighter1":
           fighter2 = Fighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   animations=load_animations_Arcane_Archer(scale=1))
        elif fighter2_id == "fighter2":
            fighter2 = Fighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms, fighters=fighters,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "attack": pygame.K_SPACE},
                   animations=load_animations_Arcane_Archer(scale=1))
        elif fighter2_id == "fighter3":
            fighter2 = Fighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms, fighters=fighters,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "attack": pygame.K_SPACE},
                   animations=load_animations_Arcane_Archer(scale=1))
        elif fighter2_id == "fighter4":
            fighter2 = Fighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms,
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   animations=load_animations_Arcane_Archer(scale=1))
        all_sprites.add(static_platform3, moving_platform,powerup,powerup2,powerup3,powerup4 ,fighter1, fighter2)
        platforms.add(static_platform3, moving_platform)
        fighters.add(fighter1, fighter2)
    else:    

        # if(level_state == 0):
        #     enemy_animation = load_animations_Goblin(150,150,crop_x= 60,crop_y= 65, crop_width=30, crop_height=35)
        #     enemy_type = Melee
        # elif(level_state == 1):
        #     enemy_animation = load_animations_Goblin(150,150,crop_x= 60,crop_y= 65, crop_width=30, crop_height=35)
        #     enemy_type = Melee
        # elif(level_state == 2):
        #     enemy_animation = load_animations_Goblin(150,150,crop_x= 60,crop_y= 65, crop_width=30, crop_height=35)
        #     enemy_type = Melee
        # elif(level_state == 3):
        #     enemy_animation = load_animations_Goblin(150,150,crop_x= 60,crop_y= 65, crop_width=30, crop_height=35)
        #     enemy_type = Melee

        melee_enemy = Medusa(config.SCENE_WIDTH/4 + 350, config.SCENE_HEIGHT*3/5 - 170, 128, 128,
                    speed=config.NPC_SPEED, platforms=platforms, projectiles=projectiles,
                    all_sprites=all_sprites, fighter=fighter1,
                    animations=load_animations_Medusa(),roam=False,damage = 10)

        support = Eye(900, config.SCENE_HEIGHT*3/5 - 32
                    ,width=20, height=20, speed=0, animations=load_animations_Eye(32,32), platforms=platforms)

        death_bomb = Suicide_Bomb(1100, config.SCENE_HEIGHT*3/5 - 32
                                , speed=2, health=50, 
                        damage=20, platforms=platforms, projectiles=projectiles, 
                        all_sprites=all_sprites, fighter=fighter1, animations=load_animations_Suicide_Bomber(), roam=True)

        ranged_enemy = Ranged(config.SCENE_WIDTH/4 + 200, config.SCENE_HEIGHT*3/5 - 32, 32, 32,
                            speed=config.NPC_SPEED, platforms=platforms, projectiles=projectiles,
                            all_sprites=all_sprites, fighter=fighter1,
                            animations=load_animations_Arcane_Archer(64, 64),roam=False)
        # Add each object to the appropriate sprite groups for updating and drawing
        all_sprites.add(moving_platform, fighter1, static_platform3,powerup,powerup2,powerup3,powerup4, ranged_enemy,melee_enemy,support,death_bomb)
        platforms.add(moving_platform, static_platform3)
        enemies.add(ranged_enemy,melee_enemy,support,death_bomb)
        fighters.add(fighter1)

def draw_background():
    scene.fill((0, 0, 0))    
    scene.blit(background2, (config.SCENE_WIDTH/2, 0))
    scene.blit(background3, (config.SCENE_WIDTH/4, 0))
    scene.blit(background4, (config.SCENE_WIDTH*3/4, 0))
    scene.blit(background5, (0, 0))