import pygame
pygame.font.init()  # Initialize the font module

# Front-related UI setup added from chatgpt.py
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boss vs. Fighter Dialog")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
BLUE = (0, 100, 200)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

# Fonts
font_dialog = pygame.font.Font(None, 24) # For dialog history
font_input = pygame.font.Font(None, 28)  # For user input
font_status = pygame.font.Font(None, 20)   # For status messages

def draw_text_multiline(surface, text, font, color, rect, line_height_factor=1.2):
    words = text.split(' ')
    lines = []
    current_line = []
    current_line_width = 0
    space_width = font.size(' ')[0]
    for word in words:
        word_surface = font.render(word, True, color)
        word_width = word_surface.get_width()
        if current_line_width + word_width + space_width < rect.width:
            current_line.append(word)
            current_line_width += word_width + space_width
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_line_width = word_width + space_width
    if current_line:
        lines.append(" ".join(current_line))
    y_offset = rect.top
    for line in lines:
        text_surface = font.render(line, True, color)
        if y_offset + text_surface.get_height() * line_height_factor > rect.bottom:
            break
        surface.blit(text_surface, (rect.left, y_offset))
        y_offset += font.get_height() * line_height_factor
    return y_offset

def draw_ui(dialog_history, user_input_text, is_waiting_for_llm, dialog_display_scroll_offset):
    # Draw the complete front UI
    screen.fill(BLACK)
    # Dialog history area
    dialog_rect = pygame.Rect(50, 20, WIDTH - 100, HEIGHT - 150)
    pygame.draw.rect(screen, GRAY, dialog_rect, 0, 8)
    pygame.draw.rect(screen, LIGHT_GRAY, dialog_rect, 2, 8)
    display_messages = [msg for msg in dialog_history if msg["role"] != "system"]
    current_y = dialog_rect.top + 10
    for msg in display_messages:
        prefix = "Fighter: " if msg["role"] == "user" else "Boss: "
        display_text = prefix + msg["content"].split("(Current game context:")[0].strip()
        message_rect = pygame.Rect(dialog_rect.left + 10, current_y, dialog_rect.width - 20, 100)
        current_y = draw_text_multiline(screen, display_text, font_dialog, WHITE, message_rect) + 5
    # Input box area
    input_box_rect = pygame.Rect(50, HEIGHT - 100, WIDTH - 100, 50)
    pygame.draw.rect(screen, LIGHT_GRAY, input_box_rect, 0, 5)
    pygame.draw.rect(screen, WHITE, input_box_rect, 2, 5)
    input_surface = font_input.render(user_input_text, True, BLACK)
    screen.blit(input_surface, (input_box_rect.left + 10, input_box_rect.centery - input_surface.get_height() // 2))
    # Status area
    status_rect = pygame.Rect(50, HEIGHT - 40, WIDTH - 100, 30)
    if is_waiting_for_llm:
        status_text = "Boss is contemplating your fate..."
        status_color = BLUE
    elif not user_input_text.strip():
        status_text = "Type your message..."
        status_color = LIGHT_GRAY
    else:
        status_text = "Type your defiance and press ENTER (or ESC to quit)."
        status_color = GREEN
    status_surface = font_status.render(status_text, True, status_color)
    screen.blit(status_surface, (status_rect.left, status_rect.top))
    pygame.display.flip()

