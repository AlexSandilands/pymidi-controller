import grp
import os
import pwd
import shutil
import subprocess
import sys
from pathlib import Path
from importlib import resources
from enum import Enum, auto

# -------------------------------------------------------------------
# Service Installation & Management with Scoped Control
# -------------------------------------------------------------------

class ServiceScope(Enum):
    USER = auto()
    SYSTEM = auto()


def _exec_start_arg(path: str) -> str:
    """Escape a path for use as the executable in a unit's ExecStart=."""
    path = path.replace("%", "%%")
    if any(c.isspace() or c in '"\\' for c in path):
        path = '"' + path.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return path


def render_system_unit(user: str, python: str) -> str:
    """
    Render the system-wide unit for ``user``, running ``python -m pymidi_controller``.

    The absolute interpreter path means the unit doesn't depend on PATH, which the
    system manager doesn't set up for a user (pipx, venv and pip --user installs).
    """
    template = (resources.files("pymidi_controller") / "data/systemd/pymidi-controller.system.service").read_text(encoding="utf-8")
    exec_start = f"{_exec_start_arg(python)} -m pymidi_controller run --mode blocking"
    return template.replace("@USER@", user).replace("@EXEC_START@", exec_start)


def _require_root(action: str):
    """Exit with a clear message instead of a PermissionError traceback."""
    if os.geteuid() != 0:
        sys.exit(
            f"⚠️  `service --system {action}` must run as root. "
            'Use: sudo "$(command -v pymidi)" service --system ' + action
        )


def _invoking_user() -> str:
    """The user to run the system service as: whoever invoked sudo."""
    user = os.environ.get("SUDO_USER")
    if not user or user == "root":
        sys.exit(
            "⚠️  Can't tell which user the service should run as. Run this from your own "
            'account with sudo, e.g. sudo "$(command -v pymidi)" service --system install '
            "(running directly as root isn't supported)."
        )
    try:
        pwd.getpwnam(user)
    except KeyError:
        sys.exit(f"⚠️  SUDO_USER {user!r} isn't a known user.")
    return user


def _warn_audio_group(user: str):
    try:
        audio = grp.getgrnam("audio")
    except KeyError:
        print("⚠️  No 'audio' group on this system; the unit's SupplementaryGroups=audio will make the service fail to start.")
        return
    gids = os.getgrouplist(user, pwd.getpwnam(user).pw_gid)
    if audio.gr_gid not in gids:
        print(f"⚠️  {user} isn't in the 'audio' group. The service adds it itself, but `pymidi` run from a shell may not reach /dev/snd/seq (sudo usermod -aG audio {user}).")


def install(scope: ServiceScope):
    """
    Install and enable the systemd service unit.

    :param scope: ServiceScope.USER or ServiceScope.SYSTEM
    """
    unit_text = None
    if scope == ServiceScope.USER:
        target_dir = Path.home() / ".config/systemd/user"
        ctl = ["systemctl", "--user"]
        src_name = "pymidi-controller.service"
    elif scope == ServiceScope.SYSTEM:
        _require_root("install")
        user = _invoking_user()
        target_dir = Path("/etc/systemd/system")
        ctl = ["systemctl"]
        unit_text = render_system_unit(user, sys.executable)
    else:
        print("⚠️  Invalid scope for install.")
        return

    target_dir.mkdir(parents=True, exist_ok=True)
    dst = target_dir / "pymidi-controller.service"
    if unit_text is None:
        src = resources.files("pymidi_controller") / "data/systemd" / src_name
        shutil.copy(src, dst)
    else:
        dst.write_text(unit_text, encoding="utf-8")
    print(f"✔️  Installed service unit to {dst}")
    if unit_text is not None:
        print(f"   User={user}")
        print(f"   ExecStart={sys.executable} -m pymidi_controller run --mode blocking")
        _warn_audio_group(user)

    subprocess.run(ctl + ["daemon-reload"], check=True)
    # Drop links from older units (e.g. default.target.wants) before enabling
    subprocess.run(ctl + ["disable", "pymidi-controller.service"], check=False)
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
        _require_root("uninstall")
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
