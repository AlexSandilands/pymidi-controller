from zeroconf import Zeroconf, ServiceBrowser, ServiceListener
from config import ENV_FILE
from dotenv import set_key
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

            save = input("💾 Save this IP to .env as ELGATO_LIGHT_IP? [y/N] ").strip().lower()
            if save == "y":
                set_key(str(ENV_FILE), "ELGATO_LIGHT_IP", ip)
                print(f"✅ Saved ELGATO_LIGHT_IP={ip} to .env")
            else:
                print("⚠️ Skipped saving IP to .env")


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
