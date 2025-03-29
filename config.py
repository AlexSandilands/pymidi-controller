from dotenv import load_dotenv
import os

load_dotenv()

HUE_BRIDGE_IP = os.getenv("HUE_BRIDGE_IP")
HUE_API_KEY = os.getenv("HUE_API_KEY")
ELGATO_LIGHT_IP = os.getenv("ELGATO_LIGHT_IP")

if not HUE_API_KEY:
    raise RuntimeError("Missing HUE_API_KEY in environment")

if not ELGATO_LIGHT_IP:
    raise RuntimeError("Missing ELGATO_LIGHT_IP in environment")
