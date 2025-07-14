import pygame  # Import pygame for game functionality
import config  # Import configuration settings like scene dimensions and FPS
import math    # Import math for sin function in pulse effect

# Initialize pygame
pygame.init()  # Initialize all imported pygame modules
pygame.display.set_caption(config.CAPTION)  # Set the window title
scene = pygame.display.set_mode((config.SCENE_WIDTH, config.SCENE_HEIGHT))  # Set up the main game window
clock = pygame.time.Clock()  # Create a clock to manage the game's frame rate

from src.engine.loading_page import *
from src.engine.mode_select import *
# Import from maps after loading screen setup to avoid resetting game_state
from src.engine.map3 import *

last_click_time = 0

running = True
while running:
    current_time = pygame.time.get_ticks()  # Get current time for debounce
    config.PULSE_TIME += config.PULSE_SPEED  # Update pulse animation
    scale = config.PULSE_SCALE * abs(math.sin(config.PULSE_TIME))  # Calculate scale for pulse

    if game_state == GAME_STATE_LOADING:
        # Draw loading screen
        scene.blit(loading_background, (0, 0))  # Draw background image
        pulsed_start_button = pygame.Rect(start_button.x - scale / 2, start_button.y - scale / 2, 
                                          start_button.width + scale, start_button.height + scale)
        mouse_pos = pygame.mouse.get_pos()
        if pulsed_start_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), pulsed_start_button)  # Brighter blue for hover
        else:
            pygame.draw.rect(scene, button_color, pulsed_start_button)  # Normal blue
        pulsed_start_button_text_rect = start_button_text.get_rect(center=pulsed_start_button.center)
        scene.blit(start_button_text, pulsed_start_button_text_rect)  # Draw Start button text
        pygame.display.flip()  # Update display

        # Handle events in loading screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_time - last_click_time > config.CLICK_COOLDOWN:
                if pulsed_start_button.collidepoint(event.pos):  # Check if Start button is clicked
                    game_state = GAME_STATE_MODE_SELECT
                    last_click_time = current_time
                    pygame.event.clear()  # Clear event queue

    elif game_state == GAME_STATE_MODE_SELECT:
        # Draw mode select screen
        scene.blit(loading_background, (0, 0))  # Same background
        pulsed_single_button = pygame.Rect(single_button.x - scale / 2, single_button.y - scale / 2, 
                                           single_button.width + scale, single_button.height + scale)
        pulsed_two_button = pygame.Rect(two_button.x - scale / 2, two_button.y - scale / 2, 
                                        two_button.width + scale, two_button.height + scale)
        mouse_pos = pygame.mouse.get_pos()
        if pulsed_single_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), pulsed_single_button)  # Brighter blue for hover
        else:
            pygame.draw.rect(scene, button_color, pulsed_single_button)  # Normal blue
        if pulsed_two_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), pulsed_two_button)  # Brighter blue for hover
        else:
            pygame.draw.rect(scene, button_color, pulsed_two_button)  # Normal blue
        pulsed_single_button_text_rect = single_button_text.get_rect(center=pulsed_single_button.center)
        pulsed_two_button_text_rect = two_button_text.get_rect(center=pulsed_two_button.center)
        scene.blit(single_button_text, pulsed_single_button_text_rect)  # Draw Single Player text
        scene.blit(two_button_text, pulsed_two_button_text_rect)  # Draw Two Players text
        pygame.display.flip()  # Update display

        # Handle events in mode select screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_time - last_click_time > config.CLICK_COOLDOWN:
                if pulsed_single_button.collidepoint(event.pos):
                    game_mode = "single"
                    game_state = GAME_STATE_PLAYING
                    last_click_time = current_time
                    pygame.event.clear()  # Clear event queue
                elif pulsed_two_button.collidepoint(event.pos):
                    game_mode = "multi"
                    game_state = GAME_STATE_PLAYING
                    last_click_time = current_time
                    pygame.event.clear()  # Clear event queue

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