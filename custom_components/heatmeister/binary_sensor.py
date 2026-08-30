from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import HeatMeisterEntity
from .firmware import normalize_version, version_tuple


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    runtime = entry.runtime_data
    async_add_entities([
        HeatMeisterNewFirmwareAvailable(
            runtime.coordinator,
            runtime.firmware_coordinator,
        )
    ])


class HeatMeisterNewFirmwareAvailable(HeatMeisterEntity, BinarySensorEntity):
    """Indicate whether a newer HeatMeister firmware version is available."""

    _attr_name = "New firmware available"
    _attr_icon = "mdi:update"

    def __init__(self, coordinator, firmware_coordinator) -> None:
        super().__init__(coordinator)
        self.firmware_coordinator = firmware_coordinator
        self._attr_unique_id = f"{self._device_identifier}_new_firmware_available"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            self.firmware_coordinator.async_add_listener(self.async_write_ha_state)
        )

    @property
    def is_on(self) -> bool | None:
        installed = version_tuple(self.coordinator.data.get("FW_VERSION"))
        latest = version_tuple(self.firmware_coordinator.data)
        if installed is None or latest is None:
            return None
        return latest > installed

    @property
    def extra_state_attributes(self):
        status = "ok" if (
            self.firmware_coordinator.last_update_success
            and self.firmware_coordinator.data is not None
        ) else "error"

        attributes = {
            "installed_version": normalize_version(
                self.coordinator.data.get("FW_VERSION")
            ),
            "latest_version": normalize_version(self.firmware_coordinator.data),
            "check_interval_hours": 12,
            "firmware_check_status": status,
        }

        if status == "error" and self.firmware_coordinator.last_error:
            attributes["firmware_check_error"] = (
                self.firmware_coordinator.last_error
            )

        return attributes
