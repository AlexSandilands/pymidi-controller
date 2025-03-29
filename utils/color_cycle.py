import json
from config import COLOR_CYCLES_FILE

# Default fallback cycle if group not defined
DEFAULT_CYCLE = ["red", "blue"]

def get_color_cycle(group_name):
    if not COLOR_CYCLES_FILE.exists():
        print(f"⚠️  color_cycles.json not found at {COLOR_CYCLES_FILE}. Using default cycle.")
        return DEFAULT_CYCLE

    try:
        with open(COLOR_CYCLES_FILE, "r") as f:
            cycles = json.load(f)
    except json.JSONDecodeError:
        print("⚠️  color_cycles.json is malformed.")
        return DEFAULT_CYCLE

    return cycles.get(group_name, DEFAULT_CYCLE)
