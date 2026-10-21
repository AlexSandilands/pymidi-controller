import subprocess
import sys

import mido

from pymidi_controller import core


def _press(bindings, monkeypatch):
    procs = []
    real_popen = subprocess.Popen

    def popen(cmd, **kwargs):
        proc = real_popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        procs.append((cmd, proc))
        return proc

    monkeypatch.setattr(core.subprocess, "Popen", popen)
    msg = mido.Message("control_change", channel=0, control=99, value=1)
    core.handle_midi_message(msg, bindings)
    return procs


def test_binding_runs_cli_through_current_interpreter(monkeypatch):
    procs = _press({"control_change:0:99:1": ["hue", "--help"]}, monkeypatch)
    [(cmd, _)] = procs
    assert cmd == [sys.executable, "-m", "pymidi_controller", "hue", "--help"]


def test_binding_runs_without_console_script_on_path(monkeypatch):
    # The system service's PATH has no ~/.local/bin, so the action must not
    # depend on finding the pymidi-controller script there
    monkeypatch.setenv("PATH", "/nonexistent")
    procs = _press({"control_change:0:99:1": ["--help"]}, monkeypatch)
    [(_, proc)] = procs
    out, _ = proc.communicate(timeout=30)
    assert proc.returncode == 0, out
    assert "usage:" in out
