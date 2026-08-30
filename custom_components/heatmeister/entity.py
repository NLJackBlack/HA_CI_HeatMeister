from __future__ import annotations
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import HeatMeisterCoordinator

class HeatMeisterEntity(CoordinatorEntity[HeatMeisterCoordinator]):
    _attr_has_entity_name = True
    @property
    def _device_identifier(self) -> str:
        data = self.coordinator.data
        return str(data.get("WIFI_HOSTNAME") or data.get("NODE_NAME") or self.coordinator.api.host)
    @property
    def device_info(self) -> DeviceInfo:
        data = self.coordinator.data
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_identifier)},
            name=str(data.get("NODE_NAME", "HeatMeister")),
            manufacturer="SDR Engineering",
            model="HeatMeister",
            sw_version=str(data.get("FW_VERSION", "")),
            configuration_url=f"http://{self.coordinator.api.host}/",
        )
