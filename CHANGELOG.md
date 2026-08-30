# Changelog

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
