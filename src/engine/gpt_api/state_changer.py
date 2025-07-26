# Centralize the game_state (initial state)
game_state = {
    "boss_health": 100,
    "fighter_health": 100,
    "boss_mood": "deceptive",
    "fighter_mood": "determined",
    "fighter_name": "the stranger",
    "fighter_class": "human",
    "fighter_level": 7,
    "dungeon_level": 5,
    "last_character_action": "Lucifer just spoke.",
}

def change_game_state(latest_state):
    global game_state
    new_state = {  # external change
        "boss_health": 0,
        "fighter_health": 100,
        "boss_mood": "angry",
        "fighter_mood": "funny",
        "fighter_name": "the stranger",
        "fighter_class": "human",
        "fighter_level": 4,
        "dungeon_level": 3,
        "last_character_action": "Lucifer just spoke.",  
    }
    game_state.clear()
    game_state.update(latest_state)