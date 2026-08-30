# HeatMeister for Home Assistant

A local Home Assistant custom integration for the **SDR Engineering HeatMeister** using its HTTP API. MQTT is not required.

Current version: **0.2.3**

## Features

- Local HTTP communication with `/getStatus` and `/setStatus`
- One Home Assistant device per HeatMeister
- Dedicated **Fan speed** slider (0-100%)
- Dedicated **Fan mode** selector: Auto / Manual / Boost
- No separate binary-style Fan entity; fan control is handled by the slider and mode selector
- Boost switch
- Room temperature control switch
- Target temperature slider
- Ambient, inlet, outlet and delta temperature sensors
- **Firmware version** diagnostic sensor; values such as `v2.8.8` are shown as `2.8.8`
- Wi-Fi, runtime and system diagnostics
- Dutch and English setup flow
- Single coordinated status poll every 30 seconds

## Install with HACS

1. Open **HACS** in Home Assistant.
2. Open the menu and choose **Custom repositories**.
3. Add `https://github.com/NLJackBlack/HA_CI_heatmeister`.
4. Select category **Integration**.
5. Install **HeatMeister**.
6. Restart Home Assistant.
7. Go to **Settings -> Devices & services -> Add integration -> HeatMeister**.
8. Enter the local IP address or hostname of your HeatMeister.

Example: `192.168.68.116`.

## Controls

### Fan speed

The **Fan speed** entity is a 0-100% slider. Changing the slider deliberately sets `FAN_CONTROLMODE=1` (Manual), disables Boost and sends the selected `FAN_SPEED`.

### Fan mode

Use **Fan mode** to select:

- **Auto**
- **Manual**
- **Boost**

### Firmware version

The integration reads `FW_VERSION` from `/getStatus`. A leading `v` is removed for display, for example:

- API value: `v2.8.8`
- Home Assistant value: `2.8.8`

## Manual installation

Copy `custom_components/heatmeister` to the `custom_components` directory of your Home Assistant configuration and restart Home Assistant.

## Repository structure

This repository follows the HACS integration layout: the integration is located at `custom_components/heatmeister`, while `hacs.json`, the root README and changelog are located at repository root.

## Support

Use the GitHub issue tracker: https://github.com/NLJackBlack/HA_CI_heatmeister/issues
