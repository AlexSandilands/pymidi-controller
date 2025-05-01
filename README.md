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

| Command       | Description                                 |
| ------------- | ------------------------------------------- |
| `pymidi init` | Create default config file                  |
| `pymidi run`  | Start the MIDI listener (`--mode blocking`) |

### Service

| Command                             | Description                         |
| ----------------------------------- | ----------------------------------- |
| `pymidi service install --user`     | Install & start as a user service   |
| `pymidi service install --system`   | Install & start system-wide service |
| `pymidi service uninstall --user`   | Stop & remove user service          |
| `pymidi service uninstall --system` | Stop & remove system service        |
| `pymidi service stop`               | Stop the running service            |
| `pymidi service enable`             | Enable service (user scope)         |
| `pymidi service log`                | Tail service logs                   |

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

## ⚙️ Service (Optional)

To run automatically at login:

```bash
pymidi service install --user
```

Logs:

```bash
pymidi service log
```

---

## 📜 License

MIT © Alex Sandilands
