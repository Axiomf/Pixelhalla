import pygame
import config
from src.engine.states.base_state import BaseState
from src.engine import map1, map4, map_boss, map_jesus, map_levels
from src.engine.mode_select import single_button, two_button

class MultiplayerState(BaseState):
    def __init__(self, scene):
        super().__init__(scene)
        self.scene = scene
        self.back_button = pygame.Rect(20, 20, 100, 50)  # Top-left corner
        self.font = pygame.font.Font(None, 60)  # Font for buttons
        self.input_font = pygame.font.Font(None, 40)  # Smaller font for input box
        self.button_color = (0, 128, 255)  # Blue button
        self.loading_background = pygame.image.load("src/assets/images/background/blue-preview.png").convert_alpha()
        self.loading_background = pygame.transform.scale(self.loading_background, (config.SCENE_WIDTH, config.SCENE_HEIGHT))
        # Input box for username
        self.input_box = pygame.Rect(config.SCENE_WIDTH // 2 - 150, config.SCENE_HEIGHT // 2 - 100, 300, 50)
        self.username = ""  # Store the username
        self.input_active = True  # Whether the input box is active
        self.error_message = ""  # Error message if username is empty
        self.error_message_time = 0  # Time when error message was set
        self.error_message_duration = 3000  # 3 seconds in milliseconds

    def handle_event(self, event, current_time, scale,current_map, state_manager):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_time - state_manager.last_click_time > config.CLICK_COOLDOWN:
            # Check if clicking the input box
            if self.input_box.collidepoint(event.pos):
                self.input_active = True
            else:
                self.input_active = False
            # Handle buttons only if username is entered
            if self.username:
                pulsed_1v1_button = pygame.Rect(single_button.x - scale / 2, single_button.y - scale / 2, 
                                               single_button.width + scale, single_button.height + scale)
                pulsed_2v2_button = pygame.Rect(two_button.x - scale / 2, two_button.y - scale / 2, 
                                               two_button.width + scale, two_button.height + scale)
                pulsed_back_button = pygame.Rect(self.back_button.x - scale / 2, self.back_button.y - scale / 2, 
                                                self.back_button.width + scale, self.back_button.height + scale)
                if pulsed_1v1_button.collidepoint(event.pos):
                    state_manager.click_sound.play()  # Play click sound
                    state_manager.multi_mode = "1v1"
                    state_manager.username = self.username  # Store username in state_manager
                    state_manager.last_click_time = current_time
                    pygame.event.clear()  # Clear event queue
                elif pulsed_2v2_button.collidepoint(event.pos):
                    state_manager.click_sound.play()  # Play click sound
                    state_manager.multi_mode = "2v2"
                    state_manager.username = self.username  # Store username in state_manager
                    state_manager.last_click_time = current_time
                    pygame.event.clear()  # Clear event queue
                elif pulsed_back_button.collidepoint(event.pos):
                    state_manager.click_sound.play()  # Play click sound
                    state_manager.change_state(config.GAME_STATE_MODE_SELECT)
                    state_manager.last_click_time = current_time
                    pygame.event.clear()  # Clear event queue
            else:
                self.error_message = "Please enter your username"
                self.error_message_time = current_time  # Store the time when error message is set

        # Handle keyboard input for username
        if self.input_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.username:
                    self.input_active = False  # Deactivate input box after entering username
                    self.error_message = ""  # Clear error message
                else:
                    self.error_message = "Please enter your username"
                    self.error_message_time = current_time  # Store the time when error message is set
            elif event.key == pygame.K_BACKSPACE:
                self.username = self.username[:-1]
            else:
                # Only add printable characters
                if event.unicode.isprintable() and len(self.username) < 15:  # Limit username length
                    self.username += event.unicode

    def update(self, current_time, scale, state_manager):
        # Clear error message after 3 seconds
        if self.error_message and current_time - self.error_message_time > self.error_message_duration:
            self.error_message = ""

    def draw(self, scene, scale, state_manager):
        mouse_pos = pygame.mouse.get_pos()
        scene.blit(self.loading_background, (0, 0))  # Draw background

        # Draw input box
        input_color = (0, 200, 255) if self.input_active else (100, 100, 100)  # Brighter when active
        pygame.draw.rect(scene, input_color, self.input_box, 2)  # Draw input box border
        input_text = self.input_font.render(self.username if self.username else "Enter your Username", True, (255, 255, 255))
        text_rect = input_text.get_rect(center=self.input_box.center)
        scene.blit(input_text, text_rect)

        # Draw error message if any
        if self.error_message:
            error_text = self.input_font.render(self.error_message, True, (255, 0, 0))
            error_rect = error_text.get_rect(center=(config.SCENE_WIDTH // 2, self.input_box.bottom - 70))
            scene.blit(error_text, error_rect)

        # Draw buttons (enabled only if username is entered)
        pulsed_1v1_button = pygame.Rect(single_button.x - scale / 2, single_button.y - scale / 2, 
                                        single_button.width + scale, single_button.height + scale)
        pulsed_2v2_button = pygame.Rect(two_button.x - scale / 2, two_button.y - scale / 2, 
                                       two_button.width + scale, two_button.height + scale)
        if self.username:  # Buttons active only if username is entered
            if pulsed_1v1_button.collidepoint(mouse_pos):
                pygame.draw.rect(scene, (0, 200, 255), pulsed_1v1_button)  # Brighter blue for hover
            else:
                pygame.draw.rect(scene, self.button_color, pulsed_1v1_button)  # Normal blue
            if pulsed_2v2_button.collidepoint(mouse_pos):
                pygame.draw.rect(scene, (0, 200, 255), pulsed_2v2_button)  # Brighter blue for hover
            else:
                pygame.draw.rect(scene, self.button_color, pulsed_2v2_button)  # Normal blue
        else:
            # Draw disabled buttons
            pygame.draw.rect(scene, (100, 100, 100), pulsed_1v1_button)  # Gray for disabled
            pygame.draw.rect(scene, (100, 100, 100), pulsed_2v2_button)  # Gray for disabled

        single_button_text = self.font.render("1v1", True, (255, 255, 255))
        two_button_text = self.font.render("2v2", True, (255, 255, 255))
        pulsed_single_button_text_rect = single_button_text.get_rect(center=pulsed_1v1_button.center)
        pulsed_two_button_text_rect = two_button_text.get_rect(center=pulsed_2v2_button.center)
        scene.blit(single_button_text, pulsed_single_button_text_rect)
        scene.blit(two_button_text, pulsed_two_button_text_rect)

        # Draw Back button
        pulsed_back_button = pygame.Rect(self.back_button.x - scale / 2, self.back_button.y - scale / 2, 
                                        self.back_button.width + scale, self.back_button.height + scale)
        if pulsed_back_button.collidepoint(mouse_pos):
            pygame.draw.rect(scene, (0, 200, 255), pulsed_back_button)  # Brighter blue for hover
        else:
            pygame.draw.rect(scene, self.button_color, pulsed_back_button)  # Normal blue
        back_button_text = self.font.render("Back", True, (255, 255, 255))
        pulsed_back_button_text_rect = back_button_text.get_rect(center=pulsed_back_button.center)
        scene.blit(back_button_text, pulsed_back_button_text_rect)