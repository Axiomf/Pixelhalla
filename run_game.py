import pygame
import config
from src.engine.game import *

pygame.init()
screen = pygame.display.set_mode((config.scene_WIDTH, config.scene_HEIGHT))
pygame.display.set_caption(config.CAPTION)
clock = pygame.time.Clock()

# Create groups for sprites
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# Create game objects
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
