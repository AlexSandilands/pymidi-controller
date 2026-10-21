import os

import pytest

from pymidi_controller.utils import service_manager
from pymidi_controller.utils.service_manager import render_system_unit


def test_placeholders_are_filled():
    unit = render_system_unit("alice", "/opt/venv/bin/python")
    assert "@" not in unit


def test_runs_as_given_user_not_root():
    unit = render_system_unit("alice", "/opt/venv/bin/python")
    assert "\nUser=alice\n" in unit
    assert "\nSupplementaryGroups=audio\n" in unit


def test_exec_start_uses_absolute_interpreter():
    unit = render_system_unit("alice", "/opt/venv/bin/python")
    assert "\nExecStart=/opt/venv/bin/python -m pymidi_controller run --mode blocking\n" in unit


def test_no_home_specifier_or_path_override():
    # %h is /root in the system manager, so it must not appear
    unit = render_system_unit("alice", "/opt/venv/bin/python")
    assert "%h" not in unit
    assert "Environment=PATH" not in unit


def test_interpreter_path_with_space_and_percent_is_escaped():
    unit = render_system_unit("alice", "/home/a b/50%/python")
    assert '\nExecStart="/home/a b/50%%/python" -m pymidi_controller run' in unit


def test_system_install_refuses_non_root(monkeypatch):
    monkeypatch.setattr(os, "geteuid", lambda: 1000)
    with pytest.raises(SystemExit) as exc:
        service_manager.install(service_manager.ServiceScope.SYSTEM)
    assert "must run as root" in str(exc.value)


def test_system_uninstall_refuses_non_root(monkeypatch):
    monkeypatch.setattr(os, "geteuid", lambda: 1000)
    with pytest.raises(SystemExit):
        service_manager.uninstall(service_manager.ServiceScope.SYSTEM)


@pytest.mark.parametrize("sudo_user", [None, "root"])
def test_system_install_refuses_without_real_sudo_user(monkeypatch, sudo_user):
    monkeypatch.setattr(os, "geteuid", lambda: 0)
    if sudo_user is None:
        monkeypatch.delenv("SUDO_USER", raising=False)
    else:
        monkeypatch.setenv("SUDO_USER", sudo_user)
    with pytest.raises(SystemExit) as exc:
        service_manager.install(service_manager.ServiceScope.SYSTEM)
    assert "which user" in str(exc.value)
