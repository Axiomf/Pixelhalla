# player.py
import pygame

class Player:
    """
    This class represents the player character in our game.
    """
    def __init__(self, x, y, width, height, color):
        # The player's position on the screen (top-left corner)
        self.x = x
        self.y = y
        # The player's dimensions
        self.width = width
        self.height = height
        # The player's color
        self.color = color
        # The rectangle object is used for drawing and collision detection
        self.rect = (x, y, width, height)
        # The player's movement speed
        self.vel = 3

    def draw(self, win):
        """
        Draws the player on the given window surface.
        """
        pygame.draw.rect(win, self.color, self.rect)

    def move(self):
        """
        Handles player movement based on keyboard input.
        """
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.x -= self.vel
        if keys[pygame.K_RIGHT]:
            self.x += self.vel
        if keys[pygame.K_UP]:
            self.y -= self.vel
        if keys[pygame.K_DOWN]:
            self.y += self.vel

        # After moving, we must update the rect attribute to match the new x, y
        self.update_rect()

    def update_rect(self):
        """
        Updates the rectangle's position. This is important for drawing.
        """
        self.rect = (self.x, self.y, self.width, self.height)