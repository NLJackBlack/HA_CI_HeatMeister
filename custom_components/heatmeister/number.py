from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import HeatMeisterEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities([
        HeatMeisterFanSpeed(coordinator),
        HeatMeisterSetpoint(coordinator),
    ])


class HeatMeisterFanSpeed(HeatMeisterEntity, NumberEntity):
    """Manual fan-speed slider (0-100%)."""

    _attr_name = "Fan speed"
    _attr_native_min_value = 0.0
    _attr_native_max_value = 100.0
    _attr_native_step = 1.0
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:fan"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._device_identifier}_fan_speed_control"

    @property
    def native_value(self) -> float | None:
        try:
            return float(self.coordinator.data.get("FAN_SPEED", 0))
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        # Changing the slider deliberately switches to manual mode and cancels boost.
        await self.coordinator.async_send(
            FAN_SPEED=max(0, min(100, int(round(value)))),
            FAN_CONTROLMODE=1,
            FAN_BOOSTMODE=0,
        )


class HeatMeisterSetpoint(HeatMeisterEntity, NumberEntity):
    _attr_name = "Target temperature"
    _attr_native_min_value = 10.0
    _attr_native_max_value = 30.0
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._device_identifier}_target_temperature"

    @property
    def native_value(self) -> float | None:
        try:
            return float(self.coordinator.data.get("AMBIENTCONTROL_TEMP"))
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_send(AMBIENTCONTROL_TEMP=f"{value:.2f}")
