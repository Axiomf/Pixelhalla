import pygame  # Import pygame for sprite and game functions
import config  # Import configuration settings such as scene dimensions

# Base class for all game objects derived from pygame's Sprite class.
class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()  # Initialize the pygame Sprite base class
        self.image = pygame.Surface([width, height])  # Create a new surface for the object
        self.image.fill(color)  # Fill the object surface with the specified color
        self.rect = self.image.get_rect()  # Get the rectangular area of the surface
        self.rect.x = x  # Set the horizontal position of the object
        self.rect.y = y  # Set the vertical position of the object

# Platform class that represents static surfaces for characters to stand on.
class Platform(GameObject):
    def __init__(self, x, y, width, height, color=(0, 255, 0)):
        super().__init__(x, y, width, height, color)

# Base class for objects that require movement or are affected by physics (e.g., gravity).
class DynamicObject(GameObject):
    """Base class for objects that can move or be affected by forces."""
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height, color)
        self.change_x = 0  # Horizontal velocity
        self.change_y = 0  # Vertical velocity

    def update(self):
        self.calc_grav()  # Adjust vertical velocity due to gravity
        self.rect.x += self.change_x  # Update horizontal position
        self.rect.y += self.change_y  # Update vertical position

    def calc_grav(self):
        # Basic gravity simulation: if not already falling, start falling.
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += 0.35  # Acceleration due to gravity

    def handle_platform_collision(self, platforms):
        """
        Checks for collision with any platform in the provided group.
        If falling and colliding with a platform, adjust the vertical position
        to stand on the platform and reset vertical velocity.
        """
        collided_platforms = pygame.sprite.spritecollide(self, platforms, False)
        for platform in collided_platforms:
            # Only resolve collision if falling downward.
            # Adjust so that object's bottom aligns with platform's top.
            if self.change_y > 0 and self.rect.bottom <= platform.rect.bottom:
                self.rect.bottom = platform.rect.top
                self.change_y = 0

# Player class that can later be expanded with collision detection and other behaviors.
class Player(DynamicObject):
    def __init__(self, x, y, width=30, height=30, color=(0, 0, 255)):
        super().__init__(x, y, width, height, color)

    def update(self):
        # Call DynamicObject's update to apply gravity and movement
        super().update()
        # Additional player-specific logic (e.g., collision checking) can be added externally

# Fighter class implements control logic for player actions such as movement and jumping.
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
        self.controls = controls or {}  # Store control keys for this fighter
        self.speed = 5  # Pixel movement per update for horizontal movement
        self.jump_strength = -10  # Vertical speed for jumping (negative to move up)

    def update(self):
        keys = pygame.key.get_pressed()  # Get the current state of keyboard keys
        # Move left if the assigned 'left' key is pressed
        if self.controls.get("left") and keys[self.controls["left"]]:
            self.rect.x -= self.speed
        # Move right if the assigned 'right' key is pressed
        if self.controls.get("right") and keys[self.controls["right"]]:
            self.rect.x += self.speed
        # Initiate jump if the 'jump' key is pressed (only if the fighter is on the ground)
        if self.controls.get("jump") and keys[self.controls["jump"]]:
            if self.change_y == 0:  # Simplistic ground check
                self.change_y = self.jump_strength
        # Call the parent's update to apply gravity and move the sprite
        super().update()

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

# Enemy class represents non-player adversaries that patrol and are affected by physics.
class Enemy(DynamicObject):
    """A simple enemy that moves horizontally and bounces at the screen edges."""
    def __init__(self, x, y, width=30, height=30, color=(255, 0, 0), speed=2):
        super().__init__(x, y, width, height, color)
        self.change_x = speed  # Set initial horizontal patrol speed

    def update(self):
        self.rect.x += self.change_x  # Move enemy horizontally
        # Reverse direction when enemy hits either side of the game scene
        if self.rect.right > config.scene_WIDTH or self.rect.left < 0:
            self.change_x *= -1
        # Apply gravity and update vertical position
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