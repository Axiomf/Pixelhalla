import pygame
import config
from src.engine.mode_select import single_button, two_button

class ModeSelectState:
    def __init__(self, scene):
        self.scene = scene
        self.back_button = pygame.Rect(20, 20, 100, 50)  # Top-left corner
        self.font = pygame.font.Font(None, 60)  # Use default font, size 65 for button text
        self.button_color = (0, 128, 255)  # Blue button
        self.loading_background = pygame.image.load("src/assets/images/blue-preview.png").convert_alpha()
        self.loading_background = pygame.transform.scale(self.loading_background, (config.SCENE_WIDTH, config.SCENE_HEIGHT))
    def handle_event(self, event, current_time, scale, state_manager):
        """Handle events in mode select screen."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_time - state_manager.last_click_time > config.CLICK_COOLDOWN:
            pulsed_single_button = pygame.Rect(single_button.x - scale / 2, single_button.y - scale / 2, 
                                              single_button.width + scale, single_button.height + scale)
            pulsed_two_button = pygame.Rect(two_button.x - scale / 2, two_button.y - scale / 2, 
                                           two_button.width + scale, two_button.height + scale)
            pulsed_back_button = pygame.Rect(self.back_button.x - scale / 2, self.back_button.y - scale / 2, 
                                            self.back_button.width + scale, self.back_button.height + scale)
            if pulsed_single_button.collidepoint(event.pos):
                state_manager.game_mode = "single"
                state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                state_manager.last_click_time = current_time
                pygame.event.clear()  # Clear event queue
            elif pulsed_two_button.collidepoint(event.pos):
                state_manager.game_mode = "multi"
                state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                state_manager.last_click_time = current_time
                pygame.event.clear()  # Clear event queue
            elif pulsed_back_button.collidepoint(event.pos):  # Back to loading screen
                state_manager.change_state(config.GAME_STATE_LOADING)
                state_manager.last_click_time = current_time
                pygame.event.clear()  # Clear event queue

    def update(self, current_time, scale, state_manager):
        """Update logic for mode select screen (if any)."""
        pass

    def draw(self, scene, scale, state_manager):
        """Draw mode select screen."""
        mouse_pos = pygame.mouse.get_pos()
        scene.blit(self.loading_background, (0, 0))  # Same background
        pulsed_single_button = pygame.Rect(single_button.x - scale / 2, single_button.y - scale / 2, 
                                          single_button.width + scale, single_button.height + scale)
        pulsed_two_button = pygame.Rect(two_button.x - scale / 2, two_button.y - scale / 2, 
                                       two_button.width + scale, two_button.height + scale)
        if pulsed_single_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), pulsed_single_button)  # Brighter blue for hover
        else:
            pygame.draw.rect(scene, self.button_color, pulsed_single_button)  # Normal blue
        if pulsed_two_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), pulsed_two_button)  # Brighter blue for hover
        else:
            pygame.draw.rect(scene, self.button_color, pulsed_two_button)  # Normal blue
        single_button_text = self.font.render("Single Player", True, (255, 255, 255))  # Render text here
        two_button_text = self.font.render("Multiplayer", True, (255, 255, 255))  # Render text here
        pulsed_single_button_text_rect = single_button_text.get_rect(center=pulsed_single_button.center)
        pulsed_two_button_text_rect = two_button_text.get_rect(center=pulsed_two_button.center)
        scene.blit(single_button_text, pulsed_single_button_text_rect)  # Draw Single Player text
        scene.blit(two_button_text, pulsed_two_button_text_rect)  # Draw Two Players text

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