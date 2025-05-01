from zeroconf import Zeroconf, ServiceBrowser, ServiceListener
from pymidi_controller.utils.config_manager import load_config, save_config
import time

# -------------------------------------------------------------------
# 🔎 Elgato Device Discovery via mDNS
# -------------------------------------------------------------------

class ElgatoListener(ServiceListener):
    """
    Zeroconf listener that prints and optionally saves discovered Elgato devices.
    """
    def add_service(self, zeroconf, type_, name):
        info = zeroconf.get_service_info(type_, name)
        if info:
            ip = ".".join(str(b) for b in info.addresses[0])
            model = info.properties.get(b'md').decode("utf-8") if b'md' in info.properties else "Unknown"

            print(f"Found Elgato Device: {model} @ {ip}")

            save = input("💾 Save this IP to config as elgato ip? [y/N] ").strip().lower()
            if save == "y":
                config = load_config()
                config.setdefault("elgato", {})
                config["elgato"]["ip"] = ip
                save_config(config)
                print(f"✅ Saved elgato ip={ip} to config")
            else:
                print("⚠️ Skipped saving IP to config")


def main(timeout=5):
    """
    Discover Elgato devices via Zeroconf (Bonjour/mDNS) and optionally save IP.
    """
    print("🔍 Searching for Elgato lights on the network...")

    zeroconf = Zeroconf()
    listener = ElgatoListener()

    # Some devices use _elgato._tcp.local., others use _elg._tcp.local.
    browser1 = ServiceBrowser(zeroconf, "_elgato._tcp.local.", listener)
    browser2 = ServiceBrowser(zeroconf, "_elg._tcp.local.", listener)

    time.sleep(timeout)
    zeroconf.close()


if __name__ == "__main__":
    main()
