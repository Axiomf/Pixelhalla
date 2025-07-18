import pygame
import config
from src.engine.fighter_select import fighter1_button, fighter2_button, fighter3_button, fighter4_button

class FighterSelectState:
    def __init__(self, scene):
        self.scene = scene
        self.back_button = pygame.Rect(20, 20, 100, 50)  # Top-left corner
        self.font = pygame.font.Font(None, 55)  # Use default font, size 36 for button text
        self.button_color = (0, 128, 255)  # Blue button
        self.loading_background = pygame.image.load("src/assets/images/background/blue-preview.png").convert_alpha()
        self.loading_background = pygame.transform.scale(self.loading_background, (config.SCENE_WIDTH, config.SCENE_HEIGHT))
        self.fighter1_preview = pygame.image.load("src/assets/images/inused_single_images/fighter.png").convert_alpha()
        self.fighter1_preview = pygame.transform.scale(self.fighter1_preview, (150, 150))
        self.fighter2_preview = pygame.image.load("src/assets/images/inused_single_images/fighter.png").convert_alpha()
        self.fighter2_preview = pygame.transform.scale(self.fighter2_preview, (150, 150))
        self.fighter3_preview = pygame.image.load("src/assets/images/inused_single_images/fighter.png").convert_alpha()
        self.fighter3_preview = pygame.transform.scale(self.fighter3_preview, (150, 150))
        self.fighter4_preview = pygame.image.load("src/assets/images/inused_single_images/fighter.png").convert_alpha()
        self.fighter4_preview = pygame.transform.scale(self.fighter4_preview, (150, 150))

    def handle_event(self, event, current_time, scale, state_manager):
        """Handle events in fighter select screen."""
        if not hasattr(state_manager, 'game_mode') or state_manager.game_mode is None:
            state_manager.change_state(config.GAME_STATE_MODE_SELECT)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_time - state_manager.last_click_time > config.CLICK_COOLDOWN:
            pulsed_fighter1_button = pygame.Rect(fighter1_button.x - scale / 2, fighter1_button.y - scale / 2, 
                                                fighter1_button.width + scale, fighter1_button.height + scale)
            pulsed_fighter2_button = pygame.Rect(fighter2_button.x - scale / 2, fighter2_button.y - scale / 2, 
                                                fighter2_button.width + scale, fighter2_button.height + scale)
            pulsed_fighter3_button = pygame.Rect(fighter3_button.x - scale / 2, fighter3_button.y - scale / 2, 
                                                fighter3_button.width + scale, fighter3_button.height + scale)
            pulsed_fighter4_button = pygame.Rect(fighter4_button.x - scale / 2, fighter4_button.y - scale / 2, 
                                                fighter4_button.width + scale, fighter4_button.height + scale)
            pulsed_back_button = pygame.Rect(self.back_button.x - scale / 2, self.back_button.y - scale / 2, 
                                            self.back_button.width + scale, self.back_button.height + scale)
            if pulsed_fighter1_button.collidepoint(event.pos):
                if state_manager.game_mode == "single" or state_manager.fighter_select_phase == 1:
                    state_manager.fighter1_id = "fighter1"
                elif state_manager.game_mode == "multi" and state_manager.fighter_select_phase == 2:
                    state_manager.fighter2_id = "fighter1"
                if state_manager.game_mode == "single":
                    state_manager.change_state(config.GAME_STATE_PLAYING)
                elif state_manager.game_mode == "multi" and state_manager.fighter_select_phase == 1:
                    state_manager.fighter_select_phase = 2
                elif state_manager.game_mode == "multi" and state_manager.fighter_select_phase == 2:
                    state_manager.change_state(config.GAME_STATE_PLAYING)
                state_manager.last_click_time = current_time
                pygame.event.clear()  # Clear event queue
            elif pulsed_fighter2_button.collidepoint(event.pos):
                if state_manager.game_mode == "single" or state_manager.fighter_select_phase == 1:
                    state_manager.fighter1_id = "fighter2"
                elif state_manager.game_mode == "multi" and state_manager.fighter_select_phase == 2:
                    state_manager.fighter2_id = "fighter2"
                if state_manager.game_mode == "single":
                    state_manager.change_state(config.GAME_STATE_PLAYING)
                elif state_manager.game_mode == "multi" and state_manager.fighter_select_phase == 1:
                    state_manager.fighter_select_phase = 2
                elif state_manager.game_mode == "multi" and state_manager.fighter_select_phase == 2:
                    state_manager.change_state(config.GAME_STATE_PLAYING)
                state_manager.last_click_time = current_time
                pygame.event.clear()  # Clear event queue
            elif pulsed_fighter3_button.collidepoint(event.pos):
                if state_manager.game_mode == "single" or state_manager.fighter_select_phase == 1:
                    state_manager.fighter1_id = "fighter3"
                elif state_manager.game_mode == "multi" and state_manager.fighter_select_phase == 2:
                    state_manager.fighter2_id = "fighter3"
                if state_manager.game_mode == "single":
                    state_manager.change_state(config.GAME_STATE_PLAYING)
                elif state_manager.game_mode == "multi" and state_manager.fighter_select_phase == 1:
                    state_manager.fighter_select_phase = 2
                elif state_manager.game_mode == "multi" and state_manager.fighter_select_phase == 2:
                    state_manager.change_state(config.GAME_STATE_PLAYING)
                state_manager.last_click_time = current_time
                pygame.event.clear()  # Clear event queue
            elif pulsed_fighter4_button.collidepoint(event.pos):
                if state_manager.game_mode == "single" or state_manager.fighter_select_phase == 1:
                    state_manager.fighter1_id = "fighter4"
                elif state_manager.game_mode == "multi" and state_manager.fighter_select_phase == 2:
                    state_manager.fighter2_id = "fighter4"
                if state_manager.game_mode == "single":
                    state_manager.change_state(config.GAME_STATE_PLAYING)
                elif state_manager.game_mode == "multi" and state_manager.fighter_select_phase == 1:
                    state_manager.fighter_select_phase = 2
                elif state_manager.game_mode == "multi" and state_manager.fighter_select_phase == 2:
                    state_manager.change_state(config.GAME_STATE_PLAYING)
                state_manager.last_click_time = current_time
                pygame.event.clear()  # Clear event queue
            elif pulsed_back_button.collidepoint(event.pos):  # Back to map select
                state_manager.change_state(config.GAME_STATE_MAP_SELECT)
                state_manager.fighter1_id = None
                state_manager.fighter2_id = None
                state_manager.fighter_select_phase = 1
                state_manager.last_click_time = current_time
                pygame.event.clear()  # Clear event queue

    def update(self, current_time, scale, state_manager):
        """Update logic for fighter select screen (if any)."""
        pass

    def draw(self, scene, scale, state_manager):
        """Draw fighter select screen."""
        mouse_pos = pygame.mouse.get_pos()
        scene.blit(self.loading_background, (0, 0))  # Same background
        pulsed_fighter1_button = pygame.Rect(fighter1_button.x - scale / 2, fighter1_button.y - scale / 2, 
                                            fighter1_button.width + scale, fighter1_button.height + scale)
        pulsed_fighter2_button = pygame.Rect(fighter2_button.x - scale / 2, fighter2_button.y - scale / 2, 
                                            fighter2_button.width + scale, fighter2_button.height + scale)
        pulsed_fighter3_button = pygame.Rect(fighter3_button.x - scale / 2, fighter3_button.y - scale / 2, 
                                            fighter3_button.width + scale, fighter3_button.height + scale)
        pulsed_fighter4_button = pygame.Rect(fighter4_button.x - scale / 2, fighter4_button.y - scale / 2, 
                                            fighter4_button.width + scale, fighter4_button.height + scale)
        if pulsed_fighter1_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), pulsed_fighter1_button, 5)  # Blue border for hover
        scene.blit(self.fighter1_preview, fighter1_button)
        if pulsed_fighter2_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), pulsed_fighter2_button, 5)  # Blue border for hover
        scene.blit(self.fighter2_preview, fighter2_button)
        if pulsed_fighter3_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), pulsed_fighter3_button, 5)  # Blue border for hover
        scene.blit(self.fighter3_preview, fighter3_button)
        if pulsed_fighter4_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), pulsed_fighter4_button, 5)  # Blue border for hover
        scene.blit(self.fighter4_preview, fighter4_button)

        # Draw phase indicator for multi mode
        if state_manager.game_mode == "multi":
            phase_text = self.font.render(f"Select Fighter {state_manager.fighter_select_phase}", True, (255, 255, 255))
            phase_text_rect = phase_text.get_rect(center=(config.SCENE_WIDTH // 2, 50))
            scene.blit(phase_text, phase_text_rect)

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