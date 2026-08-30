# HeatMeister for Home Assistant

A local Home Assistant custom integration for the **SDR Engineering HeatMeister** using its HTTP API. MQTT is not required.

## Features

- Local HTTP communication with `/getStatus` and `/setStatus`
- One Home Assistant device per HeatMeister
- Fan entity with native percentage support
- Dedicated **Fan speed** slider (0-100%)
- Dedicated **Fan mode** selector: Auto / Manual / Boost
- Boost switch
- Room temperature control switch
- Target temperature slider
- Ambient, inlet, outlet and delta temperature sensors
- Wi-Fi and runtime diagnostics
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

## Manual installation

Copy `custom_components/heatmeister` to the `custom_components` directory of your Home Assistant configuration and restart Home Assistant.

## Notes

Changing the dedicated Fan speed slider deliberately switches the HeatMeister to Manual mode and disables Boost.

## Repository structure

This repository follows the HACS integration layout: the integration is located at `custom_components/heatmeister`, while `hacs.json` and this README are at repository root.

## Support

Use the GitHub issue tracker: https://github.com/NLJackBlack/HA_CI_heatmeister/issues
