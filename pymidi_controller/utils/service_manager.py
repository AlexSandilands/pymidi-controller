import shutil
import subprocess
from pathlib import Path
from importlib import resources
from enum import Enum, auto

# -------------------------------------------------------------------
# Service Installation & Management with Scoped Control
# -------------------------------------------------------------------

class ServiceScope(Enum):
    USER = auto()
    SYSTEM = auto()


def install(scope: ServiceScope):
    """
    Install and enable the systemd service unit.

    :param scope: ServiceScope.USER or ServiceScope.SYSTEM
    """
    if scope == ServiceScope.USER:
        target_dir = Path.home() / ".config/systemd/user"
        ctl = ["systemctl", "--user"]
    elif scope == ServiceScope.SYSTEM:
        target_dir = Path("/etc/systemd/system")
        ctl = ["systemctl"]
    else:
        print("⚠️  Invalid scope for install.")
        return

    target_dir.mkdir(parents=True, exist_ok=True)
    src = resources.files("pymidi_controller") / "data/systemd/pymidi-controller.service"
    dst = target_dir / "pymidi-controller.service"
    shutil.copy(src, dst)
    print(f"✔️  Installed service unit to {dst}")

    subprocess.run(ctl + ["daemon-reload"], check=True)
    subprocess.run(ctl + ["enable", "--now", "pymidi-controller.service"], check=True)
    print("✅ Service enabled and started.")


def uninstall(scope: ServiceScope):
    """
    Disable and remove the systemd service unit.

    :param scope: ServiceScope.USER or ServiceScope.SYSTEM
    """
    if scope == ServiceScope.USER:
        target_dir = Path.home() / ".config/systemd/user"
        ctl = ["systemctl", "--user"]
    elif scope == ServiceScope.SYSTEM:
        target_dir = Path("/etc/systemd/system")
        ctl = ["systemctl"]
    else:
        print("⚠️  Invalid scope for uninstall.")
        return

    service_name = "pymidi-controller.service"
    dst = target_dir / service_name

    subprocess.run(ctl + ["stop", service_name], check=False)
    subprocess.run(ctl + ["disable", service_name], check=False)

    if dst.exists():
        dst.unlink()
        print(f"🗑️  Removed service unit at {dst}")
    else:
        print(f"⚠️  No service unit found at {dst}")

    subprocess.run(ctl + ["daemon-reload"], check=True)
    print("✅ Service uninstalled.")


def stop(scope: ServiceScope = ServiceScope.USER):
    """
    Stop the systemd service.

    :param scope: ServiceScope.USER or ServiceScope.SYSTEM
    """
    cmd = ["systemctl"]
    if scope == ServiceScope.USER:
        cmd.insert(1, "--user")
    cmd.append("stop")
    cmd.append("pymidi-controller.service")
    subprocess.run(cmd, check=True)
    print("✅ Service stopped.")


def enable(scope: ServiceScope = ServiceScope.USER):
    """
    Enable the systemd service.

    :param scope: ServiceScope.USER or ServiceScope.SYSTEM
    """
    cmd = ["systemctl"]
    if scope == ServiceScope.USER:
        cmd.insert(1, "--user")
    cmd.extend(["enable", "pymidi-controller.service"])
    subprocess.run(cmd, check=True)
    print("✅ Service enabled.")


def log(scope: ServiceScope = ServiceScope.USER):
    """
    Show the systemd service logs.

    :param scope: ServiceScope.USER or ServiceScope.SYSTEM
    """
    cmd = ["journalctl"]
    if scope == ServiceScope.USER:
        cmd.extend(["--user"])
    cmd.extend(["-u", "pymidi-controller.service", "--no-pager"])
    subprocess.run(cmd, check=True)
    print("✅ Service logs displayed.")


def dispatch(action: str, scope: ServiceScope = ServiceScope.USER):
    """
    Dispatcher for service subcommands.

    :param action: one of 'install', 'uninstall', 'stop', 'enable', 'log'
    :param scope: ServiceScope.USER or ServiceScope.SYSTEM
    """
    if action == "install":
        install(scope)
    elif action == "uninstall":
        uninstall(scope)
    elif action == "stop":
        stop(scope)
    elif action == "enable":
        enable(scope)
    elif action == "log":
        log(scope)
    else:
        print(f"⚠️  Unknown service action: {action}")
