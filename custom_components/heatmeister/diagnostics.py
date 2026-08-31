from __future__ import annotations
from typing import Any
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    data = dict(entry.runtime_data.coordinator.data)
    # Local network identifiers are unnecessary in exported diagnostics.
    for key in ("WIFI_TEST_IP", "WIFI_HOSTNAME"):
        data.pop(key, None)
    return {"version": "0.2.10", "device_status": data}
