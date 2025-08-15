import pygame
import time

def get_full_rect(rect):
    # Ensure rect is (x, y, width, height), default width and height = 32 if missing
    return rect if len(rect) == 4 else (rect[0], rect[1], 64, 64)

def interpolate_rect(prev_rect, curr_rect, alpha):
    # Ensure both rects are (x, y, width, height)
    prev_rect = get_full_rect(prev_rect)
    curr_rect = get_full_rect(curr_rect)
    # Interpolate each component (x, y, w, h) between previous and current rects
    return tuple(int(prev_rect[i] + alpha * (curr_rect[i] - prev_rect[i])) for i in range(4))

def draw_health_bar(screen, rect, health, max_health, username):
    bar_width = rect[2]
    bar_height = 10
    bar_x = rect[0]
    bar_y = rect[1] - bar_height - 5
    health_ratio = health / max_health
    health_width = bar_width * health_ratio
    pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, health_width, bar_height))
    # Draw username above health bar
    font = pygame.font.SysFont('arial', 20)
    username_text = font.render(username, True, (255, 255, 255))
    username_rect = username_text.get_rect(center=(bar_x + bar_width // 2, bar_y - 20))
    padding = 5
    username_bg = pygame.Surface((username_rect.width + 2 * padding, username_rect.height + 2 * padding), pygame.SRCALPHA)
    username_bg.fill((0, 0, 0, 100))
    screen.blit(username_bg, (username_rect.x - padding, username_rect.y - padding))
    screen.blit(username_text, username_rect)

def static_render(screen, rect, obj, sprite_type, images):
    image = images.get(sprite_type)
    if image:
        if sprite_type == "projectiles":
            w = 10
            h = 10
        scaled_image = pygame.transform.scale(image, (w, h))
        screen.blit(scaled_image, (rect[0], rect[1]))
    else:
        pygame.draw.rect(screen, (255, 255, 255), rect)

def dynamic_render(screen, rect, obj, fighter_animations, client_anim_states, images):
    facing_right = obj.get("facing_right", True)
    anim = fighter_animations.get(obj.get("state"), None)
    if anim:
        state = client_anim_states.get(
            obj["id"],
            {"current_animation": obj.get("state"), "current_frame": 0, "last_update": time.time()}
        )
        if state["current_animation"] != obj.get("state"):
            state = {"current_animation": obj.get("state"), "current_frame": 0, "last_update": time.time()}
        now = time.time()
        if now - state["last_update"] > 0.1:
            state["current_frame"] = (state["current_frame"] + 1) % len(anim)
            state["last_update"] = now
        client_anim_states[obj["id"]] = state
        image = anim[state["current_frame"]]
        if not facing_right:
            image = pygame.transform.flip(image, True, False)
        scaled_image = pygame.transform.scale(image, (rect[2], rect[3]))
        screen.blit(scaled_image, (rect[0], rect[1]))
        health = obj.get("health",100)
        max_health = obj.get("max_health", 100)
        username = obj.get("username", "Unknown")
        draw_health_bar(screen, rect, health, max_health, username)
    else:
        image = images.get("fighter")
        if image:
            if not facing_right:
                image = pygame.transform.flip(image, True, False)
            scaled_image = pygame.transform.scale(image, (rect[2], rect[3]))
            screen.blit(scaled_image, (rect[0], rect[1]))
        else:
            pygame.draw.rect(screen, (255, 255, 255), rect)

def render_obj(screen, rect, obj, sprite_type, fighter_animations, client_anim_states, images):
    rect = get_full_rect(rect)
    if sprite_type == "fighters":
        dynamic_render(screen, rect, obj, fighter_animations, client_anim_states, images)
    else:
        static_render(screen, rect, obj, sprite_type, images)

def draw_waiting_screen(screen):
    waiting_background = pygame.image.load("src/assets/images/background/blue-preview.png").convert_alpha()
    waiting_background = pygame.transform.scale(waiting_background, (1200, 600))
    screen.blit(waiting_background, (0, 0))
    font = pygame.font.SysFont('arial', 50)
    text = font.render("Waiting for game to start...", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()

def draw_menu_screen(screen, mouse_pos=None):
    screen.fill((20, 20, 80))
    font = pygame.font.SysFont('arial', 40)
    title_font = pygame.font.SysFont('arial', 60)
    title = title_font.render("Pixelhalla", True, (255, 255, 255))
    
    options = [
        "1: Find Random Game",
        "2: Create Lobby",
        "3: Join Lobby",
    ]
    
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))
    
    # Store rectangles for each option to detect clicks
    option_rects = []
    for i, option in enumerate(options):
        text = font.render(option, True, (255, 255, 255) if not mouse_pos or not pygame.Rect(
            screen.get_width() // 2 - 200, 250 + i * 60, 400, 50
        ).collidepoint(mouse_pos) else (255, 255, 0))  # Highlight on hover
        text_rect = text.get_rect(center=(screen.get_width() // 2, 250 + i * 60 + 25))
        screen.blit(text, text_rect)
        # Create a larger clickable area around the text
        clickable_rect = pygame.Rect(screen.get_width() // 2 - 200, 250 + i * 60, 400, 50)
        option_rects.append(clickable_rect)
        
    pygame.display.flip()
    return option_rects  # Return the list of rectangles for click detection

def draw_lobby_screen(screen, lobby_id=None):
    screen.fill((20, 80, 20))
    font = pygame.font.SysFont('arial', 40)
    title_font = pygame.font.SysFont('arial', 60)
    title = title_font.render("Lobby", True, (255, 255, 255))
    
    options = [
        f"Waiting for players... Lobby ID: {lobby_id if lobby_id else 'Unknown'}",
        "4: Start Game (as Host)",
        "5: Destroy Lobby (as Host)",
    ]
    
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))
    
    for i, option in enumerate(options):
        text = font.render(option, True, (255, 255, 255))
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 250 + i * 60))
        
    pygame.display.flip()

def draw_game_state(screen, shared_lock, game_state, previous_game_state, last_update_time, network_interval, fighter_animations, client_anim_states, images):
    # Clear the screen to black before drawing anything
    screen.fill((0, 0, 0))
    now = time.time()
    # Safely copy the shared game state for this frame
    with shared_lock:
        current_state = game_state
        prev_state = previous_game_state
        last_time = last_update_time

    # If we have a current game state, proceed to draw it
    if current_state:
        alpha = 1.0  # Default: no interpolation
        # If we have a previous state and timestamp, calculate interpolation alpha
        if prev_state and last_time:
            alpha = min(1, (now - last_time) / network_interval)
        # Draw each group of objects (platforms, fighters, projectiles, power_ups)
        for key in ['platforms', 'fighters', 'projectiles', 'power_ups']:
            current_group = current_state.get(key, [])
            # If previous state exists and group lengths match, interpolate positions
            if prev_state and len(prev_state.get(key, [])) == len(current_group):
                prev_group = prev_state.get(key, [])
                for idx, obj in enumerate(current_group):
                    curr_rect = obj.get("rect")
                    prev_rect = prev_group[idx].get("rect")
                    # Interpolate rect if both current and previous rects exist
                    if curr_rect and prev_rect:
                        interp_rect = interpolate_rect(prev_rect, curr_rect, alpha)
                    else:
                        interp_rect = curr_rect
                        
                    render_obj(screen, interp_rect, obj, key, fighter_animations, client_anim_states, images)
            else:
                # If no previous state or group size mismatch, just draw current positions
                for obj in current_group:
                    rect = obj.get("rect")
                    if rect:
                        render_obj(screen, rect, obj, key, fighter_animations, client_anim_states, images)
        
            
    # Update the display with everything drawn this frame
    pygame.display.flip()
    with shared_lock:
        # handle sound
        path = "src/assets/sounds/blood2.wav"
        for _ in current_state.get("sounds", []):
                sound = pygame.mixer.Sound(path)
                sound.play()

def draw_game_over(screen, winning_team, losing_team):
    game_over = pygame.image.load("src/assets/images/inused_single_images/game_over.jpg").convert_alpha()
    game_over = pygame.transform.scale(game_over, (1200, 600))
    screen.blit(game_over, (0, 0))
    font = pygame.font.SysFont('arial', 50)
    
    # Render text
    win_text = font.render(f"Team {winning_team} Won!", True, (0, 0, 0))
    lose_text = font.render(f"Team {losing_team} Lost!", True, (0, 0, 0))
    
    # Create semi-transparent white rectangles as background
    padding = 10  # Margin around text
    win_rect = win_text.get_rect(topleft=(500, 250))
    lose_rect = lose_text.get_rect(topleft=(500, 350))
    
    # Create surfaces for the rectangles with alpha
    win_bg = pygame.Surface((win_rect.width + 2 * padding, win_rect.height + 2 * padding), pygame.SRCALPHA)
    lose_bg = pygame.Surface((lose_rect.width + 2 * padding, lose_rect.height + 2 * padding), pygame.SRCALPHA)
    
    # Fill with semi-transparent white (255, 255, 255, 100)
    win_bg.fill((255, 255, 255, 100))
    lose_bg.fill((255, 255, 255, 100))
    
    # Blit the backgrounds
    screen.blit(win_bg, (win_rect.x - padding, win_rect.y - padding))
    screen.blit(lose_bg, (lose_rect.x - padding, lose_rect.y - padding))
    
    # Blit the text over the backgrounds
    screen.blit(win_text, (500, 250))
    screen.blit(lose_text, (500, 350))
    
    pygame.display.flip()
    time.sleep(3)
def draw_enter_lobby_screen(screen, entered_lobby_id, error_message=None):
    screen.fill((20, 20, 80))
    font = pygame.font.SysFont('arial', 40)
    title_font = pygame.font.SysFont('arial', 60)
    title = title_font.render("Enter Lobby ID", True, (255, 255, 255))
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))
    
    # Draw input box
    input_box = pygame.Rect(screen.get_width() // 2 - 200, 300, 400, 50)
    pygame.draw.rect(screen, (255, 255, 255), input_box, 2)
    text_surface = font.render(entered_lobby_id, True, (255, 255, 255))
    screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))
    
    # Instructions
    instruction = font.render("Press Enter to join, Backspace to delete", True, (255, 255, 255))
    screen.blit(instruction, (screen.get_width() // 2 - instruction.get_width() // 2, 400))
    
    # Draw error message if exists
    if error_message:
        error_surface = font.render(error_message, True, (255, 0, 0))  # Red color for error
        error_rect = error_surface.get_rect(center=(screen.get_width() // 2, 480))
        # Draw semi-transparent white background for error message
        padding = 10
        error_bg = pygame.Surface((error_rect.width + 2 * padding, error_rect.height + 2 * padding), pygame.SRCALPHA)
        error_bg.fill((255, 255, 255, 100))  # Semi-transparent white
        screen.blit(error_bg, (error_rect.x - padding, error_rect.y - padding))
        screen.blit(error_surface, error_rect)
    
    pygame.display.flip()
    
    pygame.display.flip()
def draw_game_mode_screen(screen, mouse_pos=None):
    screen.fill((20, 20, 80))
    font = pygame.font.SysFont('arial', 40)
    title_font = pygame.font.SysFont('arial', 60)
    title = title_font.render("Select Game Mode", True, (255, 255, 255))
    
    options = [
        "1: 1 vs 1",
        "2: 2 vs 2",
    ]
    
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))
    
    option_rects = []
    for i, option in enumerate(options):
        text = font.render(option, True, (255, 255, 255) if not mouse_pos or not pygame.Rect(
            screen.get_width() // 2 - 200, 250 + i * 60, 400, 50
        ).collidepoint(mouse_pos) else (255, 255, 0))  # Highlight on hover
        text_rect = text.get_rect(center=(screen.get_width() // 2, 250 + i * 60 + 25))
        screen.blit(text, text_rect)
        clickable_rect = pygame.Rect(screen.get_width() // 2 - 200, 250 + i * 60, 400, 50)
        option_rects.append(clickable_rect)
        
    pygame.display.flip()
    return option_rects
def draw_countdown_screen(screen, countdown_value):
    screen.fill((20, 20, 80))
    font = pygame.font.SysFont('arial', 100)
    if countdown_value is not None:
        text = font.render(str(countdown_value), True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        padding = 10
        bg_rect = pygame.Surface((text_rect.width + 2 * padding, text_rect.height + 2 * padding), pygame.SRCALPHA)
        bg_rect.fill((255, 255, 255, 100))
        screen.blit(bg_rect, (text_rect.x - padding, text_rect.y - padding))
        screen.blit(text, text_rect)
    pygame.display.flip()
def draw_enter_username_screen(screen, username):
    screen.fill((20, 20, 80))
    font = pygame.font.SysFont('arial', 40)
    title_font = pygame.font.SysFont('arial', 60)
    title = title_font.render("Enter Username", True, (255, 255, 255))
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))
    
    input_box = pygame.Rect(screen.get_width() // 2 - 200, 300, 400, 50)
    pygame.draw.rect(screen, (255, 255, 255), input_box, 2)
    text_surface = font.render(username, True, (255, 255, 255))
    screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))
    
    instruction = font.render("Press Enter to confirm, Backspace to delete", True, (255, 255, 255))
    screen.blit(instruction, (screen.get_width() // 2 - instruction.get_width() // 2, 400))
    
    pygame.display.flip()