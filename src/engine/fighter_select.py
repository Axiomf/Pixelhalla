import pygame
import config
from .platforms import *
from .dynamic_objects import *
from .base import CustomGroup


# Load fighter preview images (150x150 for each fighter button)
fighter1_preview = pygame.image.load("src/assets/images/fighter.png").convert_alpha()
fighter1_preview = pygame.transform.scale(fighter1_preview, (150, 150))
fighter2_preview = pygame.image.load("src/assets/images/fighter.png").convert_alpha()
fighter2_preview = pygame.transform.scale(fighter2_preview, (150, 150))
fighter3_preview = pygame.image.load("src/assets/images/fighter.png").convert_alpha()
fighter3_preview = pygame.transform.scale(fighter3_preview, (150, 150))
fighter4_preview = pygame.image.load("src/assets/images/fighter.png").convert_alpha()
fighter4_preview = pygame.transform.scale(fighter4_preview, (150, 150))

# Define fighter buttons (positioned in a 2x2 grid)
fighter1_button = pygame.Rect(225, 100, 150, 150)  # Top-left
fighter2_button = pygame.Rect(825, 100, 150, 150)  # Top-right
fighter3_button = pygame.Rect(225, 350, 150, 150)  # Bottom-left
fighter4_button = pygame.Rect(825, 350, 150, 150)  # Bottom-right
