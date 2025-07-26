# add front related stuff of chatgpt to the dummyUI
import openai
import pygame
import threading
import random # For random delay
from src.engine.gpt_api.state_changer import game_state
pygame.init()
# read to UI
BOSS_LAST_dialogue =   "" # external read
FIGHTER_LAST_dialog =  "" # external read
# Instead import the centralized game_state:
client = openai.OpenAI(api_key="tpsg-QqIyPsl4xQEVYxZ0oQUiumk3ruklqbh", base_url="https://api.metisai.ir/openai/v1")
# --- Custom Events for LLM Replies and Turn Delays ---
BOSS_LLM_REPLY_EVENT = pygame.USEREVENT + 1
FIGHTER_LLM_REPLY_EVENT = pygame.USEREVENT + 2
TRIGGER_NEXT_TURN_EVENT = pygame.USEREVENT + 3 # for signaling end of delay
# --- LLM State Flags ---
is_waiting_for_boss_llm = False
is_waiting_for_fighter_llm = False
is_delaying_for_next_turn = False
dialog_initialized = True
# --- Turn Management ---
current_turn = "fighter" # Initial state: Boss has spoken, Fighter's turn to respond

dialog_history = [# --- Dialog History gets fed into LLM ---
    {"role": "assistant", "content": "Hmph. You look lost. Do you want to make a deal?."},
]
BOSS_SYSTEM_PROMPT = { # --- System Prompts and Game State ---
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

# --- LLM Interaction Function for Boss and fighter ---
def get_boss_response_threaded(messages_context, current_game_state_data):
    global is_waiting_for_boss_llm, BOSS_LAST_dialogue
    try:
        messages_for_llm = [BOSS_SYSTEM_PROMPT] + list(messages_context)

        last_opponent_idx = -1
        for i, msg in enumerate(messages_for_llm):
            if msg["role"] == "user":
                last_opponent_idx = i

        game_context_string = (
            f"Current game context: The Fighter (a {current_game_state_data['fighter_class']} "
            f"named {current_game_state_data['fighter_name']}, Level {current_game_state_data['fighter_level']}) "
            f"is currently {current_game_state_data['fighter_mood']}. fighters health is {current_game_state_data['fighter_health']}. Your health is {current_game_state_data['boss_health']}. "
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

        BOSS_LAST_dialogue = llm_response

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
def get_fighter_response_threaded(messages_context, current_game_state_data):
    global is_waiting_for_fighter_llm, FIGHTER_LAST_dialog
    try:
        messages_for_llm = [FIGHTER_SYSTEM_PROMPT] + list(messages_context)

        last_opponent_idx = -1
        for i, msg in enumerate(messages_for_llm):
            if msg["role"] == "assistant":
                last_opponent_idx = i

        game_context_string = (
            f"Current game context: You are the Fighter (a {current_game_state_data['fighter_class']} "
            f"named {current_game_state_data['fighter_name']}, Level {current_game_state_data['fighter_level']}). "
            f"Lucifer's health is {current_game_state_data['boss_health']}. Lucifer's health is {current_game_state_data['boss_health']}. Lucifer's mood is {current_game_state_data['boss_mood']} Your current mood is {current_game_state_data['fighter_mood']} "
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

        FIGHTER_LAST_dialog = llm_response

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
# --- Loop ---
def gpt():
    global is_waiting_for_boss_llm, is_waiting_for_fighter_llm, is_delaying_for_next_turn, current_turn
    global BOSS_LAST_dialogue, FIGHTER_LAST_dialog
    
    for event in pygame.event.get():
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


if __name__ == "__main__":
    while True:
        gpt()