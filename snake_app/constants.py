"""Shared constants and file paths for the snake game."""

from pathlib import Path


WIDTH = 800
HEIGHT = 600
GRID_SIZE = 20

BUTTON_COLOR = (50, 50, 70)
BUTTON_HOVER = (70, 70, 90)
TEXT_COLOR = (200, 200, 210)
FOOD_COLOR = (255, 50, 75)

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
LEADERBOARD_FILE = BASE_DIR / "leaderboard.json"
SETTINGS_FILE = BASE_DIR / "settings.json"
