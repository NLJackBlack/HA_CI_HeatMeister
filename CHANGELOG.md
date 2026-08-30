# Changelog

## 0.2.8

- Fixed startup failure caused by `_LOGGER` not being defined in `firmware.py`.
- Added the missing Python `logging` setup for the firmware coordinator.
- Updated the firmware request User-Agent to 0.2.8.
- Made the initial external firmware check defensive so it can never prevent the local HeatMeister integration from starting.
- Retained numeric-only firmware version comparison and the 12-hour update check.

## 0.2.7

- Added explicit `User-Agent` and `Accept` headers to the SDR Engineering firmware request to prevent HTTP 403 responses.
- Firmware comparison continues to use only numeric dotted version components.
- Added `firmware_check_status` attribute to `New firmware available`.
- Added `firmware_check_error` attribute when the remote check fails.
- A failed remote firmware check no longer forces the binary sensor to `unavailable`; the state becomes unknown until a successful check.
- Local HeatMeister control remains independent of the external firmware endpoint.

## 0.2.6

- Firmware comparison now uses only the numeric version components; prefixes such as `v` or `V` are ignored.

- Added a firmware check against SDR Engineering every 12 hours.
- Added `New firmware available` binary sensor.
- Compares the remote firmware with local `FW_VERSION` from `/getStatus`.
- Ignores leading `v`/`V` during version comparison.
- Added `installed_version`, `latest_version`, and `check_interval_hours` attributes.
- External firmware-check failures do not prevent the local integration from loading.

## 0.2.5

- Version/release maintenance.

## 0.2.3

- Added firmware version diagnostic entity.
- Firmware version displayed without leading `v`.
- Removed Fan entity while retaining Fan speed and Fan mode controls.
