from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import HeatMeisterEntity

MODE_AUTO = "Auto"
MODE_MANUAL = "Manual"
MODE_BOOST = "Boost"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([HeatMeisterFanMode(entry.runtime_data)])


class HeatMeisterFanMode(HeatMeisterEntity, SelectEntity):
    """Explicit HeatMeister operating-mode selector."""

    _attr_name = "Fan mode"
    _attr_options = [MODE_AUTO, MODE_MANUAL, MODE_BOOST]
    _attr_icon = "mdi:fan-auto"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._device_identifier}_fan_mode"

    @property
    def current_option(self) -> str:
        if int(self.coordinator.data.get("FAN_BOOSTMODE", 0)) == 1:
            return MODE_BOOST
        if int(self.coordinator.data.get("FAN_CONTROLMODE", 0)) == 0:
            return MODE_AUTO
        return MODE_MANUAL

    async def async_select_option(self, option: str) -> None:
        if option == MODE_AUTO:
            await self.coordinator.async_send(FAN_BOOSTMODE=0, FAN_CONTROLMODE=0)
        elif option == MODE_MANUAL:
            await self.coordinator.async_send(FAN_BOOSTMODE=0, FAN_CONTROLMODE=1)
        elif option == MODE_BOOST:
            await self.coordinator.async_send(FAN_BOOSTMODE=1)
        else:
            raise ValueError(f"Unsupported fan mode: {option}")
