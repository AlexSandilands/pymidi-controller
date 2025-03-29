# 🎛️ PyMIDI Controller

A Python CLI and background MIDI listener that lets you control Philips Hue groups and Elgato Ring Lights using a MIDI device (e.g. Rode StreamerX).

Built to run persistently on Linux using a `distrobox` container or systemd user service.

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

### 🧠 Hue

| Command                         | Description                                |
|--------------------------------|--------------------------------------------|
| `hue-discover`                 | Discover Hue Bridge and pair to get API key |
| `hue-groups-info`              | List all groups and their states           |
| `hue-group-toggle <group>`     | Toggle a group on/off                      |
| `hue-group-color <group> <color>` | Set color using name or hue value       |
| `hue-group-toggle-color <group>` | Toggle a group between red and blue    |
| `hue-lights-info`              | List all individual lights and effects     |
| `hue-schedules-info`           | List all schedules                         |
| `hue-schedule-toggle <name>`   | Toggle a schedule on/off                   |
| `hue-colorloop-toggle <group>` | Toggle colorloop effect                    |

---

### 💡 Elgato

| Command             | Description                                 |
|---------------------|---------------------------------------------|
| `elgato-discover`   | Discover Elgato lights via mDNS             |
| `elgato-toggle`     | Toggle Elgato Ring Light on/off             |
| `elgato-info`       | Show brightness, temperature, and power     |

---

### 🎹 MIDI

| Command                    | Description                                     |
|----------------------------|-------------------------------------------------|
| `midi-listen`              | Print incoming MIDI events (for manual mapping) |
| `midi-run [--mode MODE]`   | Start MIDI listener (`interactive` or `blocking`) |

---

## 🎛️ MIDI Mapping

### Bind a MIDI input to a CLI command:

Run the listener:

```bash
python3 cli.py midi-listen
```

Then press buttons on your MIDI controller to get keys like:

```
control_change channel=0 control=12 value=127 time=0
→ control_change:0:12:127
```

Edit `midi_bindings.json` like this:

```json
{
  "control_change:0:12:127": ["hue-group-toggle", "Group Name"],
  "control_change:0:13:127": ["elgato-toggle"],
  "control_change:0:14:127": ["hue-group-color", "Group Name", "red"]
}
```

Then run the listener:

```bash
python3 midi_run.py --mode interactive  # supports quit()
# or
python3 midi_run.py --mode blocking     # efficient for background running
```
---

## 🔐 Environment Setup (`.env`)

Create a `.env` file in the project root to store API keys and device IPs:

```env
# Hue Bridge
HUE_BRIDGE_IP=192.168.1.xxx
HUE_API_KEY=your-api-key-here

# Elgato Ring Light
ELGATO_LIGHT_IP=192.168.1.xxx
```

> 🧠 Use the commands `hue-discover` and `elgato-discover` to automatically generate this file!

---

### 🛠 Auto-generate `.env`

Run these commands to set things up (although make sure you create the .env template first):

```bash
python3 cli.py hue-discover
python3 cli.py elgato-discover
```

These will:
- Discover devices on your network
- Prompt you to save to `.env`
- Save IP and API key using `python-dotenv`

The app will then load `.env` automatically on startup.

---

## 🧠 MIDI Device Matching

The listener uses `midi_devices.json` to match known MIDI input names:

```json
{
  "known_devices": [
    "Streamer X",
    "nanoPAD",
    "APC Key 25"
  ]
}
```

It will auto-select the first known device found in `mido.get_input_names()`.

---

## 🛠 Running as a Startup Service

Coming soon — you can run `midi_run.py` on boot using:

- `.desktop` autostart launcher
- `systemd --user` unit (recommended for persistent background use)

---

## 📂 Project Structure

```
pymidi-controller/
├── actions/
│   ├── hue.py
│   ├── hue_discovery.py
│   ├── elgato.py
│   ├── elgato_discovery.py
│   ├── midi_utils.py
├── midi_run.py
├── cli.py
├── midi_bindings.json
├── midi_devices.json
├── .env
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
