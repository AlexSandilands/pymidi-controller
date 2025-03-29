import json
from config import STATE_DIR, HUE_STATE_FILE

STATE_DIR.mkdir(parents=True, exist_ok=True)

def load_state():
    if HUE_STATE_FILE.exists():
        try:
            with open(HUE_STATE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_state(state):
    with open(HUE_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_last_color(group_name):
    state = load_state()
    return state.get("group_colors", {}).get(group_name)

def set_last_color(group_name, color):
    state = load_state()
    if "group_colors" not in state:
        state["group_colors"] = {}
    state["group_colors"][group_name] = color
    save_state(state)
