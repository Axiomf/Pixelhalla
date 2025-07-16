import pygame

# Updated GameObject that uses an image if provided.
class GameObject(pygame.sprite.Sprite):
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
    # polymorphic function to load frames from a sprite sheet, it will be rewritten for each charrecter
    def load_sprite_sheet(self,path, frame_width, frame_height, colorkey=None, scale=1):
        sheet = pygame.image.load(path).convert_alpha()
        sheet_rect = sheet.get_rect()
        frames = []
        for y in range(0, sheet_rect.height, frame_height):
            for x in range(0, sheet_rect.width, frame_width):
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                if scale != 1:
                    frame = pygame.transform.scale(frame, (int(frame_width*scale), int(frame_height*scale)))
                if colorkey is not None:
                    frame.set_colorkey(colorkey)
                frames.append(frame)
        return frames
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