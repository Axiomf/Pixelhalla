# my h & g keys are broken so I put them here
import pygame  # Import pygame for game functionality
import config  # Import configuration settings like scene dimensions and FPS

pygame.init()  # Initialize all imported pygame modules
pygame.display.set_caption(config.CAPTION) # Set the window title using the caption defined in config
clock = pygame.time.Clock()# Create a clock to manage the game's frame rate
# import from maps for example map1
from src.engine.map1 import *
from src.engine.loading_page import *

# game loop
while game_state:
    # Handle events in loading screen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Check for left mouse click
            if start_button.collidepoint(event.pos):  # Check if button is clicked
                game_state = GAME_STATE_PLAYING  # Switch to main game
    scene.fill((0, 0, 0))
    scene.blit(loading_background, (0, 0))
    pygame.draw.rect(scene, button_color, start_button)  # Draw button
    scene.blit(button_text, button_text_rect)  # Draw button text
    pygame.display.flip()  # Update display

running = True
while running:
    # Process input events (such as closing the window or shooting projectiles)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # If the shoot key for fighter1 is pressed, spawn a projectile.
            if event.key == fighter1.controls.get("shoot"):
                projectile = fighter1.shoot()
                all_sprites.add(projectile)
                projectiles.add(projectile)
    # Update all game objects (calls update() on each sprite in all_sprites)
    all_sprites.update()

    # Handle collisions so dynamic objects can stand on platforms.
    for sprite in all_sprites:
        if isinstance(sprite, DynamicObject):
            sprite.handle_platform_collision(platforms)
        if isinstance(sprite, Projectile):
            # Check for collisions with enemies and remove the projectile if it hits
            hit_enemies = pygame.sprite.spritecollide(sprite, enemies, False)
            if hit_enemies:
                for enemy in hit_enemies:
                    enemy.take_damage(sprite.damage)
                    sprite.kill()
            # Check for collisions with fighters, but not with the projectile's owner
            hit_fighters = pygame.sprite.spritecollide(sprite, fighters, False)
            for fighter in hit_fighters:
                if fighter != sprite.owner:  # Prevent projectile from damaging its owner
                    fighter.take_damage(sprite.damage)
                    sprite.kill()
            hit_platforms = pygame.sprite.spritecollide(sprite,platforms, False)
            for platform in hit_platforms:
                sprite.kill()
               
    
    # Draw phase: clear the screen, draw background, and then all sprites
    scene.fill((0, 0, 0))
    scene.blit(background, (0, 0))
    all_sprites.draw(scene)
    for sprite in all_sprites:
        if isinstance(sprite, Player):  #NFC and Fither
            sprite.draw_health_bar(scene)
    pygame.display.flip()  # Refresh the ng = Falsedisplay
    clock.tick(config.FPS)  # Maintain the FPS defined in config

pygame.quit()  # Clean up and close the pygame window
