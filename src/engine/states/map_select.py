import pygame
import config
from src.engine.map_select import map1_button, map2_button, map3_button, map4_button

class MapSelectState:
    def __init__(self, scene):
        self.scene = scene
        self.back_button = pygame.Rect(20, 20, 100, 50)  # Top-left corner
        self.font = pygame.font.Font(None, 55)  # Use default font, size 36 for button text
        self.button_color = (0, 128, 255)  # Blue button
        self.loading_background = pygame.image.load("src/assets/images/background/blue-preview.png").convert_alpha()
        self.loading_background = pygame.transform.scale(self.loading_background, (config.SCENE_WIDTH, config.SCENE_HEIGHT))
        self.map1_preview = pygame.image.load("src/assets/images/background/map-ShorwindFishingPort.png").convert_alpha()
        self.map1_preview = pygame.transform.scale(self.map1_preview, (300, 150))
        self.map2_preview = pygame.image.load("src/assets/images/nature_3/origbig.png").convert_alpha()
        self.map2_preview = pygame.transform.scale(self.map2_preview, (300, 150))
        self.map3_preview = pygame.image.load("src/assets/images/background/jesus/j1.jpg").convert_alpha()
        self.map3_preview = pygame.transform.scale(self.map3_preview, (300, 150))
        self.map4_preview = pygame.image.load("src/assets/images/nature_1/orig.png").convert_alpha()
        self.map4_preview = pygame.transform.scale(self.map4_preview, (300, 150))

    def handle_event(self, event, current_time, scale, state_manager):
        """Handle events in map select screen."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_time - state_manager.last_click_time > config.CLICK_COOLDOWN:
            pulsed_map1_button = pygame.Rect(map1_button.x - scale / 2, map1_button.y - scale / 2, 
                                            map1_button.width + scale, map1_button.height + scale)
            pulsed_map2_button = pygame.Rect(map2_button.x - scale / 2, map2_button.y - scale / 2, 
                                            map2_button.width + scale, map2_button.height + scale)
            pulsed_map3_button = pygame.Rect(map3_button.x - scale / 2, map3_button.y - scale / 2, 
                                            map3_button.width + scale, map3_button.height + scale)
            pulsed_map4_button = pygame.Rect(map4_button.x - scale / 2, map4_button.y - scale / 2, 
                                            map4_button.width + scale, map4_button.height + scale)
            pulsed_back_button = pygame.Rect(self.back_button.x - scale / 2, self.back_button.y - scale / 2, 
                                            self.back_button.width + scale, self.back_button.height + scale)
            if pulsed_map1_button.collidepoint(event.pos):
                state_manager.click_sound.play()  # Play click sound
                state_manager.current_map = "map1"
                state_manager.change_state(config.GAME_STATE_FIGHTER_SELECT)
                state_manager.last_click_time = current_time
                pygame.event.clear()  # Clear event queue
            elif pulsed_map2_button.collidepoint(event.pos):
                state_manager.click_sound.play()  # Play click sound
                state_manager.current_map = "map_levels"
                state_manager.change_state(config.GAME_STATE_FIGHTER_SELECT)
                state_manager.last_click_time = current_time
                pygame.event.clear()  # Clear event queue
            elif pulsed_map3_button.collidepoint(event.pos):
                state_manager.click_sound.play()  # Play click sound
                state_manager.current_map = "map_jesus"
                state_manager.change_state(config.GAME_STATE_FIGHTER_SELECT)
                state_manager.last_click_time = current_time
                pygame.event.clear()  # Clear event queue
            elif pulsed_map4_button.collidepoint(event.pos):
                state_manager.click_sound.play()  # Play click sound
                state_manager.current_map = "map4"
                state_manager.change_state(config.GAME_STATE_FIGHTER_SELECT)
                state_manager.last_click_time = current_time
                pygame.event.clear()  # Clear event queue
            elif pulsed_back_button.collidepoint(event.pos):  # Back to mode select
                state_manager.click_sound.play()  # Play click sound
                state_manager.change_state(config.GAME_STATE_MODE_SELECT)
                state_manager.last_click_time = current_time
                pygame.event.clear()  # Clear event queue

    def update(self, current_time, scale, state_manager):
        """Update logic for map select screen (if any)."""
        pass

    def draw(self, scene, scale, state_manager):
        """Draw map select screen."""
        mouse_pos = pygame.mouse.get_pos()
        scene.blit(self.loading_background, (0, 0))  # Same background
        pulsed_map1_button = pygame.Rect(map1_button.x - scale / 2, map1_button.y - scale / 2, 
                                        map1_button.width + scale, map1_button.height + scale)
        pulsed_map2_button = pygame.Rect(map2_button.x - scale / 2, map2_button.y - scale / 2, 
                                        map2_button.width + scale, map2_button.height + scale)
        pulsed_map3_button = pygame.Rect(map3_button.x - scale / 2, map3_button.y - scale / 2, 
                                        map3_button.width + scale, map3_button.height + scale)
        pulsed_map4_button = pygame.Rect(map4_button.x - scale / 2, map4_button.y - scale / 2, 
                                        map4_button.width + scale, map4_button.height + scale)
        if pulsed_map1_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), pulsed_map1_button, 5)  # Blue border for hover
        scene.blit(self.map1_preview, map1_button)
        if pulsed_map2_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), pulsed_map2_button, 5)  # Blue border for hover
        scene.blit(self.map2_preview, map2_button)
        if pulsed_map3_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), pulsed_map3_button, 5)  # Blue border for hover
        scene.blit(self.map3_preview, map3_button)
        if pulsed_map4_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), pulsed_map4_button, 5)  # Blue border for hover
        scene.blit(self.map4_preview, map4_button)

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