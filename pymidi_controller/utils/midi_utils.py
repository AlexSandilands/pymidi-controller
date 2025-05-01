import mido
import threading
import sys
import select
import time
from mido import get_input_names
from pymidi_controller.config import MIDI_DEVICES

def get_known_midi_input():
    input_ports = get_input_names()

    if not input_ports:
        return None

    for name in MIDI_DEVICES:
        match = next((p for p in input_ports if name.lower() in p.lower()), None)
        if match:
            return match

    # Fallback
        return input_ports[0]
    

def listen():
    device_name = get_known_midi_input()

    if not device_name:
        print("❌ No MIDI input device found.")
        return

    print(f"🎧 Listening on {device_name}...\nPress buttons on your StreamerX!")
    print("💡 Type 'quit' and press Enter to exit.\n")

    stop_flag = threading.Event()

    def input_listener():
        while not stop_flag.is_set():
            # Wait up to 1 second for user input
            if select.select([sys.stdin], [], [], 1)[0]:
                command = sys.stdin.readline().strip().lower()
                if command in ("quit", "exit", "q"):
                    stop_flag.set()

    input_thread = threading.Thread(target=input_listener, daemon=True)
    input_thread.start()

    try:
        with mido.open_input(device_name) as port:
            while not stop_flag.is_set():
                for msg in port.iter_pending():
                    key = f"{msg.type}:{msg.channel}:{getattr(msg, 'control', msg.control)}:{getattr(msg, 'value', msg.value)}"
                    print(f"{msg} → {key}")
            time.sleep(0.01)
    except IOError:
        print(f"❌ Could not open MIDI input: {device_name}")

    print("👋 Listener stopped.")

if __name__ == "__main__":
    listen()