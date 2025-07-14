# my h & g    keys are broken so I put them here
import pygame
import config
from .base import GameObject

# Platform class that now accepts an optional image.
class Platform(GameObject):
    def __init__(self, x, y, width, height, color=(0, 255, 0), image_path=None):
        super().__init__(x, y, width, height, color, image_path)

# A platform that automatically moves within a specified range.
class MovingPlatform(Platform):
    """A platform that moves horizontally or vertically within a range."""
    def __init__(self, x, y, width, height, color=(0, 255, 0), range_x=0, range_y=0, speed=2):
        super().__init__(x, y, width, height, color)
        self.start_x = x  # Initial horizontal position to measure the movement range
        self.start_y = y  # Initial vertical position to measure the movement range
        self.range_x = range_x  # Maximum horizontal distance to move from the starting point
        self.range_y = range_y  # Maximum vertical distance to move from the starting point
        self.speed = speed  # Speed at which the platform moves
        self.direction = 1  # Direction multiplier; 1 for forward and -1 for reverse motion

    def update(self):
        # Update horizontal movement if applicable
        if self.range_x:
            self.rect.x += self.speed * self.direction
            if abs(self.rect.x - self.start_x) >= self.range_x:
                self.direction *= -1  # Reverse movement direction upon reaching range limit
        # Update vertical movement if applicable
        if self.range_y:
            self.rect.y += self.speed * self.direction
            if abs(self.rect.y - self.start_y) >= self.range_y:
                self.direction *= -1  # Reverse vertical direction upon reaching range limit



