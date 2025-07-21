# add front related stuff of chatgpt to the dummyUI
import openai
import pygame
import threading
import os # For environment variables
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


client = openai.OpenAI(api_key=METISAI_API_KEY, base_url=METISAI_BASE_URL)# Initialize the OpenAI client. This object is your "waiter" for API calls. It uses the key to authenticate and the base_url to know where to send requests.
LLM_REPLY_EVENT = pygame.USEREVENT + 1 # Custom event type for LLM replies. Pygame needs a way to know when the LLM thread finishes and sends back a response.
is_waiting_for_llm = False # Flag to prevent multiple concurrent LLM requests. We don't want to send a new request before the previous one has finished.


# Dialog history: This is crucial! It keeps track of the conversation so the LLM
# knows the context of what has been said before.
# Each message is a dictionary with a 'role' and 'content'.
dialog_history = [
    # The 'system' role is like setting the model's "instructions" or "persona".
    # This is how you tell GPT-4o-mini to BE Kael'thas.
    {"role": "system", "content": (
        "You are the fearsome and ancient Dungeon Boss, Kael'thas. You are arrogant, powerful, and slightly "
        "bored by intruders. You speak concisely but with a theatrical flair. "
        "Your goal is to intimidate and perhaps toy with the Fighter. "
        "Do not break character. Keep your responses relatively brief (max 2-3 sentences), unless the Fighter "
        "asks for more detail. Do not offer solutions or quest information unless explicitly asked."
        "You are currently observing the Fighter."
    )},
    # The 'assistant' role is for the AI's responses.
    # We provide an initial response to start the conversation from the Boss's side.
    {"role": "assistant", "content": "Hmph. Another foolish mortal dares to disturb my slumber? State your purpose, worm."},
]

# --- Game State (Example) ---
# This dictionary holds dynamic information about the game that can be
# injected into the LLM's context. This makes the LLM's responses more
# relevant to the current game situation.
game_state = {
    "boss_health": 100,
    "fighter_name": "Valiant Hero",
    "fighter_class": "Paladin",
    "fighter_level": 7,
    "dungeon_level": 5,
    "last_player_action": "stood defiantly", # This will be updated by player input
    "boss_mood": "annoyed", # Could be 'angry', 'curious', 'bored', 'amused'
}

# --- LLM Interaction Function (to be run in a separate thread) ---
# We run this in a separate thread because API calls take time (they go over the internet).
# If we ran it in the main Pygame loop, the game would freeze until the response came back.
def get_llm_response_threaded(messages_context, current_game_state_data):
    global is_waiting_for_llm # Allows us to modify the global flag
    try:
        # Create a copy of messages_context to modify for the LLM call.
        # This prevents issues if the main thread modifies dialog_history while
        # this thread is preparing the messages.
        messages_for_llm = list(messages_context)

        # Inject dynamic game state into the conversation for the LLM's awareness.
        # We append this context to the *last user message* so the LLM knows
        # the current situation when responding to the player's last input.
        last_user_idx = -1
        for i, msg in enumerate(messages_for_llm):
            if msg["role"] == "user":
                last_user_idx = i

        game_context_string = (
            f"Current game context: The Fighter (a {current_game_state_data['fighter_class']} "
            f"named {current_game_state_data['fighter_name']}, Level {current_game_state_data['fighter_level']}) "
            f"{current_game_state_data['last_player_action']}. Your health is {current_game_state_data['boss_health']}. "
            f"Your current mood is {current_game_state_data['boss_mood']}."
        )

        if last_user_idx != -1:
            # Append context to the last user message
            messages_for_llm[last_user_idx]["content"] = (
                f"{messages_for_llm[last_user_idx]['content']}\n\n"
                f"({game_context_string})" # Wrap in parentheses to visually separate
            )
        else:
            # Fallback: if no user message yet (unlikely after initial setup), add it as a new user message.
            messages_for_llm.append({"role": "user", "content": game_context_string})

        print(f"Sending to LLM (last message with context): {messages_for_llm[-1]['content']}") # Debug print

        # --- The Core OpenAI API Call ---
        # This is where your program asks the LLM for a response.
        response = client.chat.completions.create(
            # Required Parameters:
            model="gpt-4o-mini",  # The specific model you want to use.
                                   # 'gpt-4o-mini' is a fast, cost-effective model.
            messages=messages_for_llm, # The conversation history (including system prompt and game context).

            # Optional Control Parameters (you asked to see these!):
            temperature=0.7,       # Controls creativity and randomness (0.0-2.0).
                                   # 0.0 means very deterministic (similar responses for same input).
                                   # 1.0 means more creative/random. Good for role-playing.
                                   # 0.7 is a good balance for creative but coherent text.
            max_tokens=150,        # Maximum number of tokens (words/parts of words) in the response.
                                   # Helps control response length, preventing the Boss from writing novels.
                                   # One token is roughly 4 characters for English text.
            top_p=1,               # Controls diversity by sampling from the most probable tokens.
                                   # 1 means consider all tokens. 0.1 means only consider top 10% most probable.
                                   # (Advanced: usually adjust temperature OR top_p, not both significantly).
            frequency_penalty=0.0, # Penalizes new tokens based on their existing frequency in the text.
                                   # Higher values (up to 2.0) make the model less likely to repeat itself.
            presence_penalty=0.0,  # Penalizes new tokens based on whether they appear in the text so far.
                                   # Higher values (up to 2.0) encourage the model to talk about new topics.
            stop=None,             # A list of strings where the model should stop generating.
                                   # E.g., `stop=["\nFighter:", "\nBoss:"]` could prevent it from
                                   # accidentally starting another turn in the dialog.
                                   # (Not strictly necessary for simple conversational turns).
        )
        llm_response = response.choices[0].message.content # Extract the actual text from the response object.
        print(f"LLM replied: {llm_response}") # Debug print

        # Post a Pygame event to the main thread so it knows the response is ready.
        pygame.event.post(pygame.event.Event(LLM_REPLY_EVENT, {"reply": llm_response}))

    except openai.APIError as e:
        # Catch specific API errors (e.g., invalid key, rate limit)
        print(f"OpenAI API Error: {e}")
        llm_response = f"Boss: [My power falters... API Error: {e.code}]"
        pygame.event.post(pygame.event.Event(LLM_REPLY_EVENT, {"reply": llm_response}))
    except openai.APIConnectionError as e:
        # Catch errors related to network connection
        print(f"OpenAI API Connection Error: {e}")
        llm_response = f"Boss: [My power falters... Connection error: {e}]"
        pygame.event.post(pygame.event.Event(LLM_REPLY_EVENT, {"reply": llm_response}))
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Error calling LLM: {e}")
        llm_response = f"Boss: [My arcane senses are muddled... Error: {e}]"
        pygame.event.post(pygame.event.Event(LLM_REPLY_EVENT, {"reply": llm_response}))
    finally:
        is_waiting_for_llm = False # Release the flag, even if an error occurred.

# --- Helper function to draw multiline text ---
# This is a good utility to display long messages within a specific rectangle.
def draw_text_multiline(surface, text, font, color, rect, line_height_factor=1.2):
    words = text.split(' ')
    lines = []
    current_line = []
    current_line_width = 0

    space_width = font.size(' ')[0] # Width of a single space

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
        # Check if drawing this line would go beyond the rect.bottom
        if y_offset + text_surface.get_height() * line_height_factor > rect.bottom:
            break # Stop drawing if we're out of bounds
        surface.blit(text_surface, (rect.left, y_offset))
        y_offset += font.get_height() * line_height_factor
    return y_offset # Return the y position after drawing all lines (useful for determining total height)


# --- Game UI Variables ---
user_input_text = ""
dialog_display_scroll_offset = 0 # Currently not used for active scrolling, but keeps display at bottom

# --- Main Game Loop ---
def main():
    global user_input_text, is_waiting_for_llm, dialog_display_scroll_offset

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.K_ESCAPE: # Added to quickly quit for testing
                running = False
            elif event.type == pygame.KEYDOWN:
                if not is_waiting_for_llm: # Only allow input if not waiting for LLM response
                    if event.key == pygame.K_RETURN:
                        if user_input_text.strip(): # If user typed something (not just spaces)
                            # Update game state based on player action
                            game_state["last_player_action"] = f"said '{user_input_text}'"

                            # Add user's message to dialog history (for display and for LLM context)
                            dialog_history.append({"role": "user", "content": user_input_text})

                            print(f"User sent: {user_input_text}") # Debug print

                            # Start the LLM request in a new thread
                            is_waiting_for_llm = True # Set flag to indicate we're waiting
                            llm_thread = threading.Thread(
                                target=get_llm_response_threaded,
                                args=(list(dialog_history), game_state), # Pass a COPY of history and current game_state
                                daemon=True # Daemon threads exit when the main program exits
                            )
                            llm_thread.start()
                            user_input_text = "" # Clear input box after sending
                    elif event.key == pygame.K_BACKSPACE:
                        user_input_text = user_input_text[:-1] # Remove last character
                    else:
                        # Add character if it's printable and fits in the input box
                        if event.unicode.isprintable() and font_input.size(user_input_text + event.unicode)[0] < (WIDTH - 100 - 20):
                            user_input_text += event.unicode

            # --- Handle LLM Reply Event ---
            # This event is posted by the `get_llm_response_threaded` function
            # when it gets a reply from the LLM.
            elif event.type == LLM_REPLY_EVENT:
                llm_response_content = event.reply
                # Add LLM's response to dialog history
                dialog_history.append({"role": "assistant", "content": llm_response_content})
                # Auto-scroll to bottom after new message (simplified for now)
                # This ensures the newest message is always visible.
                dialog_display_scroll_offset = 0

        # --- Drawing ---
        draw_ui(dialog_history, user_input_text, is_waiting_for_llm, dialog_display_scroll_offset)

        # Cap the frame rate
        clock.tick(60) # Limit to 60 frames per second

    pygame.quit() # Uninitialize Pygame modules

if __name__ == "__main__":
    main()