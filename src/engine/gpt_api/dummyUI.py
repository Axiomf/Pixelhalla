import pygame
import src.engine.gpt_api.API as gpt_api


def draw_text_multiline(surface, text, font, color, rect, line_height_factor=1.2):
    words = text.split(' ')
    lines = []
    current_line = []
    current_line_width = 0

    space_width = font.size(' ')[0]
    for word in words:
        word_surface = font.render(word, True, color)
        word_width = word_surface.get_width()
        if current_line_width + word_width + (space_width if current_line else 0) < rect.width:
            current_line.append(word)
            current_line_width += word_width + (space_width if current_line else 0)
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


DIALOG_BOX_WIDTH = 300
DIALOG_BOX_HEIGHT = 100
FIGHTER_DIALOG_BOX_X = 10
FIGHTER_DIALOG_BOX_Y = 10
BOSS_DIALOG_BOX_X = 900
BOSS_DIALOG_BOX_Y = 340

def display_texts(surface):
    font = pygame.font.Font(None, 24)
    fighter_color = (0, 255, 0)
    boss_color = (255, 0, 0)

    boss_box = pygame.Rect(BOSS_DIALOG_BOX_X, BOSS_DIALOG_BOX_Y, DIALOG_BOX_WIDTH, DIALOG_BOX_HEIGHT)
    pygame.draw.rect(surface, (0, 0, 0), boss_box)  
    draw_text_multiline(surface, "Lucifer: " + gpt_api.BOSS_LAST_dialogue, font, boss_color, boss_box)

    fighter_box = pygame.Rect(FIGHTER_DIALOG_BOX_X, FIGHTER_DIALOG_BOX_Y, DIALOG_BOX_WIDTH, DIALOG_BOX_HEIGHT)
    pygame.draw.rect(surface, (0, 0, 0), fighter_box) 
    draw_text_multiline(surface, "Fighter: " + gpt_api.FIGHTER_LAST_dialog, font, fighter_color, fighter_box)