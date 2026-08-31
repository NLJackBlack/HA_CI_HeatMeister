from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HeatMeisterApi
from .const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, PLATFORMS
from .coordinator import HeatMeisterCoordinator
from .firmware import HeatMeisterFirmwareCoordinator


@dataclass
class HeatMeisterRuntimeData:
    coordinator: HeatMeisterCoordinator
    firmware_coordinator: HeatMeisterFirmwareCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    api = HeatMeisterApi(
        entry.data[CONF_HOST],
        session,
        username=entry.data.get(CONF_USERNAME),
        password=entry.data.get(CONF_PASSWORD),
    )

    coordinator = HeatMeisterCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    firmware_coordinator = HeatMeisterFirmwareCoordinator(hass, session)
    # An unavailable Internet endpoint must not stop local HeatMeister setup.
    try:
        await firmware_coordinator.async_refresh()
    except Exception:  # Defensive: external firmware check must never block local setup.
        pass

    entry.runtime_data = HeatMeisterRuntimeData(coordinator, firmware_coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
