import pygame
import config

class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Platform(GameObject):
    def __init__(self, x, y, width, height, color=(0, 255, 0)):
        super().__init__(x, y, width, height, color)

class DynamicObject(GameObject):
    """Base class for objects that can move or be affected by forces."""
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height, color)
        self.change_x = 0
        self.change_y = 0

    def update(self):
        self.calc_grav()
        self.rect.x += self.change_x
        self.rect.y += self.change_y

    def calc_grav(self):
        # If falling, simulate gravity
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += 0.35

class Player(DynamicObject):
    def __init__(self, x, y, width=30, height=30, color=(0, 0, 255)):
        super().__init__(x, y, width, height, color)

    def update(self):
        # Override update to include player-specific behavior if needed
        super().update()
        # Collision handling or other logic may be added here

class Fighter(Player):
    """
    Fighter class with controls for left/right movement and jumping.
    Each fighter can have custom keys assigned via the `controls` dict.
    Example controls dict:
        {
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_w
        }
    """
    def __init__(self, x, y, width=30, height=30, color=(0, 0, 255), controls=None):
        super().__init__(x, y, width, height, color)
        self.controls = controls or {}
        self.speed = 5
        self.jump_strength = -10

    def update(self):
        keys = pygame.key.get_pressed()
        if self.controls.get("left") and keys[self.controls["left"]]:
            self.rect.x -= self.speed
        if self.controls.get("right") and keys[self.controls["right"]]:
            self.rect.x += self.speed
        if self.controls.get("jump") and keys[self.controls["jump"]]:
            # Only apply jump if on ground (simplistic check)
            if self.change_y == 0:
                self.change_y = self.jump_strength
        super().update()

class MovingPlatform(Platform):
    """A platform that moves horizontally or vertically within a range."""
    def __init__(self, x, y, width, height, color=(0, 255, 0), range_x=0, range_y=0, speed=2):
        super().__init__(x, y, width, height, color)
        self.start_x = x
        self.start_y = y
        self.range_x = range_x
        self.range_y = range_y
        self.speed = speed
        self.direction = 1  # 1 = forward, -1 = backward

    def update(self):
        if self.range_x:
            self.rect.x += self.speed * self.direction
            if abs(self.rect.x - self.start_x) >= self.range_x:
                self.direction *= -1
        if self.range_y:
            self.rect.y += self.speed * self.direction
            if abs(self.rect.y - self.start_y) >= self.range_y:
                self.direction *= -1

class Enemy(DynamicObject):
    """A simple enemy that moves horizontally and bounces at the screen edges."""
    def __init__(self, x, y, width=30, height=30, color=(255, 0, 0), speed=2):
        super().__init__(x, y, width, height, color)
        self.change_x = speed

    def update(self):
        self.rect.x += self.change_x
        if self.rect.right > config.scene_WIDTH or self.rect.left < 0:
            self.change_x *= -1
        # Enemy can also be affected by gravity if needed.
        self.calc_grav()
        self.rect.y += self.change_y

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((config.scene_WIDTH, config.scene_HEIGHT))
    pygame.display.set_caption(config.CAPTION)
    clock = pygame.time.Clock()

    # Create groups for sprites
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    # Create some sample objects
    static_platform = Platform(100, 500, 400, 20)
    moving_platform = MovingPlatform(100, 400, 200, 20, range_x=150, speed=3)
    fighter1 = Fighter(150, 450, color=(0, 0, 255), controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w})
    fighter2 = Fighter(350, 450, color=(255, 255, 0), controls={"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP})
    enemy = Enemy(50, 300, speed=2)

    all_sprites.add(static_platform, moving_platform, fighter1, fighter2, enemy)
    platforms.add(static_platform, moving_platform)
    enemies.add(enemy)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update objects
        all_sprites.update()

        # Draw everything
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()