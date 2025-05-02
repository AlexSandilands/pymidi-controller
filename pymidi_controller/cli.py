"""
pymidi_controller CLI entry point
"""
import argparse
import sys

from pymidi_controller.actions import hue_discovery
from pymidi_controller.actions import hue as hue_module
from pymidi_controller.actions import elgato_discovery, elgato as elgato_module

from pymidi_controller.utils.config_manager import init_config
from pymidi_controller.utils.service_manager import dispatch as service_dispatch, ServiceScope
from pymidi_controller.utils.midi_utils import listen as midi_listen


def main():
    parser = argparse.ArgumentParser(prog="pymidi", description="MIDI Controller CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ----------------------------------------------------------------
    # Initialisation
    # ----------------------------------------------------------------
    subparsers.add_parser("init", help="Bootstrap ~/.config/pymidi-controller/config.yaml")

    # ----------------------------------------------------------------
    # Run the MIDI listener
    # ----------------------------------------------------------------
    run_p = subparsers.add_parser("run", help="Start the MIDI listener")
    run_p.add_argument("--mode", choices=["interactive","blocking"], default="blocking", help="Listener mode")

    # ----------------------------------------------------------------
    # Service Commands
    # ----------------------------------------------------------------
    svc = subparsers.add_parser("service", help="Install or manage the systemd service")
    scope_grp = svc.add_mutually_exclusive_group(required=True)
    scope_grp.add_argument("--user",   action="store_true", help="Operate on the current user's service (~/.config/systemd/user)")
    scope_grp.add_argument("--system", action="store_true", help="Operate on the system service (/etc/systemd/system)")
    svc_sub = svc.add_subparsers(dest="svc_cmd", required=True)

    # install
    svc_sub.add_parser("install",   help="Install and enable the service unit")

    # uninstall
    svc_sub.add_parser("uninstall", help="Disable and remove the service unit")

    # stop, enable, log
    svc_sub.add_parser("stop",   help="Stop the service")
    svc_sub.add_parser("enable", help="Enable the service")
    svc_sub.add_parser("log",    help="Show service logs")

    # ----------------------------------------------------------------
    # Custom Function Commands
    # ----------------------------------------------------------------
    func = subparsers.add_parser("function", help="Custom function management")
    func_sub = func.add_subparsers(dest="func_cmd", required=True)
    func_sub.add_parser("list", help="List available custom functions")
    # Run a custom function
    run_func = func_sub.add_parser("run", help="Run a custom function")
    run_func.add_argument("name", help="Name of the custom function to run")
    run_func.add_argument("args", nargs=argparse.REMAINDER, help="Arguments to pass to the function")

    # ----------------------------------------------------------------
    # Hue Commands
    # ----------------------------------------------------------------
    hue = subparsers.add_parser("hue", help="Hue bridge and lights management")
    hue_sub = hue.add_subparsers(dest="hue_cmd", required=True)
    hue_sub.add_parser("discover", help="Discover Hue Bridge and generate API key")
    hue_sub.add_parser("list-groups", help="List Hue groups and their states")
    hue_sub.add_parser("list-lights", help="List Hue lights and their states")
    hue_sub.add_parser("list-schedules", help="List Hue schedules")
    tg = hue_sub.add_parser("toggle-group", help="Toggle a Hue group on/off")
    tg.add_argument("group", help="Hue group name")
    sc = hue_sub.add_parser("set-color", help="Set a Hue group color")
    sc.add_argument("group", help="Hue group name")
    sc.add_argument("color", help="Named color or hue value")
    sc.add_argument("--sat", type=int, default=254)
    sc.add_argument("--bri", type=int, default=254)
    ts = hue_sub.add_parser("toggle-schedule", help="Toggle a Hue schedule on/off")
    ts.add_argument("schedule", help="Schedule name")
    lp = hue_sub.add_parser("loop", help="Toggle colorloop effect for a group")
    lp.add_argument("group", help="Hue group name")
    lp.add_argument("--effect", choices=["colorloop","none"], default=None)
    cc = hue_sub.add_parser("cycle-color", help="Cycle a group's color through the configured cycle")
    cc.add_argument("group", help="Hue group name")

    # ----------------------------------------------------------------
    # Elgato Commands
    # ----------------------------------------------------------------
    elg = subparsers.add_parser("elgato", help="Elgato Ring Light controls")
    elg_sub = elg.add_subparsers(dest="elgato_cmd", required=True)
    elg_sub.add_parser("discover", help="Discover Elgato Ring Light via mDNS")
    elg_sub.add_parser("toggle", help="Toggle Elgato Ring Light power")
    elg_sub.add_parser("info", help="Get Elgato Ring Light status")

    # ----------------------------------------------------------------
    # MIDI Commands
    # ----------------------------------------------------------------
    midi = subparsers.add_parser("midi", help="MIDI utilities")
    midi_sub = midi.add_subparsers(dest="midi_cmd", required=True)
    midi_sub.add_parser("listen", help="Listens for MIDI inputs and prints values")

    args = parser.parse_args()

    # ----------------------------------------------------------------
    # Dispatch commands
    # ----------------------------------------------------------------
    if args.command == "init":
        init_config()
        sys.exit(0)

    if args.command == "run":
        from pymidi_controller.core import run as core_run
        core_run(mode=args.mode)
        sys.exit(0)

    if args.command == "function":
        if args.func_cmd == "list":
            from pymidi_controller.utils.function_manager import list_functions
            list_functions()
        elif args.func_cmd == "run":
            from pymidi_controller.utils.function_manager import load_user_function
            func = load_user_function(args.name)
            func(*args.args)
        sys.exit(0)

    if args.command == "service":
        scope = ServiceScope.USER if getattr(args, "user", False) else ServiceScope.SYSTEM
        service_dispatch(args.svc_cmd, scope)
        sys.exit(0)

    if args.command == "hue":
        cmd = args.hue_cmd
        if cmd == "discover":
            hue_discovery.main()
        elif cmd == "list-groups":
            hue_module.list_groups()
        elif cmd == "list-lights":
            hue_module.list_lights()
        elif cmd == "list-schedules":
            hue_module.list_schedules()
        elif cmd == "toggle-group":
            hue_module.toggle_group(args.group)
        elif cmd == "set-color":
            val = int(args.color) if args.color.isdigit() else args.color
            hue_module.set_group_color(args.group, val, args.sat, args.bri)
        elif cmd == "toggle-schedule":
            hue_module.toggle_schedule(args.schedule)
        elif cmd == "loop":
            hue_module.toggle_colorloop(args.group, args.effect)
        elif cmd == "cycle-color":
            hue_module.cycle_group_color(args.group)
        sys.exit(0)

    if args.command == "elgato":
        cmd = args.elgato_cmd
        if cmd == "discover":
            elgato_discovery.main()
        elif cmd == "toggle":
            elgato_module.toggle_light()
        elif cmd == "info":
            elgato_module.get_ring_info()
        sys.exit(0)

    if args.command == "midi":
        if args.midi_cmd == "listen":
            midi_listen()
        sys.exit(0)
