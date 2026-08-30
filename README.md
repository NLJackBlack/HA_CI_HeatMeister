# HeatMeister Home Assistant Integration

Custom Home Assistant integration for SDR Engineering HeatMeister using its local HTTP API.

## Version

**0.2.8**

## Features

- Local `/getStatus` polling every 30 seconds
- Fan speed slider (0-100%)
- Fan mode selector: Auto / Manual / Boost
- Boost and room temperature control switches
- Target temperature control
- Temperature and diagnostic sensors
- Firmware version sensor without the leading `v`
- **New firmware available** binary sensor
- Checks SDR Engineering every **12 hours** for the latest firmware
- HACS-compatible repository structure

## Firmware update check

Every 12 hours the integration reads:

`https://www.sdr-engineering.nl/dl_firmware/heatbooster/latest/fwversion`

The returned version is compared with `FW_VERSION` from the local HeatMeister `/getStatus` response. A leading `v` is ignored for comparison.

The entity **New firmware available** is `on` only when the remote version is newer than the installed version. It also exposes `installed_version`, `latest_version`, and `check_interval_hours` attributes.

If the external endpoint cannot be reached, local HeatMeister functionality continues normally; only this binary sensor is temporarily unavailable.

## HACS installation

Add `https://github.com/NLJackBlack/HA_CI_HeatMeister` as a custom HACS repository of type **Integration**, install HeatMeister, restart Home Assistant, then add the integration from **Settings -> Devices & services**.

Version comparison uses only the numeric dotted value. For example, `v2.8.8`, `V2.8.8` and `2.8.8` are all treated as `2.8.8`.

## Firmware check behavior in 0.2.7

The firmware request sends explicit HTTP headers, including a browser-compatible
`User-Agent`, because the SDR Engineering endpoint may return HTTP 403 for
requests without an accepted user agent.

Firmware comparison uses only the numeric dotted version:

- `v2.8.8` -> `2.8.8`
- `V2.8.8` -> `2.8.8`
- `2.8.8` -> `2.8.8`

The `New firmware available` binary sensor exposes:

- `installed_version`
- `latest_version`
- `check_interval_hours`
- `firmware_check_status`
- `firmware_check_error` when the remote check fails

A failed external firmware check no longer forces the entity to become
`unavailable`. Its firmware state becomes unknown until a successful check,
while local HeatMeister functionality continues to work.

## Startup resilience in 0.2.8

Version 0.2.8 fixes the firmware coordinator startup error caused by a missing logger definition. The external firmware check is also isolated from local device setup, so a failure of the SDR Engineering endpoint cannot prevent the HeatMeister integration from starting.
