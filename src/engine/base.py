# my h & g keys are broken so I put them here
import pygame

# Base class for all game objects derived from pygame's Sprite class.
class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()  # Initialize the pygame Sprite base class
        self.image = pygame.Surface([width, height])  # Create a new surface for the object
        self.image.fill(color)  # Fill the object surface with the specified color
        self.rect = self.image.get_rect()  # Get the rectangular area of the surface
        self.rect.x = x  # Set the horizontal position of the object
        self.rect.y = y  # Set the vertical position of the object