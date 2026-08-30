from __future__ import annotations
from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from .entity import HeatMeisterEntity

PRESET_AUTO = "Auto"
PRESET_MANUAL = "Manual"
PRESET_BOOST = "Boost"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities([HeatMeisterFan(entry.runtime_data)])

class HeatMeisterFan(HeatMeisterEntity, FanEntity):
    _attr_name = "Fan"
    _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
    _attr_speed_count = 100
    _attr_preset_modes = [PRESET_AUTO, PRESET_MANUAL, PRESET_BOOST]
    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._device_identifier}_fan"
    @property
    def is_on(self) -> bool:
        return bool(int(self.coordinator.data.get("FAN_ENABLED", 0))) or self.percentage > 0
    @property
    def percentage(self) -> int:
        try: return max(0, min(100, int(float(self.coordinator.data.get("FAN_SPEED", 0)))))
        except (TypeError, ValueError): return 0
    @property
    def preset_mode(self) -> str | None:
        if int(self.coordinator.data.get("FAN_BOOSTMODE", 0)) == 1: return PRESET_BOOST
        if int(self.coordinator.data.get("FAN_CONTROLMODE", 0)) == 0: return PRESET_AUTO
        return PRESET_MANUAL
    async def async_set_percentage(self, percentage: int) -> None:
        await self.coordinator.async_send(FAN_SPEED=max(0,min(100,int(percentage))), FAN_CONTROLMODE=1, FAN_BOOSTMODE=0)
    async def async_set_preset_mode(self, preset_mode: str) -> None:
        if preset_mode == PRESET_AUTO:
            await self.coordinator.async_send(FAN_BOOSTMODE=0, FAN_CONTROLMODE=0)
        elif preset_mode == PRESET_MANUAL:
            await self.coordinator.async_send(FAN_BOOSTMODE=0, FAN_CONTROLMODE=1)
        elif preset_mode == PRESET_BOOST:
            await self.coordinator.async_send(FAN_BOOSTMODE=1)
        else: raise ValueError(f"Unsupported preset mode: {preset_mode}")
    async def async_turn_on(self, percentage=None, preset_mode=None, **kwargs) -> None:
        if preset_mode:
            await self.async_set_preset_mode(preset_mode); return
        await self.async_set_percentage(percentage if percentage is not None else max(self.percentage, 30))
    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_send(FAN_SPEED=0, FAN_CONTROLMODE=1, FAN_BOOSTMODE=0)
