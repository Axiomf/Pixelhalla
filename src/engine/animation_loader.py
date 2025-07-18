import pygame
# trying to make a general template  for loading animations outside of objects, dict : ( "state" : frames )
def load_animations_template(path, frame_width, frame_height, colorkey=None,
                                   scale=1, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    """ "walk", "death" """
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
################################################################
# these have shared loader: HellDude, Eye,

def load_animations_Suicide_Bomber(path, frame_width, frame_height, colorkey=None,
                                   scale=1, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    """ "walk", "death" """
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
    frames.clear()
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
    animations["death"] = frames
################################################################
    return animations

def load_animations_Arcane_Archer(path, frame_width, frame_height, colorkey=None,
                                   scale=1, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    """ "walk", "death" , "shoot" """
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
    frames.clear()
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
    frames.clear()
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
    frames.clear()
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
    frames.clear()
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
    frames.clear()
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
    frames.clear()
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

def load_animations_Eye(path, frame_width, frame_height, colorkey=None,
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

def load_animations_Medusa(path_list, frame_width, frame_height, colorkey=None,
                                   scale=1, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    """ "idle" "hurt" "walk" "death" "attack" """
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






