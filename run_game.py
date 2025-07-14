import pygame  # Import pygame for game functionality
import config  # Import configuration settings like scene dimensions and FPS

# Initialize pygame
pygame.init()  # Initialize all imported pygame modules
pygame.display.set_caption(config.CAPTION)  # Set the window title
scene = pygame.display.set_mode((config.SCENE_WIDTH, config.SCENE_HEIGHT))  # Set up the main game window
clock = pygame.time.Clock()  # Create a clock to manage the game's frame rate
from src.engine.loading_page import *

# Import from maps after loading screen setup to avoid resetting game_state
from src.engine.map3 import *

running = True
while running:
    current_time = pygame.time.get_ticks()  # Get current time for debounce
    if game_state == GAME_STATE_LOADING:
        # Draw loading screen
        scene.blit(loading_background, (0, 0))  # Draw background image
        mouse_pos = pygame.mouse.get_pos()
        if start_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), start_button)  # Brighter blue for hover
        else:
            pygame.draw.rect(scene, button_color, start_button)  # Normal blue
        scene.blit(start_button_text, start_button_text_rect)  # Draw Start button text
        pygame.display.flip()  # Update display

        # Handle events in loading screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break  # Exit event loop immediately
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_time - last_click_time > CLICK_COOLDOWN:
                if start_button.collidepoint(event.pos):  # Check if Start button is clicked
                    game_state = GAME_STATE_PLAYING
                    last_click_time = current_time  # Update last click time
                    pygame.event.clear()  # Clear event queue to prevent duplicate clicks
            # Optional: Use Space key to start game
            # elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            #     game_state = GAME_STATE_PLAYING
            #     pygame.event.clear()  # Clear event queue

    elif game_state == GAME_STATE_PLAYING:
        # Process input events (such as closing the window or shooting projectiles)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break  # Exit event loop immediately
            elif event.type == pygame.KEYDOWN:
                if event.key == fighter1.controls.get("shoot"):
                    projectile = fighter1.shoot()
                    all_sprites.add(projectile)
                    projectiles.add(projectile)

        # Update all game objects (calls update() on each sprite in all_sprites)
        all_sprites.update()  # Call update for all sprites

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
                hit_platforms = pygame.sprite.spritecollide(sprite, platforms, False)
                for platform in hit_platforms:
                    sprite.kill()

        # Draw phase: clear the screen, draw background, and then all sprites
        draw_background()  # Use draw_background from map3.py
        all_sprites.draw(scene)
        for sprite in all_sprites:
            if isinstance(sprite, Player):  # NPC and Fighter
                sprite.draw_health_bar(scene)
        pygame.display.flip()  # Refresh the display
        clock.tick(config.FPS)  # Maintain the FPS defined in config

pygame.quit()  # Clean up and close the pygame window