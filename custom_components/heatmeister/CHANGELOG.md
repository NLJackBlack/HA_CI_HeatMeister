# Changelog

## 0.3.0

- Upped the version number, since HACS thinks 0.2.10 is older than 0.2.8

## 0.2.10

- Added password/access-code support using HTTP Digest Authentication as used by HeatMeister firmware.
- Setup now detects a `401 Unauthorized` Digest challenge after entering the IP address or hostname.
- Added a second wizard step for username and password/access code, with username pre-filled as `admin`.
- Credentials are validated against `/getStatus` before setup completes.
- Digest authentication is used for both `/getStatus` and `/setStatus`.
- Devices without authentication remain fully supported.
- Added a masked password field in the setup wizard.
- Updated diagnostics version and firmware-check User-Agent to 0.2.10.

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
