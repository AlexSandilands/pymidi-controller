import requests
import time
from pymidi_controller.utils.config_manager import load_config, save_config

# -------------------------------------------------------------------
# 🌐 Hue Bridge Discovery & API Key Creation
# -------------------------------------------------------------------

def discover_bridge():
    """
    Discover the Hue Bridge on the local network using Philips N-UPnP service.
    """
    print("🔍 Discovering Hue Bridge via N-UPnP...")

    response = requests.get("https://discovery.meethue.com/")
    bridges = response.json()

    if not bridges:
        raise RuntimeError("❌ No Hue Bridge found on the local network.")

    bridge_ip = bridges[0]["internalipaddress"]
    print(f"✅ Found Hue Bridge at {bridge_ip}")
    return bridge_ip


def create_user(bridge_ip, app_name="pymidi-controller"):
    """
    Prompt user to press the bridge link button and create a new API key.
    """
    print("🟡 Press the physical link button on the Hue Bridge, then press Enter...")
    input("🔘 Waiting for confirmation...")

    url = f"http://{bridge_ip}/api"
    payload = {"devicetype": f"{app_name}#linux"}

    for i in range(30):  # Retry for up to 30 seconds
        response = requests.post(url, json=payload).json()
        print(".", end="", flush=True)
        time.sleep(1)

        if "error" in response[0]:
            if response[0]["error"]["type"] == 101:
                continue  # Link button not pressed yet
            else:
                raise RuntimeError(response[0]["error"]["description"])
        elif "success" in response[0]:
            username = response[0]["success"]["username"]
            print(f"\n✅ API key created: {username}")
            return username

    raise TimeoutError("❌ Timeout waiting for link button to be pressed.")


def save_to_config(ip, api_key):
    """
    Ask to save the discovered IP and API key into .env.
    """
    print(f"\nDiscovered Bridge IP: {ip}")
    print(f"Generated API Key:     {api_key}")

    save = input("\n💾 Save this info to your .env file? [y/N] ").strip().lower()
    if save == "y":
        config = load_config()
        config.setdefault("hue", {})
        config["hue"]["bridge_ip"] = ip
        config["hue"]["api_key"]   = api_key
        save_config(config)
        print(f"✅ Saved to config.yaml:\n  HUE_BRIDGE_IP={ip}\n  HUE_API_KEY={api_key}")

    else:
        print("⚠️ Skipped saving to config. You can manually add these later.")


def main():
    bridge_ip = discover_bridge()
    api_key = create_user(bridge_ip)
    save_to_config(bridge_ip, api_key)


if __name__ == "__main__":
    main()
