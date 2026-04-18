"""Runtime settings storage for the snake game."""

import json

from snake_app.constants import SETTINGS_FILE


sound_volume = 0.5
game_speed = 0.1


def load_settings():
    """Load persisted settings into module state."""
    global sound_volume, game_speed
    if SETTINGS_FILE.exists():
        try:
            with SETTINGS_FILE.open("r", encoding="utf-8") as file:
                settings = json.load(file)
        except Exception as error:
            print("Error loading settings:", error)
            sound_volume = 0.5
            game_speed = 0.1
            return
        sound_volume = settings.get("sound_volume", 0.5)
        game_speed = settings.get("game_speed", 0.4)
        return
    sound_volume = 0.5
    game_speed = 0.1


def save_settings():
    """Persist current settings to disk."""
    settings = {
        "sound_volume": sound_volume,
        "game_speed": game_speed,
    }
    try:
        with SETTINGS_FILE.open("w", encoding="utf-8") as file:
            json.dump(settings, file)
    except Exception as error:
        print("Error saving settings:", error)


def set_sound_volume(value):
    """Update sound volume in module state."""
    global sound_volume
    sound_volume = value


def set_game_speed(value):
    """Update game speed in module state."""
    global game_speed
    game_speed = value


load_settings()
