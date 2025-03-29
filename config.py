from pathlib import Path
from dotenv import load_dotenv
import os

# Project root
ROOT_DIR = Path(__file__).resolve().parent

# Shared folders
SETTINGS_DIR = ROOT_DIR / "user_settings"
STATE_DIR = ROOT_DIR / "state"

# CLI
CLI_FILE = ROOT_DIR / "cli.py"

# Key files
MIDI_BINDINGS_FILE = SETTINGS_DIR / "midi_bindings.json"
MIDI_DEVICES_FILE = SETTINGS_DIR / "midi_devices.json"
COLOR_CYCLES_FILE = SETTINGS_DIR / "color_cycles.json"
HUE_STATE_FILE = STATE_DIR / "hue_state.json"

# Load .env if present
ENV_FILE = SETTINGS_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE)

# Hue and Elgato vars (fail loudly if missing)
HUE_BRIDGE_IP = os.getenv("HUE_BRIDGE_IP")
HUE_API_KEY = os.getenv("HUE_API_KEY")
ELGATO_LIGHT_IP = os.getenv("ELGATO_LIGHT_IP")

if not HUE_BRIDGE_IP or not HUE_API_KEY:
    raise RuntimeError("Missing HUE_BRIDGE_IP or HUE_API_KEY in environment")

if not ELGATO_LIGHT_IP:
    raise RuntimeError("Missing ELGATO_LIGHT_IP in environment")
