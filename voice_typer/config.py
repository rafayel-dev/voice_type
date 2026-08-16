import os
import json
import logging
# --- Paths ---
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")
LOG_FILE = os.path.join(APP_DIR, "voice_typer.log")

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("VoiceTyper")

# --- Audio Constants ---
CHUNK = 1024
FORMAT_INT = 8  # pyaudio.paInt16 = 8
CHANNELS = 1
RATE = 16000

# --- Default Settings ---
DEFAULT_SETTINGS = {
    "language": "bn",  # "bn", "en"
    "engine": "google",
    "hotkey_start_stop": "ctrl+alt+space",
    "hotkey_english": "ctrl+alt+e",
    "hotkey_bangla": "ctrl+alt+b",
}

def load_settings():
    """Load user settings from JSON file, merging with defaults."""
    settings = DEFAULT_SETTINGS.copy()
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            settings.update(saved)
            logger.info("Settings loaded from %s", SETTINGS_FILE)
        except Exception as e:
            logger.warning("Failed to load settings: %s. Using defaults.", e)
    return settings

def save_settings(settings):
    """Persist user settings to JSON file."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        logger.info("Settings saved to %s", SETTINGS_FILE)
    except Exception as e:
        logger.error("Failed to save settings: %s", e)
