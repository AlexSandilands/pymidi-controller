import requests
from pymidi_controller.config import HUE_BRIDGE_IP, HUE_API_KEY
from pymidi_controller.utils.state_manager import get_last_color, set_last_color
from pymidi_controller.utils.color_cycle import get_color_cycle

# -------------------------------------------------------------------
# 🎨 Color Presets
# -------------------------------------------------------------------

PRESET_COLORS = {
    "red": 0,
    "orange": 8000,
    "yellow": 12750,
    "green": 25500,
    "cyan": 35000,
    "blue": 46920,
    "purple": 50000,
    "pink": 56100,
    "white": 0,  # White achieved by setting saturation to 0
}

# -------------------------------------------------------------------
# 📋 List Functions
# -------------------------------------------------------------------

def list_groups():
    """Print all Hue groups with their current on/off state."""
    url = f"http://{HUE_BRIDGE_IP}/api/{HUE_API_KEY}/groups"
    groups = requests.get(url).json()

    for group_id, group in groups.items():
        state = group.get('action', {}).get('on')
        print(f"Group ID: {group_id}, Name: {group.get('name')}, State: {'on' if state else 'off'}")


def list_schedules():
    """Print all configured Hue schedules."""
    url = f"http://{HUE_BRIDGE_IP}/api/{HUE_API_KEY}/schedules"
    schedules = requests.get(url).json()

    if not schedules:
        print("No schedules found.")
        return

    for sched_id, sched in schedules.items():
        print(f"ID: {sched_id}, Name: {sched.get('name')}, Status: {sched.get('status')}, Command: {sched.get('command')}")


def list_lights():
    """Print all individual Hue lights with their state, brightness, and effect."""
    url = f"http://{HUE_BRIDGE_IP}/api/{HUE_API_KEY}/lights"
    lights = requests.get(url).json()

    if not lights:
        print("No lights found.")
        return

    print("Lights:")
    for light_id, light in lights.items():
        state = light.get("state", {})
        name = light.get("name")
        on = state.get("on")
        effect = state.get("effect", "none")
        bri = state.get("bri", "-")
        print(f"  ID: {light_id} | Name: {name} | On: {on} | Brightness: {bri} | Effect: {effect}")

# -------------------------------------------------------------------
# 💡 Group Controls
# -------------------------------------------------------------------

def toggle_group(group_name):
    """Toggle a group on or off based on its current state."""
    url = f"http://{HUE_BRIDGE_IP}/api/{HUE_API_KEY}/groups"
    groups = requests.get(url).json()

    for group_id, group in groups.items():
        if group.get("name") == group_name:
            current_state = group.get("action", {}).get("on")
            new_state = not current_state
            response = requests.put(
                f"{url}/{group_id}/action",
                json={"on": new_state}
            )
            print(f"Toggled group '{group_name}' to {'on' if new_state else 'off'}")
            return response.json()

    raise ValueError(f"No group found with name: {group_name}")

def toggle_red_blue(group_name):
    """Toggle a group color between red or blue based on its current state."""
    last = get_last_color(group_name)
    next_color = "blue" if last == "red" else "red"
    set_group_color(group_name, next_color)
    set_last_color(group_name, next_color)
    print(f"Toggled {group_name} from {last or '[unknown]'} to {next_color}")

def cycle_group_color(group_name):
    """Cycle the color of the group between the values specified in the user settings."""
    colors = get_color_cycle(group_name)
    if not colors:
        raise ValueError(f"No color cycle defined for group '{group_name}'")

    last_color = get_last_color(group_name)
    if last_color not in colors:
        next_index = 0
    else:
        next_index = (colors.index(last_color) + 1) % len(colors)

    next_color = colors[next_index]
    set_group_color(group_name, next_color)
    set_last_color(group_name, next_color)

    print(f"Cycled color for '{group_name}': {last_color or '[unknown]'} → {next_color}")

def set_group_color(group_name, hue_or_color, sat_val=254, bri_val=254):
    """Set a group's color by hue value or preset name."""
    if isinstance(hue_or_color, str):
        hue_key = hue_or_color.lower()
        if hue_key not in PRESET_COLORS:
            raise ValueError(f"Unknown color name: {hue_key}")
        hue_val = PRESET_COLORS[hue_key]
        if hue_key == "white":
            sat_val = 0  # Desaturate for white
    else:
        hue_val = hue_or_color

    url = f"http://{HUE_BRIDGE_IP}/api/{HUE_API_KEY}/groups"
    groups = requests.get(url).json()

    for group_id, group in groups.items():
        if group.get("name") == group_name:
            action_url = f"{url}/{group_id}/action"
            data = {
                "on": True,
                "hue": hue_val,
                "sat": sat_val,
                "bri": bri_val
            }
            response = requests.put(action_url, json=data)
            print(f"Set group '{group_name}' to hue={hue_val}, sat={sat_val}, bri={bri_val}")
            return response.json()

    raise ValueError(f"No group found with name: {group_name}")

# -------------------------------------------------------------------
# ⏰ Schedule Controls
# -------------------------------------------------------------------

def toggle_schedule(schedule_name):
    """Enable or disable a Hue schedule by name."""
    url = f"http://{HUE_BRIDGE_IP}/api/{HUE_API_KEY}/schedules"
    schedules = requests.get(url).json()

    for schedule_id, schedule in schedules.items():
        if schedule.get("name") == schedule_name:
            current_status = schedule.get("status", "enabled")
            new_status = "disabled" if current_status == "enabled" else "enabled"

            response = requests.put(f"{url}/{schedule_id}", json={
                "status": new_status
            })

            print(f"Toggled schedule '{schedule_name}' to {new_status}")
            return response.json()

    raise ValueError(f"No schedule found with name: {schedule_name}")

# -------------------------------------------------------------------
# 🌈 Colorloop Effect
# -------------------------------------------------------------------

def toggle_colorloop(group_name, effect=""):
    """
    Toggle colorloop effect for all lights in a group.
    Accepts an optional override: --effect colorloop / none
    """
    group_url = f"http://{HUE_BRIDGE_IP}/api/{HUE_API_KEY}/groups"
    light_url_base = f"http://{HUE_BRIDGE_IP}/api/{HUE_API_KEY}/lights"

    effect = effect.strip().lower()
    valid_effects = {"", "none", "colorloop"}
    if effect not in valid_effects:
        raise ValueError(f"Invalid effect '{effect}'. Valid options: {', '.join(valid_effects - {''})}")

    groups = requests.get(group_url).json()

    for group_id, group in groups.items():
        if group.get("name") == group_name:
            light_ids = group.get("lights", [])
            if not light_ids:
                print(f"No lights found in group '{group_name}'")
                return

            print(f"Found group '{group_name}' with lights: {light_ids}")

            is_colorloop = False

            if effect == "colorloop":
                is_colorloop = False  # Force toggle "on"
            elif effect == "none":
                is_colorloop = True   # Force toggle "off"
            else:
                # Auto-detect based on lights
                for light_id in light_ids:
                    light = requests.get(f"{light_url_base}/{light_id}").json()
                    current_effect = light.get("state", {}).get("effect", "none")
                    print(f"Light {light_id}: current effect = {current_effect}")
                    if current_effect == "colorloop":
                        is_colorloop = True

            new_effect = "none" if is_colorloop else "colorloop"
            print(f"\nToggling all lights in group to: {new_effect}")

            for light_id in light_ids:
                result = requests.put(f"{light_url_base}/{light_id}/state", json={
                    "on": True,
                    "effect": new_effect
                })
                print(f" → Set Light {light_id} to effect '{new_effect}' - response: {result.status_code}")

            print(f"\nAll lights in group '{group_name}' updated.")
            return

    raise ValueError(f"No group found with name: {group_name}")
