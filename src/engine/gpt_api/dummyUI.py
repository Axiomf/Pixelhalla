import pygame
import src.engine.gpt_api.API as gpt_api

def display_texts(surface):
    font = pygame.font.Font(None, 24)
    boss_text = font.render("Boss: " + gpt_api.BOSS_LAST_dialogue, True, (255, 255, 255))
    fighter_text = font.render("Fighter: " + gpt_api.FIGHTER_LAST_dialog, True, (255, 255, 255))
    surface.blit(boss_text, (10, 10))
    surface.blit(fighter_text, (10, 40))

