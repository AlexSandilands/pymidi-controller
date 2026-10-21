import os
import shutil
import subprocess
from pathlib import Path

import pytest

from pymidi_controller.utils import service_manager
from pymidi_controller.utils.service_manager import ServiceScope, render_system_unit

PY = "/opt/venv/bin/python"


def _exec_start_line(unit):
    return next(l for l in unit.splitlines() if l.startswith("ExecStart="))


def test_unit_runs_as_given_user_with_audio_group():
    unit = render_system_unit("alice", PY)
    assert "\nUser=alice\n" in unit
    assert "\nSupplementaryGroups=audio\n" in unit
    assert "@" not in unit


def test_unit_omits_audio_group_when_missing():
    unit = render_system_unit("alice", PY, audio_group=False)
    assert "SupplementaryGroups" not in unit
    assert "@SUPPLEMENTARY_GROUPS@" not in unit
    assert "\nUser=alice\nExecStart=" in unit


def test_exec_start_uses_absolute_interpreter():
    unit = render_system_unit("alice", PY)
    assert _exec_start_line(unit) == f"ExecStart={PY} -m pymidi_controller run --mode blocking"


def test_no_home_specifier_or_path_override():
    # %h is /root in the system manager, so it must not appear
    unit = render_system_unit("alice", PY)
    assert "%h" not in unit
    assert "Environment=PATH" not in unit


@pytest.mark.parametrize(
    "path, expected",
    [
        ("/home/a b/python", '"/home/a b/python"'),
        ("/home/50%/python", "/home/50%%/python"),
        ("/home/a b/50%/python", '"/home/a b/50%%/python"'),
        ("/home/a$b/python", "/home/a$b/python"),
    ],
)
def test_interpreter_path_is_escaped(path, expected):
    unit = render_system_unit("alice", path)
    assert _exec_start_line(unit) == f"ExecStart={expected} -m pymidi_controller run --mode blocking"


@pytest.mark.skipif(shutil.which("systemd-analyze") is None, reason="systemd-analyze not available")
@pytest.mark.parametrize("dirname", ["plain", "with space", "with%percent", "with space%and percent", "with$dollar", "with $dollar space"])
def test_systemd_resolves_the_rendered_interpreter(tmp_path, dirname):
    interpreter = tmp_path / dirname / "python"
    interpreter.parent.mkdir()
    interpreter.write_text("#!/bin/sh\n")
    interpreter.chmod(0o755)
    unit_file = tmp_path / "pymidi-controller.service"
    unit_file.write_text(render_system_unit("alice", str(interpreter)))
    out = subprocess.run(["systemd-analyze", "verify", str(unit_file)], capture_output=True, text=True)
    assert "not executable" not in out.stdout + out.stderr
    assert "quoting" not in (out.stdout + out.stderr).lower()


@pytest.mark.parametrize("path", ["/tmp/o'x/python", '/tmp/q"x/python', "/tmp/b\\s/python"])
def test_paths_systemd_cant_express_are_rejected(path):
    with pytest.raises(ValueError):
        render_system_unit("alice", path)


@pytest.mark.parametrize("path", ["/tmp/a\nExecStartPre=/bin/evil", "/tmp/a\rb"])
def test_control_characters_in_interpreter_path_are_rejected(path):
    with pytest.raises(ValueError):
        render_system_unit("alice", path)


@pytest.mark.parametrize("user", ["", "a b", "alice\n", "a\nUser=root", "50%", "-lead", "a/b"])
def test_unsupported_user_names_are_rejected(user):
    with pytest.raises(ValueError):
        render_system_unit(user, PY)


@pytest.mark.parametrize("user", ["alice", "pi", "_svc", "first.last", "name-1", "machine$"])
def test_ordinary_user_names_are_accepted(user):
    assert f"\nUser={user}\n" in render_system_unit(user, PY)


# ---- install / uninstall -------------------------------------------------

@pytest.fixture
def calls(monkeypatch):
    recorded = []
    monkeypatch.setattr(subprocess, "run", lambda cmd, **kw: recorded.append(cmd))
    return recorded


def _as_root(monkeypatch, tmp_path, sudo_user="alice"):
    monkeypatch.setattr(os, "geteuid", lambda: 0)
    monkeypatch.setattr(service_manager, "SYSTEM_UNIT_DIR", tmp_path / "system")
    monkeypatch.setattr(service_manager.sys, "executable", PY)
    monkeypatch.setattr(service_manager.pwd, "getpwnam", lambda name: type("P", (), {"pw_gid": 1000})())
    monkeypatch.setattr(service_manager, "_audio_group_exists", lambda: True)
    monkeypatch.setattr(service_manager, "_warn_audio_group", lambda user: None)
    if sudo_user is None:
        monkeypatch.delenv("SUDO_USER", raising=False)
    else:
        monkeypatch.setenv("SUDO_USER", sudo_user)


def test_system_install_writes_rendered_unit_and_restarts(monkeypatch, tmp_path, calls):
    _as_root(monkeypatch, tmp_path)
    service_manager.install(ServiceScope.SYSTEM)

    unit = (tmp_path / "system" / "pymidi-controller.service").read_text()
    assert unit == render_system_unit("alice", PY)
    # restart, not just enable --now, so a running old instance is replaced
    assert ["systemctl", "restart", "pymidi-controller.service"] in calls
    assert calls.index(["systemctl", "daemon-reload"]) < calls.index(["systemctl", "restart", "pymidi-controller.service"])


def test_system_install_omits_audio_group_line_when_group_missing(monkeypatch, tmp_path, calls):
    _as_root(monkeypatch, tmp_path)
    monkeypatch.setattr(service_manager, "_audio_group_exists", lambda: False)
    service_manager.install(ServiceScope.SYSTEM)
    assert "SupplementaryGroups" not in (tmp_path / "system" / "pymidi-controller.service").read_text()


def test_system_uninstall_removes_unit(monkeypatch, tmp_path, calls):
    _as_root(monkeypatch, tmp_path)
    service_manager.install(ServiceScope.SYSTEM)
    service_manager.uninstall(ServiceScope.SYSTEM)
    assert not (tmp_path / "system" / "pymidi-controller.service").exists()
    assert ["systemctl", "stop", "pymidi-controller.service"] in calls


def test_user_install_still_copies_unmodified_unit(monkeypatch, tmp_path, calls):
    monkeypatch.setenv("HOME", str(tmp_path))
    service_manager.install(ServiceScope.USER)
    dst = tmp_path / ".config/systemd/user/pymidi-controller.service"
    assert "graphical-session.target" in dst.read_text()
    assert "@" not in dst.read_text()
    assert ["systemctl", "--user", "restart", "pymidi-controller.service"] in calls


def test_system_install_refuses_non_root(monkeypatch):
    monkeypatch.setattr(os, "geteuid", lambda: 1000)
    with pytest.raises(SystemExit) as exc:
        service_manager.install(ServiceScope.SYSTEM)
    assert "must run as root" in str(exc.value)


def test_system_uninstall_refuses_non_root(monkeypatch):
    monkeypatch.setattr(os, "geteuid", lambda: 1000)
    with pytest.raises(SystemExit) as exc:
        service_manager.uninstall(ServiceScope.SYSTEM)
    assert "must run as root" in str(exc.value)


@pytest.mark.parametrize("sudo_user", [None, "root"])
def test_system_install_refuses_without_real_sudo_user(monkeypatch, tmp_path, sudo_user):
    _as_root(monkeypatch, tmp_path, sudo_user)
    with pytest.raises(SystemExit) as exc:
        service_manager.install(ServiceScope.SYSTEM)
    assert "which user" in str(exc.value)


def test_system_install_refuses_unknown_sudo_user(monkeypatch, tmp_path):
    _as_root(monkeypatch, tmp_path, "ghost")
    def missing(name):
        raise KeyError(name)
    monkeypatch.setattr(service_manager.pwd, "getpwnam", missing)
    with pytest.raises(SystemExit) as exc:
        service_manager.install(ServiceScope.SYSTEM)
    assert "isn't a known user" in str(exc.value)
