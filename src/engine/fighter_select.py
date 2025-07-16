import pygame
import config
from .platforms import *
from .dynamic_objects import *
from .base import CustomGroup

# Define fighter buttons (positioned in a 2x2 grid)
fighter1_button = pygame.Rect(225, 100, 150, 150)  # Top-left
fighter2_button = pygame.Rect(825, 100, 150, 150)  # Top-right
fighter3_button = pygame.Rect(225, 350, 150, 150)  # Bottom-left
fighter4_button = pygame.Rect(825, 350, 150, 150)  # Bottom-right