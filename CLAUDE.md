# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Persistent Memory

Conversation context is stored across sessions in:
```
C:\Users\julie\.claude\projects\C--Development-irrigation\memory\
```

**At the start of every session:** read `MEMORY.md` (the index) and any memory files relevant to the current task.

**During and at the end of every session:** save anything non-obvious that a future session would need — decisions made, bugs found, hardware quirks, user preferences, open items. Use these four types:

| Type | What to save |
|---|---|
| `project` | Goals, decisions, open bugs, deployment incidents |
| `user` | Preferences, workflow, things to avoid or repeat |
| `feedback` | Corrections or confirmed approaches the user gave |
| `reference` | Where to find things (dashboards, external docs) |

Each memory lives in its own `.md` file with YAML frontmatter (`name`, `description`, `metadata.type`) and a body that leads with the fact, then **Why:** and **How to apply:** lines. Add a pointer line to `MEMORY.md` for every new file.

Do **not** save: code patterns, file structure, git history, or anything already in this CLAUDE.md.

## Project Overview

A Raspberry Pi-based automated irrigation system. The main script runs on a Pi, reads soil moisture via an MCP3008 ADC over SPI, and controls a pump via a GPIO relay. It reports state and accepts manual commands through an MQTT broker (Home Assistant at `homeassistant.local`).

## Deployment

Credentials are **never stored in source** — `watering_system_prod.py` uses the placeholders `<username>` and `<password>`. The deployment script injects real credentials at deploy time.

```powershell
# Deploy to Raspberry Pi (injects credentials, SCP, restarts systemd service)
.\deploy.ps1
```

`deploy.ps1` reads credentials from `C:\Users\julie\OneDrive\Leisure\Irrigation\Mosquitto MQTT\credentials.json`, creates a temp copy with real values, SCPs it to `vill@192.168.1.112:/home/vill/Desktop/watering_system_prod.py`, then restarts the `irrigation` systemd service.

To check service status manually:
```bash
ssh vill@192.168.1.112 "sudo systemctl status irrigation --no-pager -l"
```

To tail logs on the Pi:
```bash
ssh vill@192.168.1.112 "tail -f /home/vill/Desktop/watering_system_prod.log"
```

## Architecture

### Hardware

- **MCP3008** ADC chip reads the analog capacitive moisture sensor on CH0 via SPI bus 0, device 0 at 1.35 MHz
- **GPIO pin 26 (BCM)** drives the pump relay — a 1-second HIGH pulse triggers one pump activation
- Wetness is calibrated by two fixed raw ADC values: `RAW_DRY=920` (sensor in air) and `RAW_WET=90` (sensor in water), linearly interpolated to 0.0–1.0

### Main Loop Logic (`watering_system_prod.py`)

- **Every 15 minutes**: reads moisture, publishes to `watering/soil/moisture` (retained)
- **Every 3 hours, if wetness < 0.45**: runs `pump_cycle()` — three pump pulses spaced 310 seconds apart
- **Subscribes** to `watering/soil/pumpmanual` for manual pump commands (received and logged, not yet acted upon beyond logging)
- **Publishes** to `watering/soil/pump` with payload `"1"` on each pump activation

### MQTT Topics

| Topic | Direction | Purpose |
|---|---|---|
| `watering/soil/moisture` | publish (retained) | Current soil wetness % |
| `watering/soil/pump` | publish | Pump activation event |
| `watering/soil/pumpmanual` | subscribe | Manual pump trigger from Home Assistant |

### Debug Scripts (`debug/`)

Run directly on the Pi to test individual subsystems:
- `moisture_sensor.py` — continuous SPI/ADC moisture readings to stdout
- `gpio_test.py` — single ON/OFF pulse on GPIO 26 to verify relay wiring
- `mosquitto_test_send.py` — publishes random values to `watering/soil/moisturetest`
- `mosquitto_test_receive.py` — subscribes to `test/villberry` and prints received messages

These scripts also use `<username>`/`<password>` placeholders; substitute real credentials before running on the Pi.
