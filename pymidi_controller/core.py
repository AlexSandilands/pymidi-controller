import threading
import sys
import select
import time
import subprocess
from mido import open_input
from pymidi_controller.utils.midi_utils import get_known_midi_input
from pymidi_controller.config import MIDI_BINDINGS, CLI_COMMAND

def format_midi_key(msg):
    if msg.type == "control_change":
        return f"{msg.type}:{msg.channel}:{msg.control}:{msg.value}"
    elif msg.type in ("note_on", "note_off"):
        return f"{msg.type}:{msg.channel}:{msg.note}:{msg.velocity}"
    return None

def handle_midi_message(msg, bindings):

    key = format_midi_key(msg)
    if key and key in bindings:
        command = [CLI_COMMAND] + bindings[key]
        print(f"🎯 Matched {key} → Running: {' '.join(command)}")
        try:
            subprocess.Popen(command)
        except Exception as e:
            print(f"❌ Failed to run command: {e}")
    elif key:
        print(f"🎵 Unmapped input: {key}")

def run_blocking(device_name, bindings):
    print("💤 Blocking mode: press Ctrl+C to exit.\n")
    with open_input(device_name) as inport:
        for msg in inport:
            handle_midi_message(msg, bindings)

def run_interactive(device_name, bindings):
    print("💡 Interactive mode: type 'quit' to exit.\n")
    stop_flag = threading.Event()

    def input_listener():
        while not stop_flag.is_set():
            if select.select([sys.stdin], [], [], 1)[0]:
                command = sys.stdin.readline().strip().lower()
                if command in ("quit", "exit", "q"):
                    stop_flag.set()

    input_thread = threading.Thread(target=input_listener, daemon=True)
    input_thread.start()

    with open_input(device_name) as inport:
        while not stop_flag.is_set():
            for msg in inport.iter_pending():
                handle_midi_message(msg, bindings)
            time.sleep(0.01)

    print("👋 Listener stopped.")

def run(mode: str = "blocking"):
    """
    Entry point for the long-running MIDI listener.
    mode: 'interactive' or 'blocking'
    """
    bindings = MIDI_BINDINGS
    if not bindings:
        print("❌ No MIDI bindings defined in config.yaml.")
        return

    device_name = get_known_midi_input()
    if not device_name:
        print("❌ No MIDI input devices found.")
        return

    print(f"🎹 Listening on: {device_name}")
    print(f"📖 Loaded {len(bindings)} mappings...")

    if mode == "blocking":
        run_blocking(device_name, bindings)
    else:
        run_interactive(device_name, bindings)


if __name__ == "__main__":
    run()
