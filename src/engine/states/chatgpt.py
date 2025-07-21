# add front related stuff of chatgpt to the dummyUI
import openai
import pygame
import threading
import os # For environment variables
import random # For random delay
# Assuming dummyUI can handle an empty input string and a combined thinking state
from dummyUI import draw_ui, WIDTH, font_input

# --- Pygame Setup ---
pygame.init()

# --- LLM Setup ---
# *** IMPORTANT: API Key Management ***
# It's best practice NOT to hardcode API keys directly in your script.
# If someone sees your code, they could use your key and you'd be charged.
# Instead, set them as environment variables in your terminal before running:
#
# For Linux/macOS:
# export METISAI_API_KEY="tpsg-QqIyPsl4xQEVYxZ0oQUiumk3ruklqbh"
# export METISAI_BASE_URL="https://api.metisai.ir/openai/v1"
#
# For Windows (Command Prompt):
# set METISAI_API_KEY="tpsg-QqIyPsl4xQEVYxZ0oQUiumk3ruklqbh"
# set METISAI_BASE_URL="https://api.metisai.ir/openai/v1"
#
# Then run your Python script from the same terminal.
#
# The `os.getenv` function tries to get the value from the environment.
# If it's not found, it uses the second argument as a default (your hardcoded key).
# This provides a fallback for testing but you should ideally remove the hardcoded part
# once you're comfortable with environment variables.

METISAI_API_KEY = os.getenv("METISAI_API_KEY", "tpsg-QqIyPsl4xQEVYxZ0oQUiumk3ruklqbh") # Your MetisAI API Key
METISAI_BASE_URL = os.getenv("METISAI_BASE_URL", "https://api.metisai.ir/openai/v1") # MetisAI's OpenAI-compatible base URL

# Ensure API key is set before initializing the client
if METISAI_API_KEY == "YOUR_METISAI_API_KEY_HERE" or not METISAI_API_KEY:
    print("WARNING: METISAI_API_KEY is not set or is default. Please set it as an environment variable or replace 'YOUR_METISAI_API_KEY_HERE'.")


client = openai.OpenAI(api_key=METISAI_API_KEY, base_url=METISAI_BASE_URL)

# --- Custom Events for LLM Replies and Turn Delays ---
BOSS_LLM_REPLY_EVENT = pygame.USEREVENT + 1
FIGHTER_LLM_REPLY_EVENT = pygame.USEREVENT + 2
TRIGGER_NEXT_TURN_EVENT = pygame.USEREVENT + 3 # New event for signaling end of delay



# to export and display
boss_last_dialog =     ""
fighter_last_dialog =  ""



# --- LLM State Flags ---
is_waiting_for_boss_llm = False
is_waiting_for_fighter_llm = False
is_delaying_for_next_turn = False # New flag to indicate we are in a delay period

# --- Turn Management ---
current_turn = "fighter" # Initial state: Boss has spoken, Fighter's turn to respond

# --- Dialog History ---
dialog_history = [
    {"role": "assistant", "content": "Hmph. You look lost. Do you want to make a deal?."},
]

# --- System Prompts for AI Characters ---
BOSS_SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are the mafia Boss of hell, Lucifer. You are materialistic and powerful,"
        "you always try to either scam or gamble people to own their souls. You speak like a black gangster. "
        "Your goal is to look innocent to the fighter and convince them to join."
        "Do not break character. Keep your responses relatively brief (max 2-3 sentences), unless the Fighter "
        "asks for more detail. Do not offer solutions or quest information unless explicitly asked."
        "You are currently observing the Fighter getting close."

    )
}

FIGHTER_SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are a loanly innocent but clever and pessimistic little kid in an underground and materialistic world full of monsters, demons and corrupted people"
        "You are trying to find a way out of this world and the Lucifer, the mafia Boss of hell, owns the key so you reach out to him. "
        "You know that you can't trust anyone. You are getting close to Lucifer. "
        "Keep your responses concise (1-2 sentences). "
        "Do not break character. You are the player character in this turn-based dialogue."
    )
}

# --- Game State (Example) ---
game_state = {
    "boss_health": 100,
    "player_name": "unknown",
    "player_class": "human",
    "player_level": 7,
    "dungeon_level": 6,
    "last_character_action": "Lucifer just spoke.",
    "boss_mood": "deceptive and greedy",
    "fighter_mood": "determined",
}

# --- LLM Interaction Function for Kael'thas (Boss) ---
def get_boss_response_threaded(messages_context, current_game_state_data):
    global is_waiting_for_boss_llm
    try:
        messages_for_llm = [BOSS_SYSTEM_PROMPT] + list(messages_context)

        last_opponent_idx = -1
        for i, msg in enumerate(messages_for_llm):
            if msg["role"] == "user":
                last_opponent_idx = i

        game_context_string = (
            f"Current game context: The Fighter (a {current_game_state_data['fighter_class']} "
            f"named {current_game_state_data['fighter_name']}, Level {current_game_state_data['fighter_level']}) "
            f"is currently {current_game_state_data['fighter_mood']}. Your health is {current_game_state_data['boss_health']}. "
            f"Your current mood is {current_game_state_data['boss_mood']}. The last action was: {current_game_state_data['last_character_action']}."
        )

        if last_opponent_idx != -1:
            messages_for_llm[last_opponent_idx]["content"] = (
                f"{messages_for_llm[last_opponent_idx]['content']}\n\n"
                f"(Boss Context: {game_context_string})"
            )
        else:
            messages_for_llm.append({"role": "user", "content": f"Begin the encounter. {game_context_string}"})

        print(f"[BOSS LLM] Sending to LLM (last message with context): {messages_for_llm[-1]['content']}")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_for_llm,
            temperature=0.7,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=None,
        )
        llm_response = response.choices[0].message.content
        print(f"[BOSS LLM] Replied: {llm_response}")

        pygame.event.post(pygame.event.Event(BOSS_LLM_REPLY_EVENT, {"reply": llm_response}))

    except openai.APIError as e:
        print(f"OpenAI API Error (Boss): {e}")
        llm_response = f"Boss: [My power falters... API Error: {e.code}]"
        pygame.event.post(pygame.event.Event(BOSS_LLM_REPLY_EVENT, {"reply": llm_response}))
    except openai.APIConnectionError as e:
        print(f"OpenAI API Connection Error (Boss): {e}")
        llm_response = f"Boss: [My power falters... Connection error: {e}]"
        pygame.event.post(pygame.event.Event(BOSS_LLM_REPLY_EVENT, {"reply": llm_response}))
    except Exception as e:
        print(f"Error calling Boss LLM: {e}")
        llm_response = f"Boss: [My arcane senses are muddled... Error: {e}]"
        pygame.event.post(pygame.event.Event(BOSS_LLM_REPLY_EVENT, {"reply": llm_response}))
    finally:
        is_waiting_for_boss_llm = False

# --- LLM Interaction Function for Fighter (Player AI) ---
def get_fighter_response_threaded(messages_context, current_game_state_data):
    global is_waiting_for_fighter_llm
    try:
        messages_for_llm = [FIGHTER_SYSTEM_PROMPT] + list(messages_context)

        last_opponent_idx = -1
        for i, msg in enumerate(messages_for_llm):
            if msg["role"] == "assistant":
                last_opponent_idx = i

        game_context_string = (
            f"Current game context: You are the Fighter (a {current_game_state_data['fighter_class']} "
            f"named {current_game_state_data['fighter_name']}, Level {current_game_state_data['fighter_level']}). "
            f"Kael'thas's health is {current_game_state_data['boss_health']}. Your current mood is {current_game_state_data['fighter_mood']}. "
            f"The last action was: {current_game_state_data['last_character_action']}."
        )

        if last_opponent_idx != -1:
            messages_for_llm[last_opponent_idx]["content"] = (
                f"{messages_for_llm[last_opponent_idx]['content']}\n\n"
                f"(Fighter Context: {game_context_string})"
            )
        else:
            messages_for_llm.append({"role": "assistant", "content": f"The Boss awaits. {game_context_string}"})

        print(f"[FIGHTER LLM] Sending to LLM (last message with context): {messages_for_llm[-1]['content']}")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_for_llm,
            temperature=0.8,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=None,
        )
        llm_response = response.choices[0].message.content
        print(f"[FIGHTER LLM] Replied: {llm_response}")

        pygame.event.post(pygame.event.Event(FIGHTER_LLM_REPLY_EVENT, {"reply": llm_response}))

    except openai.APIError as e:
        print(f"OpenAI API Error (Fighter): {e}")
        llm_response = f"Fighter: [My spirit wavers... API Error: {e.code}]"
        pygame.event.post(pygame.event.Event(FIGHTER_LLM_REPLY_EVENT, {"reply": llm_response}))
    except openai.APIConnectionError as e:
        print(f"OpenAI API Connection Error (Fighter): {e}")
        llm_response = f"Fighter: [My spirit wavers... Connection error: {e}]"
        pygame.event.post(pygame.event.Event(FIGHTER_LLM_REPLY_EVENT, {"reply": llm_response}))
    except Exception as e:
        print(f"Error calling Fighter LLM: {e}")
        llm_response = f"Fighter: [My mind clouds... Error: {e}]"
        pygame.event.post(pygame.event.Event(FIGHTER_LLM_REPLY_EVENT, {"reply": llm_response}))
    finally:
        is_waiting_for_fighter_llm = False


# --- Helper function to draw multiline text ---
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


# --- Game UI Variables ---
dialog_display_scroll_offset = 0

# --- Main Game Loop ---
def main():
    global is_waiting_for_boss_llm, is_waiting_for_fighter_llm, is_delaying_for_next_turn, dialog_display_scroll_offset, current_turn
    global boss_last_dialog, fighter_last_dialog
    running = True
    clock = pygame.time.Clock()

    # Initial state: Boss has already made the first move.
    current_turn = "fighter"
    # Immediately trigger the first Fighter response without an initial delay
    # because the Boss's initial line is already in history.
    # The delay will apply *after* the Fighter responds.


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.K_ESCAPE:
                running = False

            # --- Handle Boss LLM Reply Event ---
            elif event.type == BOSS_LLM_REPLY_EVENT:
                llm_response_content = event.reply

                boss_last_dialog = llm_response_content

                dialog_history.append({"role": "assistant", "content": llm_response_content})
                game_state["last_character_action"] = f"Lucifer just said: '{llm_response_content[:40]}...'"
                is_waiting_for_boss_llm = False # Boss has finished thinking
                dialog_display_scroll_offset = 0 # Auto-scroll to bottom

                # Now, start the delay for the Fighter's turn
                current_turn = "fighter" # Set who should speak next
                delay_time = random.randint(15, 20) * 1000 # Convert to milliseconds
                pygame.time.set_timer(TRIGGER_NEXT_TURN_EVENT, delay_time, 1) # Fire once
                is_delaying_for_next_turn = True
                print(f"Boss replied. Starting {delay_time / 1000}s delay for Fighter's turn...")

            # --- Handle Fighter LLM Reply Event ---
            elif event.type == FIGHTER_LLM_REPLY_EVENT:
                llm_response_content = event.reply

                fighter_last_dialog = llm_response_content

                dialog_history.append({"role": "user", "content": llm_response_content})
                game_state["last_character_action"] = f"Valiant Hero just said: '{llm_response_content[:40]}...'"
                is_waiting_for_fighter_llm = False # Fighter has finished thinking
                dialog_display_scroll_offset = 0 # Auto-scroll to bottom

                # Now, start the delay for the Boss's turn
                current_turn = "boss" # Set who should speak next
                delay_time = random.randint(15, 20) * 1000 # Convert to milliseconds
                pygame.time.set_timer(TRIGGER_NEXT_TURN_EVENT, delay_time, 1) # Fire once
                is_delaying_for_next_turn = True
                print(f"Fighter replied. Starting {delay_time / 1000}s delay for Boss's turn...")

            # --- Handle Trigger Next Turn Event ---
            elif event.type == TRIGGER_NEXT_TURN_EVENT:
                is_delaying_for_next_turn = False
                print("Delay ended. Next turn triggered.")
                # The automatic turn logic below will now pick up the current_turn

        # --- Automatic Turn Logic ---
        # Trigger an AI only if no AI is currently processing and no delay is active
        if not is_waiting_for_boss_llm and not is_waiting_for_fighter_llm and not is_delaying_for_next_turn:
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

        # --- Drawing ---
        # Pass an empty string for user_input_text.
        # The UI should display "AI Thinking..." if either AI is waiting or if we are in a delay.
        is_overall_thinking_or_delaying = is_waiting_for_boss_llm or is_waiting_for_fighter_llm or is_delaying_for_next_turn
        draw_ui(dialog_history, "", is_overall_thinking_or_delaying, dialog_display_scroll_offset)


        # Cap the frame rate
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()