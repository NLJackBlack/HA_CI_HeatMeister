from __future__ import annotations
from datetime import timedelta
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .api import HeatMeisterApi, HeatMeisterApiError
from .const import DEFAULT_SCAN_INTERVAL
_LOGGER = logging.getLogger(__name__)

class HeatMeisterCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, api: HeatMeisterApi) -> None:
        super().__init__(hass, _LOGGER, name="HeatMeister", update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL))
        self.api = api

    async def _async_update_data(self) -> dict:
        try:
            return await self.api.async_get_status()
        except HeatMeisterApiError as err:
            raise UpdateFailed(str(err)) from err

    async def async_send(self, **params) -> None:
        await self.api.async_set_status(**params)
        await self.async_request_refresh()
