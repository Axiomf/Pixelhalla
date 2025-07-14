# my h & g keys are broken so I put them here
import pygame

# Updated GameObject that uses an image if provided.
class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, image_path=None):
        super().__init__()
        if image_path:
            # Load image and scale to desired size.
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (int(width), int(height)))
        else:
            # Fallback: create a simple colored rectangle.
            self.image = pygame.Surface([width, height])
            self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y




import pygame

class CustomGroup(pygame.sprite.Group):
    def draw(self, surface):
        # Draw all sprites (their image and rect)
        super().draw(surface)
        # Now draw extra elements (like health bars) if available
        for sprite in self.sprites():
            if hasattr(sprite, "draw_health_bar"):
                sprite.draw_health_bar(surface)
        