# Load map preview images (300x150 for each map button)
import pygame


map1_preview = pygame.image.load("src/assets/images/background/country-platform-preview.png").convert_alpha()
map1_preview = pygame.transform.scale(map1_preview, (300, 150))
map2_preview = pygame.image.load("src/assets/images/nature_3/origbig.png").convert_alpha()
map2_preview = pygame.transform.scale(map2_preview, (300, 150))
map3_preview = pygame.image.load("src/assets/images/background/jesus/j1.jpg").convert_alpha()
map3_preview = pygame.transform.scale(map3_preview, (300, 150))
map4_preview = pygame.image.load("src/assets/images/nature_1/orig.png").convert_alpha()
map4_preview = pygame.transform.scale(map4_preview, (300, 150))

# Define map buttons (positioned in a 2x2 grid)
map1_button = pygame.Rect(150, 100, 300, 150)  # Top-left
map2_button = pygame.Rect(750, 100, 300, 150)  # Top-right
map3_button = pygame.Rect(150, 350, 300, 150)  # Bottom-left
map4_button = pygame.Rect(750, 350, 300, 150)  # Bottom-right