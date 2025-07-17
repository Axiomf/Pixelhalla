import pygame

# Updated GameObject that uses an image if provided.
class GameObject(pygame.sprite.Sprite):
    """Base class for objects that can move or be affected by forces."""
    def __init__(self, x, y, width, height, color=None, image_path=None):
        super().__init__()
        if image_path:
            # Load image and scale to desired size.
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (int(width), int(height)))
        elif color:
            # Fallback: create a simple colored rectangle.
            self.image = pygame.Surface([width, height])
            self.image.fill(color)
        else:
            # No image or color provided, set image to None.
            self.image = None
        self.rect = pygame.Rect(x, y, width, height)
            
    
class CustomGroup(pygame.sprite.Group):
    def draw(self, surface):
        # Draw all sprites (their image and rect)
        for sprite in self.sprites():
            if hasattr(sprite, "image") and sprite.image is not None:
                surface.blit(sprite.image, sprite.rect)
        # Now draw extra elements (like health bars) if available
        for sprite in self.sprites():
            if hasattr(sprite, "draw_health_bar"):
                sprite.draw_health_bar(surface)