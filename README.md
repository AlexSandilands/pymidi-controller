# 🎛️ PyMIDI Controller

[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/AlexSandilands/pymidi-controller)](https://github.com/AlexSandilands/pymidi-controller/blob/main/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/AlexSandilands/pymidi-controller)](https://github.com/AlexSandilands/pymidi-controller/commits/main)

A Python CLI and background MIDI listener that lets you control Philips Hue groups and Elgato Ring Lights using a MIDI device.

Built to run persistently on Linux using a `distrobox` container or systemd user service.

---

## 📚 Table of Contents

- [📦 Features](#-features)
- [🚀 Commands](#-commands)
  - [🌈 Hue](#-hue)
  - [💡 Elgato](#-elgato)
  - [🎹 MIDI](#-midi)
- [🧑‍💻 User Settings](#-user-settings)
- [🎛️ MIDI Mapping](#️-midi-mapping)
- [🔐 Environment Setup (.env)](#-environment-setup-env)
- [🚀 Background Service Setup (Optional)](#-background-service-setup-optional-recommended)
- [📂 Project Structure](#-project-structure)
- [✅ Requirements](#-requirements)
- [📋 TODO](#-todo)

---

## 📦 Features

- 🔆 Control **Hue groups**: toggle, color set, effect, schedule
- 💡 Control **Elgato Ring Light**: toggle, discover via mDNS
- 🎹 Listen to **MIDI input** and trigger CLI commands
- 🎛️ Map any button to any command via `midi_bindings.json`
- 🧠 Run in either **interactive** or **blocking** mode
- 🧽 Simple, customizable architecture (no external frameworks)

---

## 🚀 Commands

### 🌈 Hue

| Command                            | Description                                    |
|------------------------------------|------------------------------------------------|
| `hue-discover`                     | Discover Hue Bridge and pair to get API key    |
| `hue-groups-info`                  | List all groups and their states               |
| `hue-group-color <group> <color>`  | Set color using name or hue value              |
| `hue-group-color-cycle <group>`    | Cycles a group color between configured colors |
| `hue-group-toggle <group>`         | Toggle a group on/off                          |
| `hue-group-toggle-redblue <group>` | Toggle a group between red and blue            |
| `hue-lights-info`                  | List all individual lights and effects         |
| `hue-schedules-info`               | List all schedules                             |
| `hue-schedule-toggle <name>`       | Toggle a schedule on/off                       |
| `hue-colorloop-toggle <group>`     | Toggle colorloop effect                        |

---

### 💡 Elgato

| Command             | Description                                 |
|---------------------|---------------------------------------------|
| `elgato-discover`   | Discover Elgato lights via mDNS             |
| `elgato-toggle`     | Toggle Elgato Ring Light on/off             |
| `elgato-info`       | Show brightness, temperature, and power     |

---

### 🎹 MIDI

| Command                    | Description                                        |
|----------------------------|----------------------------------------------------|
| `midi-listen`              | Print incoming MIDI events (for manual mapping)    |
| `midi-run [--mode MODE]`   | Start MIDI listener (`interactive` or `blocking`)  |

---

## 🧑‍💻 User Settings

All user-specific configuration files are stored in the `user_settings/` folder. These define how your MIDI device behaves, what colors to cycle through, and how devices are identified.

You can safely version or ignore these files. Here's what each one does:

---

### 🎨 `color_cycles.json`

Used by `hue-group-color-cycle` to define the color loop for each group:

```json
{
  "YOUR GROUP": ["red", "blue", "green", "purple"],
}
```

If a group is missing from this file, it will default to: `["red", "blue"]`.

---

### 🎚 `midi_bindings.json`

Defines what each MIDI control triggers.  
See [🎛️ MIDI Mapping](#️-midi-mapping) for how to generate these values.

```json
{
  "control_change:0:1:127": ["hue-group-toggle", "YOUR GROUP"],
  "control_change:0:2:127": ["hue-group-cycle-color", "YOUR GROUP"],
  "control_change:0:3:127": ["elgato-toggle"]
}
```

Each array is a CLI command split into arguments, e.g. `["command", "arg1", "arg2"]`.

---

### 🎛 `midi_devices.json`

Used to define known MIDI device names so the listener can auto-connect:

```json
{
  "known_devices": [
    "Streamer X",
    "nanoPAD",
    "APC Key 25",
    "MIDI Fighter"
  ]
}
```

It will auto-select the first known device found in `mido.get_input_names()`.

---

## 🎛️ MIDI Mapping

### Bind a MIDI input to a CLI command:

Run the listener:

```bash
make listen
# or
python3 cli.py midi-listen
```

Then press buttons on your MIDI controller to get keys like:

```
control_change channel=0 control=12 value=127 time=0
→ control_change:0:12:127
```

Edit `./user_settings/midi_bindings.json` with your mappings.

Then run the app to test the command:

```bash
make run-dev
# or through python directly:

python3 pymidi.py --mode interactive  # supports quit()
python3 pymidi.py --mode blocking     # efficient for background running
```

---

## 🔐 Environment Setup (.env)

Create a `.env` file in `./user_settings/` to store API keys and device IPs:

```env
# Hue Bridge
HUE_BRIDGE_IP=192.168.1.xxx
HUE_API_KEY=your-api-key-here

# Elgato Ring Light
ELGATO_LIGHT_IP=192.168.1.xxx
```

> 🧠 Use the commands `hue-discover` and `elgato-discover` to automatically populate this file!

---

### 🛠 Auto-populate `.env`

Run these commands to set things up (although make sure you create the `.env` template first):

```bash
make setup
# or through python directly, separately:

python3 cli.py hue-discover
python3 cli.py elgato-discover
```

These will:
- Discover devices on your network
- Prompt you to save to `.env`
- Save IP and API key using `python-dotenv`

The app will then load `.env` automatically on startup.

---

## 🚀 Background Service Setup (Optional, Recommended)

To make PyMIDI start automatically at login and listen in the background, you can set up a `systemd` user service.

This step is **optional**, but highly recommended for full automation.

---

### 🐧 Step 1: (Optional) Create a Distrobox Container

If you're using an **immutable distro** (like Bazzite or Fedora Silverblue), you’ll want to run PyMIDI inside a containerized development environment:

```bash
distrobox create --name pymidi --image fedora:latest
distrobox enter pymidi
```

Inside the container:

```bash
# Optional: install dependencies
sudo dnf install python3 git gcc alsa-lib-devel

# Clone or mount your repo, or use `make install` from host after setting up the config (make setup, make listen)
```

PyMIDI will run from this container when the system service starts.

---

### 🔧 Step 2: Create the systemd User Service

Create this file:

```bash
mkdir -p ~/.config/systemd/user
vim ~/.config/systemd/user/pymidi.service
```

Paste the following:

```ini
[Unit]
Description=🎛️ PyMIDI Listener (via Distrobox)
After=graphical.target

[Service]
Type=simple
ExecStart=/usr/bin/distrobox enter pymidi -- /usr/bin/python3 /home/YOUR_USERNAME/.local/share/pymidi-controller/pymidi.py --mode blocking
Restart=on-failure
Environment=DISPLAY=:0
Environment=PATH=/usr/local/bin:/usr/bin:/bin
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

> 📝 Replace `/home/YOUR_USERNAME/...` with your actual home directory path.

---

### ✅ Step 3: Enable and Start the Service

Run the following from your **host terminal**:

```bash
systemctl --user daemon-reexec
systemctl --user daemon-reload
systemctl --user enable --now pymidi.service
```

Check status:

```bash
systemctl --user status pymidi.service
```

---

### 🧠 Optional: Enable Linger (Start Without Logging In)

If you want the MIDI service to run even before you've logged in to your desktop:

```bash
loginctl enable-linger $USER
```

This ensures your `systemd --user` services start at system boot.

---

## 📂 Project Structure

```
pymidi-controller/
├── actions/
│   ├── elgato_discovery.py
│   ├── elgato.py
│   ├── hue_discovery.py
│   ├── hue_state.py
│   ├── hue.py
├── user_settings/
│   ├── .env
│   ├── color_cycles.json
│   ├── midi_bindings.json
│   ├── midi_devices.json
├── utils/
│   ├── color_cycle.py
│   ├── midi_utils.py
├── pymidi.py
├── cli.py
└── requirements.txt
```

---

## ✅ Requirements

- Python 3.12+
- `mido`, `python-rtmidi`, `requests`, `zeroconf`, `python-dotenv`
- Alsa / RtMidi build deps

Install dependencies with:

```bash
pip install -r requirements.txt
```

## 📋 TODO

- 🎚️ Adding a GUI or system tray app
- ✈️ Adding application launcher commands
- 🔄 Adding OBS scene switching commands
- 🐍 Publishing to PyPI
- 🧪 Adding tests / GitHub Actions
- 📦 Turning this into a plug-and-play installer