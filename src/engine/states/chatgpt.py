import openai
from openai import *

#client = OpenAI(api_key = "tpsg-QqIyPsl4xQEVYxZ0oQUiumk3ruklqbh",base_url="https://api.metisai.ir/openai/v1")

#response = client.chat.completions.create(
#model="gpt-4o-mini",
#messages=[{"role": "user", "content": "Salam man be to yare ghadimi :)"}],)
#print(response.choices[0].message.content)


import pygame
import threading
import os # For environment variables
# Use the new client from openai import OpenAI

# --- Pygame Setup ---
pygame.init()

# Screen dimensions
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
font_input = pygame.font.Font(None, 28) # For user input
font_status = pygame.font.Font(None, 20) # For status messages

# --- LLM Setup ---
# It's best practice NOT to hardcode API keys directly in your script.
# Set them as environment variables (e.g., in your terminal before running):
# export METISAI_API_KEY="tpsg-..."
# export METISAI_BASE_URL="https://api.metisai.ir/openai/v1"
METISAI_API_KEY = os.getenv("METISAI_API_KEY", "tpsg-QqIyPsl4xQEVYxZ0oQUiumk3ruklqbh") # Replace if you must hardcode for testing
METISAI_BASE_URL = os.getenv("METISAI_BASE_URL", "https://api.metisai.ir/openai/v1")

# Ensure API key is set before initializing the client
if METISAI_API_KEY == "YOUR_METISAI_API_KEY_HERE" or not METISAI_API_KEY:
    print("WARNING: METISAI_API_KEY is not set or is default. Please set it as an environment variable or replace 'YOUR_METISAI_API_KEY_HERE'.")
    # You might want to exit or disable LLM functionality if the key is missing.
    # For now, we'll proceed, but it will likely fail on API calls.

# Initialize the OpenAI client (using MetisAI's base URL)
client = OpenAI(api_key=METISAI_API_KEY, base_url=METISAI_BASE_URL)

# Custom event type for LLM replies
LLM_REPLY_EVENT = pygame.USEREVENT + 1

# Flag to prevent multiple concurrent LLM requests
is_waiting_for_llm = False

# Dialog history (list of dictionaries, compatible with OpenAI messages format)
# The system message is crucial for setting the context and persona.
dialog_history = [
    {"role": "system", "content": (
        "You are the fearsome and ancient Dungeon Boss, Kael'thas. You are arrogant, powerful, and slightly "
        "bored by intruders. You speak concisely but with a theatrical flair. "
        "Your goal is to intimidate and perhaps toy with the Fighter. "
        "Do not break character. Keep your responses relatively brief (max 2-3 sentences), unless the Fighter "
        "asks for more detail. Do not offer solutions or quest information unless explicitly asked."
        "You are currently observing the Fighter."
    )},
    {"role": "assistant", "content": "Hmph. Another foolish mortal dares to disturb my slumber? State your purpose, worm."},
]

# --- Game State (Example - these values would change during gameplay) ---
game_state = {
    "boss_health": 100,
    "fighter_name": "Valiant Hero",
    "fighter_class": "Paladin",
    "fighter_level": 7,
    "dungeon_level": 5,
    "last_player_action": "stood defiantly",
    "boss_mood": "annoyed", # Could be 'angry', 'curious', 'bored', 'amused'
}

# --- LLM Interaction Function (to be run in a separate thread) ---
def get_llm_response_threaded(messages_context, current_game_state_data):
    global is_waiting_for_llm
    try:
        # Create a copy of messages_context to modify for the LLM call
        messages_for_llm = list(messages_context)

        # Inject dynamic game state into the conversation for the LLM's awareness.
        # This is a good place to be explicit about context.
        # We'll add it as a new user message *before* the actual player's prompt,
        # or append it to the last user message. Appending to the last user message
        # is often more natural for the LLM in a direct conversation.
        
        # Find the last message that is a 'user' message to append context to.
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
            messages_for_llm[last_user_idx]["content"] = (
                f"{messages_for_llm[last_user_idx]['content']}\n\n"
                f"({game_context_string})" # Wrap in parentheses to visually separate
            )
        else:
            # Fallback, if for some reason no user message was found
            messages_for_llm.append({"role": "user", "content": game_context_string})

        print(f"Sending to LLM (last message): {messages_for_llm[-1]['content']}") # Debug print

        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4o-mini", # The model you specified
            messages=messages_for_llm, # Send the full conversation context
            temperature=0.7, # Controls creativity/randomness (0.0-1.0)
            max_tokens=150, # Limit response length to keep dialog snappy
        )
        llm_response = response.choices[0].message.content
        print(f"LLM replied: {llm_response}") # Debug print
        pygame.event.post(pygame.event.Event(LLM_REPLY_EVENT, {"reply": llm_response}))

    except openai.APIError as e:
        print(f"OpenAI API Error: {e}")
        llm_response = f"Boss: [My power falters... API Error: {e.code}]"
        pygame.event.post(pygame.event.Event(LLM_REPLY_EVENT, {"reply": llm_response}))
    except openai.error.APIConnectionError as e:
        # Handle connection-specific errors
        print(f"OpenAI API Connection Error: {e}")
        llm_response = f"Boss: [My power falters... Connection error: {e}]"
        pygame.event.post(pygame.event.Event(LLM_REPLY_EVENT, {"reply": llm_response}))
    except Exception as e:
        print(f"Error calling LLM: {e}")
        llm_response = f"Boss: [My arcane senses are muddled... Error: {e}]"
        pygame.event.post(pygame.event.Event(LLM_REPLY_EVENT, {"reply": llm_response}))
    finally:
        is_waiting_for_llm = False # Release the flag, even on error

# --- Helper function to draw multiline text ---
def draw_text_multiline(surface, text, font, color, rect, line_height_factor=1.2):
    # This function wraps text to fit within a given rectangle
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
dialog_display_scroll_offset = 0 # For future scrolling, though not fully implemented here

# --- Main Game Loop ---
def main():
    global user_input_text, is_waiting_for_llm, dialog_display_scroll_offset

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if not is_waiting_for_llm: # Only allow input if not waiting for LLM
                    if event.key == pygame.K_RETURN:
                        if user_input_text.strip(): # If user typed something
                            # Add user's message to history
                            # Ensure the user's message matches the role expected by LLM
                            # Remove game context from display text for user clarity
                            display_text = f"Fighter: {user_input_text}"
                            dialog_history.append({"role": "user", "content": user_input_text})
                            
                            print(f"User sent: {user_input_text}") # Debug
                            
                            # Start the LLM request in a new thread
                            is_waiting_for_llm = True
                            # Pass a *copy* of dialog_history to the thread to avoid race conditions
                            llm_thread = threading.Thread(
                                target=get_llm_response_threaded,
                                args=(list(dialog_history), game_state), # Pass the game_state
                                daemon=True # Daemon threads exit when the main program exits
                            )
                            llm_thread.start()
                            user_input_text = "" # Clear input box after sending
                    elif event.key == pygame.K_BACKSPACE:
                        user_input_text = user_input_text[:-1]
                    else:
                        # Add character if it's printable
                        if event.unicode.isprintable():
                            user_input_text += event.unicode
            
            # --- Handle LLM Reply Event ---
            elif event.type == LLM_REPLY_EVENT:
                llm_response_content = event.reply
                # Add LLM's response to history
                dialog_history.append({"role": "assistant", "content": llm_response_content})
                # Auto-scroll to bottom after new message (simplified)
                dialog_display_scroll_offset = 0 # Reset to show latest

        # --- Drawing ---
        screen.fill(BLACK)

        # 1. Dialog History Area
        dialog_rect = pygame.Rect(50, 20, WIDTH - 100, HEIGHT - 150)
        pygame.draw.rect(screen, GRAY, dialog_rect, 0, 8) # Background for dialog area
        pygame.draw.rect(screen, LIGHT_GRAY, dialog_rect, 2, 8) # Border

        # Calculate where to start drawing dialog messages to simulate bottom-up fill
        # This requires knowing the total height of all messages
        
        # Filter out the system prompt for display purposes
        display_messages = [msg for msg in dialog_history if msg["role"] != "system"]
        
        # Calculate total height of messages if drawn
        temp_surf = pygame.Surface((dialog_rect.width - 20, 1)) # Dummy surface for height calculation
        total_dialog_content_height = 0
        for msg in display_messages:
            prefix = "Fighter: " if msg["role"] == "user" else "Boss: "
            # Clean up injected game context for display, so it doesn't clutter the UI
            display_text_cleaned = msg["content"].split("(Current game context:")[0].strip()
            display_message = prefix + display_text_cleaned
            
            # Use draw_text_multiline to calculate height
            temp_rect = pygame.Rect(0, 0, dialog_rect.width - 20, 1) # Width for wrapping
            line_end_y = draw_text_multiline(temp_surf, display_message, font_dialog, WHITE, temp_rect)
            total_dialog_content_height += line_end_y + 5 # Add a small gap between messages

        # Determine start Y for drawing
        current_y_for_display = dialog_rect.bottom - total_dialog_content_height - dialog_display_scroll_offset
        if current_y_for_display < dialog_rect.top + 10: # Don't draw above top
            current_y_for_display = dialog_rect.top + 10

        # Draw dialog messages
        for msg in display_messages:
            prefix = "Fighter: " if msg["role"] == "user" else "Boss: "
            display_text_cleaned = msg["content"].split("(Current game context:")[0].strip()
            display_message = prefix + display_text_cleaned

            message_rect = pygame.Rect(dialog_rect.left + 10, current_y_for_display, dialog_rect.width - 20, 0)
            line_end_y = draw_text_multiline(screen, display_message, font_dialog, WHITE, message_rect)
            current_y_for_display = line_end_y + 5 # Move down for the next message


        # 2. Input Box Area
        input_box_rect = pygame.Rect(50, HEIGHT - 100, WIDTH - 100, 50)
        pygame.draw.rect(screen, LIGHT_GRAY, input_box_rect, 0, 5) # Background for input
        pygame.draw.rect(screen, WHITE, input_box_rect, 2, 5) # Border

        # Draw current user input
        input_surface = font_input.render(user_input_text, True, BLACK)
        screen.blit(input_surface, (input_box_rect.left + 10, input_box_rect.centery - input_surface.get_height() // 2))

        # 3. Status/Prompt Area
        status_rect = pygame.Rect(50, HEIGHT - 40, WIDTH - 100, 30)
        
        if is_waiting_for_llm:
            status_text_surface = font_status.render("Boss is contemplating your fate...", True, BLUE)
        else:
            status_text_surface = font_status.render("Type your defiance and press ENTER.", True, GREEN)
            if not user_input_text.strip(): # Hint if input is empty
                 status_text_surface = font_status.render("Type your message...", True, LIGHT_GRAY)

        screen.blit(status_text_surface, (status_rect.left, status_rect.top))


        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()