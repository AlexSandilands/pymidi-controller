# 🎹 PyMIDI Controller

[![Python](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/AlexSandilands/pymidi-controller)](https://github.com/AlexSandilands/pymidi-controller/blob/main/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/AlexSandilands/pymidi-controller)](https://github.com/AlexSandilands/pymidi-controller/commits/main)

A lightweight Python CLI and background MIDI listener for controlling Philips Hue and Elgato Ring Lights via a MIDI device.

---

## 📚 Table of Contents

- [🚀 Installation](#-installation)
- [⚡ Quickstart](#-quickstart)
- [⚙️ Configuration](#️-configuration)
- [🎛️ Commands](#️-commands)
  - [Global](#global)
  - [Service](#service)
  - [Hue Commands](#hue-commands)
  - [Elgato Commands](#elgato-commands)
  - [MIDI Commands](#midi-commands)
  - [Custom Function Commands](#custom-function-commands)
- [🎹 MIDI Binding Guide](#-midi-binding-guide)
- [⚙️ Service (Optional)](#️-service-optional)

## 🚀 Installation

**Requirements:**

- Python 3.7 or higher
- A modern Linux distro (systemd)

### Via pip

```bash
pip install pymidi-controller
```

### Via pipx (isolated install)

```bash
pipx install pymidi-controller
```

> If you use `pipx`, make sure `~/.local/bin` is on your `PATH` (`pipx ensurepath`).

---

## ⚡ Quickstart

1. **Initialize your config** (creates `~/.config/pymidi-controller/config.yaml`):
   ```bash
   pymidi init
   ```
2. **Discover your Hue Bridge** (press the link button when prompted):
   ```bash
   pymidi hue discover
   ```
3. **Discover your Elgato Ring Light**:
   ```bash
   pymidi elgato discover
   ```
4. **Map MIDI inputs** (listen to your controller to grab event keys):
   ```bash
   pymidi midi listen
   ```
   Press buttons/knobs to print strings like `control_change:0:12:127` for use in your config.
5. **Edit your config** (see [Configuration](#️-configuration)) to add your device IPs, API keys, MIDI bindings, and color cycles.
6. **Start the listener to test configuration**:
   ```bash
   pymidi run --mode blocking
   ```
7. **(Optional) Background Service**:
  You can also install as a background service: see [Service](#️-service-optional).

---

## ⚙️ Configuration

All settings live in a single YAML file:

```
~/.config/pymidi-controller/config.yaml
```

This file will contain potentially sensitive data like your Hue API key or your IP address,
so it will be flagged as senstive and set so only your user can read it.

### Example `config.yaml`

```yaml
hue:
  bridge_ip: 192.168.1.42      # your Hue Bridge address
  api_key: YOUR_HUE_API_KEY    # obtained via `pymidi hue discover`

elgato:
  host: 192.168.1.43           # your Elgato Ring Light address

midi:
  devices:
    - "Streamer X"
    - "nanoPAD"

  # Map MIDI event keys → pymidi commands
  bindings:
    control_change:0:12:127:
      - hue
      - toggle-group
      - "Living Room"
    control_change:0:14:127:
      - elgato
      - toggle

  # Optional: define color cycles per group
  color_cycles:
    Living Room:
      - red
      - blue
      - green
```
---

## 🎛️ Commands

Use `pymidi <group> --help` for details on each context.

### Global

| Command                                        | Description                                 |
| ---------------------------------------------- | ------------------------------------------- |
| `pymidi init`                                  | Create default config file and function dir |
| `pymidi run [--mode interactive \| blocking]`  | Start the MIDI listener (`--mode blocking`) |

### Service

| Command                                      | Description                         |
| -------------------------------------------- | ----------------------------------- |
| `pymidi service --user install`               | Install & start as a user service   |
| `pymidi service --system install`             | Install & start system-wide service |
| `pymidi service --user uninstall`             | Stop & remove user service          |
| `pymidi service --system uninstall`           | Stop & remove system service        |
| `pymidi service --user\|--system stop`        | Stop the running service            |
| `pymidi service --user\|--system enable`      | Enable service                      |
| `pymidi service --user\|--system log`         | Tail service logs                   |

Every service subcommand requires a scope flag before the subcommand. Choose either `--user` or `--system` where the table shows `--user|--system`, for example `pymidi service --user stop`.

### Hue Commands

| Command                                                    | Description                              |
| ---------------------------------------------------------- | ---------------------------------------- |
| `pymidi hue discover`                                      | Find bridge & generate API key           |
| `pymidi hue list-groups`                                   | List all groups and on/off states        |
| `pymidi hue list-lights`                                   | List all lights and their state/effect   |
| `pymidi hue list-schedules`                                | List all schedules                       |
| `pymidi hue toggle-group <group>`                          | Toggle a group on/off                    |
| `pymidi hue set-color <group> <color> [--sat N] [--bri N]` | Set group color                          |
| `pymidi hue toggle-schedule <name>`                        | Enable/disable a schedule                |
| `pymidi hue loop [--effect colorloop \| none]`             | Toggle colorloop effect                  |
| `pymidi hue cycle-color <group>`                           | Cycle group color through `color_cycles` |

### Elgato Commands

| Command                  | Description                    |
| ------------------------ | ------------------------------ |
| `pymidi elgato discover` | Discover Ring Light via mDNS   |
| `pymidi elgato toggle`   | Toggle Ring Light on/off       |
| `pymidi elgato info`     | Show current Ring Light status |

### MIDI Commands

| Command              | Description                                |
| -------------------- | ------------------------------------------ |
| `pymidi midi listen` | Print incoming MIDI event keys for mapping |

### Custom Function Commands

| Command                                        | Description                                           |
| ---------------------------------------------- | ----------------------------------------------------- |
| `pymidi function list`                         | List all available custom functions                  |
| `pymidi function run <name> [args...]`         | Run a custom function by name with optional arguments |

---

## 🎹 MIDI Binding Guide

1. Run:
   ```bash
   pymidi midi listen
   ```
2. Press a control (button/knob) to see its event key, e.g. `control_change:0:12:127`.
3. Open `~/.config/pymidi-controller/config.yaml` and under `midi.bindings`, add:
   ```yaml
   bindings:
     control_change:0:12:127:
       - hue
       - toggle-group
       - "Living Room"
   ```
   Each value under the event key should be one part in order of the [Commands](#️-commands)
4. Save and test:
   ```bash
   pymidi run --mode interactive
   ```

---

## 📜 Custom User Functions

You can define your own Python functions to run on MIDI events. These live in:

```
~/.config/pymidi-controller/functions/
```

This directory is created by `pymidi init` and permissioned as `0700` (only accessible to your user).

### Supported Formats

#### Option 1: Single `.py` file

**Structure:**

```
functions/
└── my_function.py
```

**Content:**

Note, the function must have a main() function, and this will be the entry point.

```python
def main(*args):
    print("Hello from my_function", args)
```

#### Option 2: Package folder

You can also use a subfolder with either an `__init__.py` or a `main.py`:
These must have a main() function.

**Structure A:**

```
functions/
└── my_package/
    └── __init__.py
```

**Structure B:**

```
functions/
└── my_package/
    └── main.py
```

**Content:**

```python
def main(*args):
    print("Hello from package function", args)
```

Then bind it in your config:

```yaml
bindings:
  control_change:0:10:127:
    - custom
    - my_function
    - optional_arg1
    - optional_arg2
```

---

## ⚙️ Service (Optional)

To run automatically at login:

```bash
pymidi service --user install
```

The user service starts with your graphical session (`graphical-session.target`), after the desktop compositor is up. It does not pull that target in itself, so it can't make other autostart apps start early.

If your window manager doesn't start `graphical-session.target` (Plasma and GNOME do; some minimal setups such as i3, sway or Hyprland don't unless configured to), the service won't start at login. Start the target from your session startup, e.g. `systemctl --user start graphical-session.target`.

> **Upgrading from 0.3.0 or earlier?** Rerun `pymidi service --user install` (or `pymidi service --system install` for a system-wide install) once. It replaces the old unit and removes its stale `default.target` link. `pymidi service --user enable` alone doesn't refresh the unit file.

Logs:

```bash
pymidi service --user log
```

---

## 📜 License

MIT © Alex Sandilands
