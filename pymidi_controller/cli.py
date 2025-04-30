import argparse
from pymidi_controller.actions import hue, hue_discovery, elgato, elgato_discovery
from pymidi_controller.utils import midi_utils
from pymidi_controller.config_manager import init_config

def main():
    parser = argparse.ArgumentParser(description="🎹 Python MIDI :: Controller CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ----------------------------------------------------------------
    # Initialisation
    # ----------------------------------------------------------------
    subparsers.add_parser("init", help="Bootstrap ~/.config/pymidi-controller/config.yaml")

    # ----------------------------------------------------------------
    # Application
    # ----------------------------------------------------------------
    run = subparsers.add_parser("run", help="Start the MIDI listener as a long-running process")
    run.add_argument("--mode", choices=["interactive", "blocking"], default="blocking", help="Listener mode (blocking is best for a service)")

    # ----------------------------------------------------------------
    # HUE: Discovery
    # ----------------------------------------------------------------
    subparsers.add_parser("hue-discover", help="Discover Hue Bridge and generate API key")

    # ----------------------------------------------------------------
    # HUE: Group Controls
    # ----------------------------------------------------------------
    group_toggle = subparsers.add_parser("hue-group-toggle", help="Toggle a Hue group on/off")
    group_toggle.add_argument("group", help="Hue group name")

    group_color = subparsers.add_parser("hue-group-color", help="Set a Hue group's color")
    group_color.add_argument("group", help="Hue group name")
    group_color.add_argument("color", help="Named color or hue value (0-65535)")
    group_color.add_argument("--sat", type=int, default=254, help="Saturation (0-254)")
    group_color.add_argument("--bri", type=int, default=254, help="Brightness (0-254)")

    # ----------------------------------------------------------------
    # HUE: Info
    # ----------------------------------------------------------------
    subparsers.add_parser("hue-groups-info", help="List all Hue groups and their states")
    subparsers.add_parser("hue-lights-info", help="List all Hue lights and their states")
    subparsers.add_parser("hue-schedules-info", help="List all Hue schedules")

    # ----------------------------------------------------------------
    # HUE: Effect + Schedule Controls
    # ----------------------------------------------------------------
    sched_toggle = subparsers.add_parser("hue-schedule-toggle", help="Toggle a Hue schedule on/off")
    sched_toggle.add_argument("schedule", help="Schedule name")

    colorloop = subparsers.add_parser("hue-colorloop-toggle", help="Toggle colorloop effect for a group")
    colorloop.add_argument("group", help="Hue group name")
    colorloop.add_argument("--effect", default="", help="Set a specific effect (colorloop, none)")

    color_toggle = subparsers.add_parser("hue-group-toggle-redblue", help="Toggle a group's color between red and blue")
    color_toggle.add_argument("group", help="Hue group name")

    color_cycle = subparsers.add_parser("hue-group-color-cycle", help="Cycles a group's color through the colors provided in user_settings/color_cycles.json")
    color_cycle.add_argument("group", help="Hue group name")

    # ----------------------------------------------------------------
    # ELGATO: Discovery + Controls
    # ----------------------------------------------------------------
    subparsers.add_parser("elgato-discover", help="Discover Elgato Ring Light via mDNS")
    subparsers.add_parser("elgato-toggle", help="Toggle Elgato Ring Light power")
    subparsers.add_parser("elgato-info", help="Get Elgato Ring Light status")

    # ----------------------------------------------------------------
    # MIDI: Utils
    # ----------------------------------------------------------------
    subparsers.add_parser("midi-listen", help="Listens for midi inputs and prints the values so they can be bound")

    # ----------------------------------------------------------------
    # Command Handlers
    # ----------------------------------------------------------------
    args = parser.parse_args()


    # Initialise config
    if args.command == "init":
        init_config()

    # Application run
    elif args.command == "run":
        from pymidi_controller.core import run as core_run
        core_run(mode=args.mode)

    # Hue discovery
    elif args.command == "hue-discover":
        hue_discovery.main()

    # Hue group controls
    elif args.command == "hue-group-toggle":
        hue.toggle_group(args.group)
    elif args.command == "hue-group-toggle-redblue":
        hue.toggle_red_blue(args.group)
    elif args.command == "hue-group-color":
        try:
            hue_val = int(args.color)
        except ValueError:
            hue_val = args.color
        hue.set_group_color(args.group, hue_val, args.sat, args.bri)
    elif args.command == "hue-group-color-cycle":
        hue.cycle_group_color(args.group)

    # Hue info
    elif args.command == "hue-groups-info":
        hue.list_groups()
    elif args.command == "hue-lights-info":
        hue.list_lights()
    elif args.command == "hue-schedules-info":
        hue.list_schedules()

    # Hue effects/schedules
    elif args.command == "hue-schedule-toggle":
        hue.toggle_schedule(args.schedule)
    elif args.command == "hue-colorloop-toggle":
        hue.toggle_colorloop(args.group, args.effect)

    # Elgato discovery + control
    elif args.command == "elgato-discover":
        elgato_discovery.main()
    elif args.command == "elgato-toggle":
        elgato.toggle_light()
    elif args.command == "elgato-info":
        elgato.get_ring_info()

    # MIDI utils
    elif args.command == "midi-listen":
        midi_utils.listen()

if __name__ == "__main__":
    main()
