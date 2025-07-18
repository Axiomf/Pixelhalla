import pygame
# trying to make a general template  for loading animations outside of objects, dict : ( "state" : frames )

def load_animations_template(path, frame_width, frame_height, colorkey=None,
                                   scale=1, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    """ "walk", "death" ("run" is the same as walk with increased speed)"""
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

# (Suicide_bomber is an example)
def load_animations_Suicide_Bomber(path, frame_width, frame_height, colorkey=None,
                                   scale=1, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    """ "walk", "death" ("run" is the same as walk with increased speed)"""
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
