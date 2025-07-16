import pygame
import config
from src.engine.loading_page import start_button

class LoadingState:
    def __init__(self, scene):
        self.scene = scene
        self.back_button = pygame.Rect(20, 20, 100, 50)  # Top-left corner
        self.font = pygame.font.Font(None, 74)  # Use default font, size 74 for button text
        self.button_color = (0, 128, 255)  # Blue button for Start
        self.loading_background = pygame.image.load("src/assets/images/blue-preview.png").convert_alpha()
        self.loading_background = pygame.transform.scale(self.loading_background, (config.SCENE_WIDTH, config.SCENE_HEIGHT))

    def handle_event(self, event, current_time, scale, state_manager):
        """Handle events in loading screen."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_time - state_manager.last_click_time > config.CLICK_COOLDOWN:
            pulsed_start_button = pygame.Rect(start_button.x - scale / 2, start_button.y - scale / 2, 
                                             start_button.width + scale, start_button.height + scale)
            pulsed_back_button = pygame.Rect(self.back_button.x - scale / 2, self.back_button.y - scale / 2, 
                                            self.back_button.width + scale, self.back_button.height + scale)
            if pulsed_start_button.collidepoint(event.pos):
                state_manager.change_state(config.GAME_STATE_MODE_SELECT)
                state_manager.last_click_time = current_time
                pygame.event.clear()  # Clear event queue
            elif pulsed_back_button.collidepoint(event.pos):  # Back button quits the game
                pygame.quit()
                exit()

    def update(self, current_time, scale, state_manager):
        """Update logic for loading screen (if any)."""
        pass

    def draw(self, scene, scale, state_manager):
        """Draw loading screen."""
        mouse_pos = pygame.mouse.get_pos()
        scene.blit(self.loading_background, (0, 0))  # Draw background image
        pulsed_start_button = pygame.Rect(start_button.x - scale / 2, start_button.y - scale / 2, 
                                         start_button.width + scale, start_button.height + scale)
        if pulsed_start_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), pulsed_start_button)  # Brighter blue for hover
        else:
            pygame.draw.rect(scene, self.button_color, pulsed_start_button)  # Normal blue
        start_button_text = self.font.render("Start", True, (255, 255, 255))  # Render text here
        pulsed_start_button_text_rect = start_button_text.get_rect(center=pulsed_start_button.center)
        scene.blit(start_button_text, pulsed_start_button_text_rect)  # Draw Start button text

        # Draw Back button
        pulsed_back_button = pygame.Rect(self.back_button.x - scale / 2, self.back_button.y - scale / 2, 
                                        self.back_button.width + scale, self.back_button.height + scale)
        if pulsed_back_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), pulsed_back_button)  # Brighter blue for hover
        else:
            pygame.draw.rect(scene, self.button_color, pulsed_back_button)  # Normal blue
        back_button_text = self.font.render("Back", True, (255, 255, 255))  # Render text here
        pulsed_back_button_text_rect = back_button_text.get_rect(center=pulsed_back_button.center)
        scene.blit(back_button_text, pulsed_back_button_text_rect)  # Draw Back button text