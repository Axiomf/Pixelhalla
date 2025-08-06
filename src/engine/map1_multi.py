import pygame
import config
from src.engine.platforms import *
from src.engine.dynamic_objects import *
from src.engine.base import CustomGroup
from src.engine.animation_loader import *

scene = pygame.display.set_mode((config.SCENE_WIDTH, config.SCENE_HEIGHT))
background = pygame.image.load("src/assets/images/background/map-ShorwindFishingPort.png")
background = pygame.transform.scale(background, (config.SCENE_WIDTH, config.SCENE_HEIGHT))

all_sprites = CustomGroup()
platforms = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
fighters = pygame.sprite.Group()

def create_fighter(fighter_id, client_id, username, platforms, fighters_group):
    """Create a fighter based on fighter_id with client_id and username."""
    if fighter_id == "fighter1":
        return Fighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms,
                       controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                       animations=load_animations_Elf_Archer(), username=username, id=client_id)
    elif fighter_id == "fighter2":
        return MeleeFighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms, fighters=fighters_group,
                            controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "attack": pygame.K_SPACE},
                            animations=load_animations_Samurai(scale=1), username=username, id=client_id)
    elif fighter_id == "fighter3":
        return MeleeFighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms, fighters=fighters_group,
                            controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "attack": pygame.K_SPACE},
                            animations=load_animations_Knight(scale=1), username=username, id=client_id)
    elif fighter_id == "fighter4":
        return Fighter(450, config.SCENE_HEIGHT*3/5 - 70, 32, 32, platforms=platforms,
                       controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                       animations=load_animations_Arcane_Archer(scale=1), username=username, id=client_id)
    return None

def load_map(level_state, fighter1_id, fighter2_id, fighter_select_phase, client_id, username):
    platforms.empty()
    fighters.empty()
    all_sprites.empty()
    static_platform1 = Platform(config.SCENE_WIDTH*2/8 + 73, config.SCENE_HEIGHT*3/5 - 11, 
                               config.SCENE_WIDTH*3/8, config.SCENE_HEIGHT*1/200, color=None)
    static_platform2 = Platform(config.SCENE_WIDTH*2/8 + 88, config.SCENE_HEIGHT*2/5 + 13, 
                               130, config.SCENE_HEIGHT*1/200, color=None)
    static_platform3 = Platform(680, config.SCENE_HEIGHT*2/5 + 14, 
                               130, config.SCENE_HEIGHT*1/200, color=None)
    platforms.add(static_platform1, static_platform2, static_platform3)
    all_sprites.add(static_platform1, static_platform2, static_platform3)
    
    # Create fighter for this client
    fighter = create_fighter(fighter1_id, client_id, username, platforms, fighters)
    if fighter:
        fighters.add(fighter)
        all_sprites.add(fighter)
    
    return {"fighters": fighters, "platforms": platforms}  # Return both fighters and platforms

def draw_background():
    scene.fill((0, 0, 0))
    scene.blit(background, (0, 0))