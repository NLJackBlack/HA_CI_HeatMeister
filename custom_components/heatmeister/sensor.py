from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTemperature, SIGNAL_STRENGTH_DECIBELS_MILLIWATT, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from .entity import HeatMeisterEntity

@dataclass(frozen=True)
class Desc:
    key:str; name:str; unit:str|None=None; device_class:SensorDeviceClass|None=None; state_class:SensorStateClass|None=None; transform:Callable[[Any],Any]|None=None; diagnostic:bool=False

SENSORS=(
 Desc("TEMP_AMBIENT","Ambient temperature",UnitOfTemperature.CELSIUS,SensorDeviceClass.TEMPERATURE,SensorStateClass.MEASUREMENT,float),
 Desc("TEMP_INLET","Inlet temperature",UnitOfTemperature.CELSIUS,SensorDeviceClass.TEMPERATURE,SensorStateClass.MEASUREMENT,float),
 Desc("TEMP_OUTLET","Outlet temperature",UnitOfTemperature.CELSIUS,SensorDeviceClass.TEMPERATURE,SensorStateClass.MEASUREMENT,float),
 Desc("TEMP_DELTA","Delta temperature",UnitOfTemperature.CELSIUS,SensorDeviceClass.TEMPERATURE,SensorStateClass.MEASUREMENT,float),
 Desc("TEMP_INLET_RATE","Inlet temperature rate","°C/min",None,SensorStateClass.MEASUREMENT,float),
 Desc("FAN_SPEED","Fan speed","%",None,SensorStateClass.MEASUREMENT,float),
 Desc("WIFI_TEST_RSSI","Wi-Fi signal",SIGNAL_STRENGTH_DECIBELS_MILLIWATT,SensorDeviceClass.SIGNAL_STRENGTH,SensorStateClass.MEASUREMENT,int,True),
 Desc("TEMP_CHIP","Chip temperature",UnitOfTemperature.CELSIUS,SensorDeviceClass.TEMPERATURE,SensorStateClass.MEASUREMENT,float,True),
 Desc("RUNTIME","Runtime",UnitOfTime.SECONDS,SensorDeviceClass.DURATION,SensorStateClass.TOTAL_INCREASING,int,True),
 Desc("WIFI_RECONNECTS","Wi-Fi reconnects",None,None,SensorStateClass.TOTAL_INCREASING,int,True),
 Desc("FAN_CONTROL_STATE","Fan control state",None,None,None,int,True),
 Desc("OPERATING_MODE","Operating mode",None,None,None,int,True),
 Desc("HEAP_FREE","Free heap","B",SensorDeviceClass.DATA_SIZE,SensorStateClass.MEASUREMENT,int,True),
)
async def async_setup_entry(hass:HomeAssistant,entry:ConfigEntry,async_add_entities:AddConfigEntryEntitiesCallback)->None:
    async_add_entities(HeatMeisterSensor(entry.runtime_data,d) for d in SENSORS)
class HeatMeisterSensor(HeatMeisterEntity,SensorEntity):
    def __init__(self,c,d:Desc):
        super().__init__(c); self.d=d; self._attr_name=d.name; self._attr_unique_id=f"{self._device_identifier}_{d.key.lower()}"; self._attr_native_unit_of_measurement=d.unit; self._attr_device_class=d.device_class; self._attr_state_class=d.state_class
        if d.diagnostic: self._attr_entity_category=EntityCategory.DIAGNOSTIC
    @property
    def native_value(self):
        v=self.coordinator.data.get(self.d.key)
        if v is None:return None
        try:return self.d.transform(v) if self.d.transform else v
        except (TypeError,ValueError):return v
