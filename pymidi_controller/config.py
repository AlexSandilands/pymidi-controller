from pymidi_controller.utils.config_manager import load_config

_cfg = load_config()

# Credentials
HUE_BRIDGE_IP   = _cfg.get("hue", {}).get("bridge_ip")
HUE_API_KEY     = _cfg.get("hue", {}).get("api_key")
ELGATO_LIGHT_IP = _cfg.get("elgato", {}).get("ip")

# MIDI section
_m = _cfg.get("midi", {})
MIDI_DEVICES    = _m.get("devices", [])
MIDI_BINDINGS   = _m.get("bindings", {})
COLOR_CYCLES    = _m.get("color_cycles", {})

# CLI entrypoint
CLI_COMMAND = "pymidi-controller"
