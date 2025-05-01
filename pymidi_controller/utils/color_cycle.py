from pymidi_controller.config import COLOR_CYCLES

# Default fallback cycle if group not defined
DEFAULT_CYCLE = ["red", "blue"]

def get_color_cycle(group_name):
    
    if not COLOR_CYCLES:
        print(f"⚠️  color cycles not found at config.yaml. Using default cycle.")
        return DEFAULT_CYCLE

    return COLOR_CYCLES.get(group_name, DEFAULT_CYCLE)

