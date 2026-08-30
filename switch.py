from __future__ import annotations
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from .entity import HeatMeisterEntity

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    c=entry.runtime_data; async_add_entities([HeatMeisterBoostSwitch(c), HeatMeisterAmbientControlSwitch(c)])

class HeatMeisterBoostSwitch(HeatMeisterEntity, SwitchEntity):
    _attr_name="Boost"
    def __init__(self,c): super().__init__(c); self._attr_unique_id=f"{self._device_identifier}_boost"
    @property
    def is_on(self): return int(self.coordinator.data.get("FAN_BOOSTMODE",0))==1
    async def async_turn_on(self,**kwargs): await self.coordinator.async_send(FAN_BOOSTMODE=1)
    async def async_turn_off(self,**kwargs): await self.coordinator.async_send(FAN_BOOSTMODE=0)

class HeatMeisterAmbientControlSwitch(HeatMeisterEntity, SwitchEntity):
    _attr_name="Room temperature control"
    def __init__(self,c): super().__init__(c); self._attr_unique_id=f"{self._device_identifier}_ambient_control"
    @property
    def is_on(self): return int(self.coordinator.data.get("AMBIENTCONTROL_ENABLE",0))==1
    async def async_turn_on(self,**kwargs): await self.coordinator.async_send(AMBIENTCONTROL_ENABLE=1)
    async def async_turn_off(self,**kwargs): await self.coordinator.async_send(AMBIENTCONTROL_ENABLE=0)
