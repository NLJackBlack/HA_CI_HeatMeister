# Changelog

## 0.2.3

- Added **Firmware version** as a diagnostic sensor.
- Firmware values now omit a leading `v`/`V`, so `v2.8.8` is displayed as `2.8.8`.
- Removed the separate Home Assistant **Fan** entity/platform.
- Fan control remains available through the dedicated **Fan speed** slider and **Fan mode** selector (Auto / Manual / Boost).
- Updated README and integration documentation.

## 0.2.2

- Repackaged repository for HACS compatibility.
- Moved the Home Assistant integration to `custom_components/heatmeister/`.
- Added root `hacs.json`.
- Added GitHub HACS and hassfest validation workflows.
- Added GitHub repository URLs, issue tracker and `@NLJackBlack` as code owner to `manifest.json`.
- Kept Fan speed slider and Auto / Manual / Boost selector from 0.2.1.

## 0.2.1

- Added dedicated Fan speed number entity rendered as a 0-100% slider.
- Added dedicated Fan mode select entity with Auto / Manual / Boost.
- Moving the fan-speed slider switches to Manual mode and disables Boost.

## 0.2.0

- Added local brand assets.
- Added native fan percentage support, room control, target temperature and diagnostics.
