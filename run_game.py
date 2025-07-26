import pygame  # Import pygame for game functionality
import config  # Import configuration settings like scene dimensions and FPS
import math    # Import math for sin function in pulse effect
from src.engine.state_manager import StateManager
from src.engine.gpt_api.state_changer import*
from src.engine.gpt_api.API import*
from src.engine.gpt_api.dummyUI import*
from src.engine.states.playing import PlayingState

# Initialize pygame
pygame.init()  # Initialize all imported pygame modules
pygame.mixer.init()  # Initialize mixer for audio
pygame.font.init()  # Explicitly initialize font module
pygame.display.set_caption(config.CAPTION)  # Set the window title
scene = pygame.display.set_mode((config.SCENE_WIDTH, config.SCENE_HEIGHT))  # Set up the main game window
clock = pygame.time.Clock()  # Create a clock to manage the game's frame rate

# Initialize state manager
state_manager = StateManager(scene)
dialog_enabled = False

running = True
while running:
    current_time = pygame.time.get_ticks()  # Get current time for debounce
    config.PULSE_TIME += config.PULSE_SPEED  # Update pulse animation
    scale = config.PULSE_SCALE * abs(math.sin(config.PULSE_TIME))  # Calculate scale for pulse

    dialog_enabled = (state_manager.current_map == "map_boss" and not PlayingState.game_over_fighter1 and not PlayingState.win)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        elif dialog_enabled:
            if event.type == BOSS_LLM_REPLY_EVENT:# --- Handle Boss LLM Reply Event ---
                llm_response_content = event.reply
                BOSS_LAST_dialogue = llm_response_content
                dialog_history.append({"role": "assistant", "content": llm_response_content})
                game_state["last_character_action"] = f"Kael'thas just said: '{llm_response_content[:40]}...'"
                is_waiting_for_boss_llm = False # Boss has finished thinking
                # Now, start the delay for the Fighter's turn
                current_turn = "fighter" # Set who should speak next
                delay_time = random.randint(10, 15) * 1000 # Convert to milliseconds
                pygame.time.set_timer(TRIGGER_NEXT_TURN_EVENT, delay_time, 1) # Fire once
                is_delaying_for_next_turn = True
                print(f"Boss replied. Starting {delay_time / 1000}s delay for Fighter's turn...")
            elif event.type == FIGHTER_LLM_REPLY_EVENT:# --- Handle Fighter LLM Reply Event ---
                llm_response_content = event.reply
                FIGHTER_LAST_dialog = llm_response_content
                dialog_history.append({"role": "user", "content": llm_response_content})
                game_state["last_character_action"] = f"Valiant Hero just said: '{llm_response_content[:40]}...'"
                is_waiting_for_fighter_llm = False # Fighter has finished thinking
                # Now, start the delay for the Boss's turn
                current_turn = "boss" # Set who should speak next
                delay_time = random.randint(10, 15) * 1000 # Convert to milliseconds
                pygame.time.set_timer(TRIGGER_NEXT_TURN_EVENT, delay_time, 1) # Fire once
                is_delaying_for_next_turn = True
                print(f"Fighter replied. Starting {delay_time / 1000}s delay for Boss's turn...")
            elif event.type == TRIGGER_NEXT_TURN_EVENT:# --- Handle Trigger Next Turn Event ---
                is_delaying_for_next_turn = False
                print("Delay ended. Next turn triggered.")
                # The automatic turn logic below will now pick up the current_turn
                change_game_state()
            state_manager.handle_event(event, current_time, scale)
        else:
            state_manager.handle_event(event, current_time, scale)

    if dialog_initialized and dialog_enabled and not is_waiting_for_boss_llm and not is_waiting_for_fighter_llm and not is_delaying_for_next_turn:
        
        if current_turn == "fighter":
            is_waiting_for_fighter_llm = True
            fighter_llm_thread = threading.Thread(
                target=get_fighter_response_threaded,
                args=(list(dialog_history), game_state),
                daemon=True
            )
            fighter_llm_thread.start()
            print("Fighter AI turn started.")
        elif current_turn == "boss":
            is_waiting_for_boss_llm = True
            boss_llm_thread = threading.Thread(
                target=get_boss_response_threaded,
                args=(list(dialog_history), game_state),
                daemon=True
            )
            boss_llm_thread.start()
            print("Boss AI turn started.")
    
    # Update and draw the current state
    
    state_manager.update(current_time, scale)
    state_manager.draw(scale)
    # display_texts(scene)
    pygame.display.flip()  # Refresh the display
    clock.tick(config.FPS)  # Maintain the FPS defined in config

pygame.quit()  # Clean up and close the pygame window