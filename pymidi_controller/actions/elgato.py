import requests
from pymidi_controller.config import ELGATO_LIGHT_IP

# -------------------------------------------------------------------
# 💡 Elgato Ring Light Controls
# -------------------------------------------------------------------

def get_ring_info():
    """
    Fetch and display full status info for the Elgato Ring Light.
    Includes power state, brightness, and temperature.
    """
    url = f"http://{ELGATO_LIGHT_IP}:9123/elgato/lights"
    try:
        response = requests.get(url, timeout=2)
        response.raise_for_status()
        data = response.json()
        light = data["lights"][0]

        print("Elgato Ring Light Info:")
        print(f"  Power:       {'ON' if light['on'] else 'OFF'}")
        print(f"  Brightness:  {light['brightness']}%")
        print(f"  Temperature: {light['temperature']}K")
        return light

    except Exception as e:
        print(f"❌ Failed to reach Elgato light at {ELGATO_LIGHT_IP}: {e}")


def get_light_state():
    """
    Return the current power state of the Elgato Ring Light (on/off).
    """
    url = f"http://{ELGATO_LIGHT_IP}:9123/elgato/lights"
    response = requests.get(url).json()
    light = response.get("lights", [{}])[0]
    on = light.get("on", 0)
    print(f"Elgato light is {'ON' if on else 'OFF'}")
    return on


def toggle_light():
    """
    Toggle the Elgato Ring Light on/off based on current power state.
    """
    current = get_light_state()
    new_state = 0 if current else 1

    url = f"http://{ELGATO_LIGHT_IP}:9123/elgato/lights"
    response = requests.put(url, json={
        "lights": [{"on": new_state}]
    })

    print(f"Set Elgato light to {'ON' if new_state else 'OFF'}")
    return response.status_code
