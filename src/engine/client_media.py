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

def draw_health_bar(screen, rect, health, max_health):
    bar_width = rect[2] 
    bar_height = 10  
    bar_x = rect[0]
    bar_y = rect[1] - bar_height - 5  
    health_ratio = health / max_health
    health_width = bar_width * health_ratio
    pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height)) 
    pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, health_width, bar_height))  

def static_render(screen, rect, obj, sprite_type, images):
    image = images.get(sprite_type)
    if image:
        # facing_right = obj.get("facing_right", True)
        if sprite_type == "projectiles":
            w = 10
            h = 10
        # if not facing_right:
        #     image = pygame.transform.flip(image, True, False)
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
        
        draw_health_bar(screen, rect, health, max_health)
        # print(f"Rendered fighter: id={obj['id']}, state={state}, health={health}/{max_health}")
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

def draw_menu_screen(screen):
    screen.fill((20, 20, 80))
    font = pygame.font.SysFont('arial', 40)
    title_font = pygame.font.SysFont('arial', 60)
    title = title_font.render("Pixelhalla", True, (255, 255, 255))
    
    options = [
        "1: Find Random 1v1 Game",
        "2: Create Lobby",
        "3: Join Lobby (Not implemented)",
    ]
    
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))
    
    for i, option in enumerate(options):
        text = font.render(option, True, (255, 255, 255))
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 250 + i * 60))
        
    pygame.display.flip()

def draw_lobby_screen(screen):
    screen.fill((20, 80, 20))
    font = pygame.font.SysFont('arial', 40)
    title_font = pygame.font.SysFont('arial', 60)
    title = title_font.render("Lobby", True, (255, 255, 255))
    
    options = [
        "Waiting for players...",
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
    screen.fill((0, 0, 0))  
    font = pygame.font.SysFont('arial', 50) 
    win_text = font.render(f"Team {winning_team} Won!", True, (0, 255, 0)) 
    lose_text = font.render(f"Team {losing_team} Lost!", True, (255, 0, 0)) 
    screen.blit(win_text, (400, 250)) 
    screen.blit(lose_text, (400, 350)) 
    pygame.display.flip()
    time.sleep(2)
