import pygame
from PIL import Image  
import os
# trying to make a general template  for loading animations outside of objects, dict : ( "state" : frames )
# these have shared loader: HellDude, Eye,

def load_animations_Suicide_Bomber(frame_width = 40, frame_height = 32, colorkey=None,
                                   scale=1, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    """ "walk", "death" """
    path = "src/assets/images/inused_sheets/death_bomb.png"
    animations = {}
    frames = []
    sheet = pygame.image.load(path).convert_alpha()
    sheet_rect = sheet.get_rect()
    if crop_width == None:
        crop_width = frame_width
    if crop_height == None:
        crop_height = frame_height
################################################################
    for x in range(0, sheet_rect.width, frame_width):
            # Define the full frame
            full_frame = pygame.Rect(x, 0, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, 0 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["walk"] = frames
################################################################
    frames = []
    for x in range(0, frame_width*6, frame_width):
            # Define the full frame
            full_frame = pygame.Rect(x, frame_height, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, frame_height + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["death"] = frames
################################################################
    return animations

def load_animations_Arcane_Archer(frame_width= 64, frame_height= 64, colorkey=None,
                                   scale=1, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    """ "walk", "death" , "shoot" , "idle", "hurt" """
    path = "src/assets/images/inused_sheets/Arcane_Archer.png"
    animations = {} # output
    sheet = pygame.image.load(path).convert_alpha()
    sheet_rect = sheet.get_rect()
    frames = [] # slut for temporary storing frames
    if crop_width == None:
        crop_width = frame_width
    if crop_height == None:
        crop_height = frame_height
################################################################
    for x in range(0, sheet_rect.width, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, 0, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, 0 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["walk"] = frames
################################################################
    frames = []  # replaced frames.clear() with new list
    for x in range(0, sheet_rect.width, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, frame_height, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, frame_height + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["death"] = frames
################################################################
    frames = []  # replaced frames.clear() with new list
    for x in range(0, sheet_rect.width - frame_width, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, frame_height*3, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, frame_height*3 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["shoot"] = frames
################################################################
    frames = []  # replaced frames.clear() with new list
    for x in range(0, sheet_rect.width - frame_width*4, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, frame_height*5, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, frame_height*5 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["idle"] = frames
################################################################
    frames = []  # replaced frames.clear() with new list
    for x in range(0, sheet_rect.width - frame_width*4, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, frame_height*5, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, frame_height*5 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["hurt"] = frames
################################################################
    return animations

def load_animations_Deadly_Effect(path, frame_width, frame_height, colorkey=None,
                                   scale=1, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    """ "death" """
    animations = {} # output
    sheet = pygame.image.load(path).convert_alpha()
    sheet_rect = sheet.get_rect()
    frames = [] # slut for temporary storing frames
    if crop_width == None:
        crop_width = frame_width
    if crop_height == None:
        crop_height = frame_height
################################################################
    for x in range(0, sheet_rect.width, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, 0, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, 0 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["death"] = frames
    return animations

def load_animations_NightBorne(path, frame_width, frame_height, colorkey=None,
                                   scale=1, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    """ "idle" "walk", "death", "attack", "hurt" """
    animations = {} # output
    sheet = pygame.image.load(path).convert_alpha()
    sheet_rect = sheet.get_rect()
    frames = [] # slut for temporary storing frames
    if crop_width == None:
        crop_width = frame_width
    if crop_height == None:
        crop_height = frame_height
################################################################
    for x in range(0, frame_width*9, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, 0, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, 0 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["idle"] = frames
################################################################
    frames = []  # replaced frames.clear() with new list for walk
    for x in range(0, frame_width*6, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, frame_height, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, frame_height + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["walk"] = frames
################################################################
    frames = []  # replaced frames.clear() with new list for attack
    for x in range(0, frame_width*12, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, frame_height*2, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, frame_height*2 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["attack"] = frames
################################################################
    frames = []  # replaced frames.clear() with new list for hurt
    for x in range(0, frame_width*5, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, frame_height*3, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, frame_height*3 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["hurt"] = frames
################################################################
    frames = []  # replaced frames.clear() with new list for death
    for x in range(0, frame_width*23, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, frame_height*4, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, frame_height*4 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["death"] = frames
################################################################
    return animations

def load_animations_HellDude(path, frame_width, frame_height, colorkey=None,
                                   scale=1, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    """ "idle" """
    animations = {} # output
    sheet = pygame.image.load(path).convert_alpha()
    sheet_rect = sheet.get_rect()
    frames = [] # slut for temporary storing frames
    if crop_width == None:
        crop_width = frame_width
    if crop_height == None:
        crop_height = frame_height

################################################################
    frames.clear()
    for y in range(0, sheet_rect.height, frame_height):
            for x in range(0, sheet_rect.width, frame_width):
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                if scale != 1:
                    frame = pygame.transform.scale(frame, (int(frame_width*scale), int(frame_height*scale)))
                if colorkey is not None:
                    frame.set_colorkey(colorkey)
                frames.append(frame)
    animations["idle"] = frames
################################################################
    return animations

def load_animations_Eye(frame_width, frame_height, colorkey=None,
                                   scale=1, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    """ "idle" """
    path = "src/assets/images/inused_sheets/eye_idle.png"
    animations = {} # output
    sheet = pygame.image.load(path).convert_alpha()
    sheet_rect = sheet.get_rect()
    frames = [] # slut for temporary storing frames
    if crop_width == None:
        crop_width = frame_width
    if crop_height == None:
        crop_height = frame_height

################################################################
    frames.clear()
    for y in range(0, sheet_rect.height, frame_height):
            for x in range(0, sheet_rect.width, frame_width):
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                if scale != 1:
                    frame = pygame.transform.scale(frame, (int(frame_width*scale), int(frame_height*scale)))
                if colorkey is not None:
                    frame.set_colorkey(colorkey)
                frames.append(frame)
    animations["idle"] = frames
################################################################
    return animations

def load_animations_Medusa(frame_width=128, frame_height=128, colorkey=None,
                                   scale=1, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    """ "idle" "hurt" "walk" "death" "attack" """
    animations = {} # output
    path_list = {"idle" : "src/assets/images/inused_sheets/Medusa_purple/idle.png"
                 ,"hurt" : "src/assets/images/inused_sheets/Medusa_purple/hurt.png"
                 ,"walk" : "src/assets/images/inused_sheets/Medusa_purple/walk.png"
                 ,"death" : "src/assets/images/inused_sheets/Medusa_purple/death.png"
                 ,"attack" : "src/assets/images/inused_sheets/Medusa_purple/attack.png"}
    for action in path_list:
        sheet = pygame.image.load(path_list[action]).convert_alpha()
        sheet_rect = sheet.get_rect()
        frames = [] # slut for temporary storing frames
        if crop_width == None:
            crop_width = frame_width
        if crop_height == None:
            crop_height = frame_height

        for x in range(0, sheet_rect.width, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, 0, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, 0 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
            animations[action] = frames

    return animations


def load_animations_Goblin(frame_width, frame_height, colorkey=None,
                                   scale=1, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    """ "idle" "hurt" "walk" "death" "attack" """
    path_list = {"idle" : "src/assets/images/inused_sheets/Goblin/Idle.png",
             "walk" : "src/assets/images/inused_sheets/Goblin/Run.png",
             "death" : "src/assets/images/inused_sheets/Goblin/Death.png",
             "hurt" : "src/assets/images/inused_sheets/Goblin/Take Hit.png",
             "attack" : "src/assets/images/inused_sheets/Goblin/Attack.png"}
    animations = {} # output

    for action in path_list:
        sheet = pygame.image.load(path_list[action]).convert_alpha()
        sheet_rect = sheet.get_rect()
        frames = [] # slut for temporary storing frames
        if crop_width == None:
            crop_width = frame_width
        if crop_height == None:
            crop_height = frame_height

        for x in range(0, sheet_rect.width, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, 0, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, 0 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
            animations[action] = frames

    return animations


def load_animations_Boss(frame_width, frame_height, colorkey=None,
                                   scale=1, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    path = "src/assets/images/inused_sheets/helldude_idle.png"
    animations = {} # output
    sheet = pygame.image.load(path).convert_alpha()
    sheet_rect = sheet.get_rect()
    frames = [] # slut for temporary storing frames
    if crop_width == None:
        crop_width = frame_width
    if crop_height == None:
        crop_height = frame_height

################################################################
    frames.clear()
    for y in range(0, sheet_rect.height, frame_height):
            for x in range(0, sheet_rect.width, frame_width):
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                if scale != 1:
                    frame = pygame.transform.scale(frame, (int(frame_width*scale), int(frame_height*scale)))
                if colorkey is not None:
                    frame.set_colorkey(colorkey)
                frames.append(frame)
    animations["idle"] = frames
################################################################
    return animations

# heroes
def load_animations_Samurai(frame_width=96, frame_height=96, colorkey=None,
                                   scale=1, crop_x=31, crop_y=44, crop_width=35, crop_height=38):
    """ "idle" "hurt" "walk" "death" "attack" """
    animations = {} # output
    path_list = {   "idle" : "src/assets/images/inused_sheets/Samurai/idle.png"
                 ,  "hurt" : "src/assets/images/inused_sheets/Samurai/hurt.png"
                 ,  "walk" : "src/assets/images/inused_sheets/Samurai/walk.png"
                 ,"attack" : "src/assets/images/inused_sheets/Samurai/attack.png"}
    for action in path_list:
        sheet = pygame.image.load(path_list[action]).convert_alpha()
        sheet_rect = sheet.get_rect()
        frames = [] # slut for temporary storing frames
        if crop_width == None:
            crop_width = frame_width
        if crop_height == None:
            crop_height = frame_height

        for x in range(0, sheet_rect.width, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, 0, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, 0 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
            animations[action] = frames

    return animations

def load_animations_Elf_Archer(frame_width= 288, frame_height= 128, colorkey=None,
                                   scale=1, crop_x=113, crop_y=76, crop_width=60, crop_height=52):
    """ "walk", "death" , "shoot" , "idle" , "hurt", "signiture" """
    path = "src/assets/images/inused_sheets/Archer_elf/elf_288x128.png"
    animations = {} # output
    sheet = pygame.image.load(path).convert_alpha()
    sheet_rect = sheet.get_rect()
    frames = [] # slut for temporary storing frames
    if crop_width == None:
        crop_width = frame_width
    if crop_height == None:
        crop_height = frame_height
################################################################
    for x in range(0, frame_width*12, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, 0, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, 0 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["idle"] = frames
################################################################
    frames = []  # replaced frames.clear() with new list
    for x in range(0, frame_width*10, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, frame_height, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, frame_height + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["walk"] = frames
################################################################
    frames = []  # replaced frames.clear() with new list
    for x in range(0, frame_width*15, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, frame_height*11, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, frame_height*11 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["shoot"] = frames
################################################################
    frames = []  # replaced frames.clear() with new list
    for x in range(0, frame_width*17, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, frame_height*13, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, frame_height*13 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["signiture"] = frames
################################################################
    frames = []  # replaced frames.clear() with new list
    for x in range(0, frame_width*6, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, frame_height*15, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, frame_height*15 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["hurt"] = frames
################################################################
    frames = []  # replaced frames.clear() with new list
    for x in range(0, frame_width*19, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, frame_height*16, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, frame_height*16 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    animations["death"] = frames
################################################################
    return animations

def load_animations_Knight(frame_width=120, frame_height=80, colorkey=None,
                                   scale=1, crop_x=31, crop_y=35, crop_width=43, crop_height=44):
    """ "idle"  "walk" "death" "attack" """
    animations = {} # output
    path_list = {"idle" :    "src/assets/images/inused_sheets/Knight/idle.png"
                 ,"hurt" : "src/assets/images/inused_sheets/Knight/idle.png"
                 ,"walk" :   "src/assets/images/inused_sheets/Knight/walk.png"
                 ,"death" :  "src/assets/images/inused_sheets/Knight/death.png"
                 ,"attack" : "src/assets/images/inused_sheets/Knight/attack.png"}
    for action in path_list:
        sheet = pygame.image.load(path_list[action]).convert_alpha()
        sheet_rect = sheet.get_rect()
        frames = [] # slut for temporary storing frames
        if crop_width == None:
            crop_width = frame_width
        if crop_height == None:
            crop_height = frame_height

        for x in range(0, sheet_rect.width, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, 0, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, 0 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
            animations[action] = frames

    return animations

def load_animations_Electric_Warrior(frame_width=162, frame_height=162, colorkey=None,
                                   scale=1, crop_x=52, crop_y=49, crop_width=59, crop_height=54):
    """ "idle" "hurt" "walk" "death" "attack" """
    animations = {} # output
    path_list = {"idle" :    "src/assets/images/inused_sheets/Electric_Warrior/idle.png"
                 ,"hurt" :   "src/assets/images/inused_sheets/Electric_Warrior/hurt.png"
                 ,"walk" :   "src/assets/images/inused_sheets/Electric_Warrior/walk.png"
                 ,"death" :  "src/assets/images/inused_sheets/Electric_Warrior/death.png"
                 ,"attack" : "src/assets/images/inused_sheets/Electric_Warrior/attack.png"
               ,"signiture" :"src/assets/images/inused_sheets/Electric_Warrior/signiture.png" }
    for action in path_list:
        sheet = pygame.image.load(path_list[action]).convert_alpha()
        sheet_rect = sheet.get_rect()
        frames = [] # slut for temporary storing frames
        if crop_width == None:
            crop_width = frame_width
        if crop_height == None:
            crop_height = frame_height

        for x in range(0, sheet_rect.width, frame_width): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(x, 0, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(x + crop_x, 0 + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
            animations[action] = frames

    return animations



def load_animations_Cat(colorkey=None,# it has problems
                                   scale=1, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    """ "idle" "hurt" "walk" "death" "attack" """
    animations = {} # output
    path_list = {"idle" :    "src/assets/images/inused_sheets/Cat/idle.png"
                 ,"hurt" :   "src/assets/images/inused_sheets/Cat/hurt.png"
                 ,"walk" :   "src/assets/images/inused_sheets/Cat/walk.png"
                 ,"death" :  "src/assets/images/inused_sheets/Cat/death.png"
                 ,"attack" : "src/assets/images/inused_sheets/Cat/attack.png"
                 , "signiture" :"src/assets/images/inused_sheets/Cat/signiture.png" }
    frame_list = {"idle" : [32,31]
                   ,"hurt":[32,24]
                   ,"walk":[16,23]
                   ,"death":[16,24]
                   ,"attack":[80,41]
                   ,"signiture":[16,29]}
    for action in path_list:
        frame_width = frame_list[action][0]
        frame_height = frame_list[action][1]
        scale_width  = 1
        scale_height = 1
        sheet = pygame.image.load(path_list[action]).convert_alpha()
        sheet_rect = sheet.get_rect()
        frames = [] # slut for temporary storing frames
        if crop_width == None:
            crop_width = frame_width
        if crop_height == None:
            crop_height = frame_height

        for y in range(0, sheet_rect.height, frame_height): # first row is ""
            # Define the full frame
            full_frame = pygame.Rect(0, y, frame_width, frame_height)
            # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
            crop_rect = pygame.Rect(0 + crop_x, y + crop_y, crop_width, crop_height)
            frame = sheet.subsurface(crop_rect)
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(crop_width * scale), int(crop_height * scale)))
            if colorkey is not None:
                frame.set_colorkey(colorkey)
            frames.append(frame)
            animations[action] = frames

    return animations

def load_animations_Witch(colorkey=None,# it has problems
                                   scale=1, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    """ "idle" "hurt" "walk" "death" "attack" """
    animations = {} # output
    path_list = { "idle" :    "src/assets/images/inused_sheets/Witch/idle.png"
                 ,"hurt" :   "src/assets/images/inused_sheets/Witch/hurt.png"
                 ,"walk" :   "src/assets/images/inused_sheets/Witch/walk.png"
                 ,"death" :  "src/assets/images/inused_sheets/Witch/death.png"
                 ,"attack" : "src/assets/images/inused_sheets/Witch/attack.png"
                 , "signiture" :"src/assets/images/inused_sheets/Witch/signiture.png" }
    frame_list = {"idle" : [32,48]
                   ,"hurt":[32,48]
                   ,"walk":[32,48]
                   ,"death":[32,40]
                   ,"attack":[104,46]
                   ,"signiture":[48,48]}
    

    for action in path_list:
        frame_width = frame_list[action][0]
        frame_height = frame_list[action][1]
        scale_width  = 32 / frame_list[action][0]
        scale_height = 48 / frame_list[action][1]

        sheet = pygame.image.load(path_list[action]).convert_alpha()
        sheet_rect = sheet.get_rect()
        frames = [] # slut for temporary storing frames
        if crop_width == None:
            crop_width = frame_width
        if crop_height == None:
            crop_height = frame_height

        for y in range(0, sheet_rect.height, frame_height):
            for x in range(0, sheet_rect.width, frame_width):
                # Define the full frame
                full_frame = pygame.Rect(x, 0, frame_width, frame_height)
                # Crop to the character section (default is full frame, adjust crop_x, crop_y, crop_width, crop_height)
                crop_rect = pygame.Rect(x + crop_x, 0 + crop_y, crop_width, crop_height)
                frame = sheet.subsurface(crop_rect)
                if scale != 1:
                    frame = pygame.transform.scale(frame, (int(crop_width * scale_width), int(crop_height * scale_height)))
                if colorkey is not None:
                    frame.set_colorkey(colorkey)
                frames.append(frame)
            animations[action] = frames

    return animations

