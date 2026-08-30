from __future__ import annotations

from datetime import timedelta
import re

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import FIRMWARE_CHECK_INTERVAL_HOURS, FIRMWARE_VERSION_URL


def normalize_version(value: str | None) -> str | None:
    """Return only the numeric dotted firmware version.

    Examples:
    v2.8.8 -> 2.8.8
    V2.8.8 -> 2.8.8
    2.8.8  -> 2.8.8
    """
    if value is None:
        return None

    match = re.search(r"(\d+(?:\.\d+)+)", str(value))
    return match.group(1) if match else None


def version_tuple(value: str | None) -> tuple[int, ...] | None:
    """Convert the numeric dotted version to an integer tuple for comparison."""
    normalized = normalize_version(value)
    if normalized is None:
        return None

    try:
        return tuple(int(part) for part in normalized.split("."))
    except ValueError:
        return None


class HeatMeisterFirmwareCoordinator(DataUpdateCoordinator[str | None]):
    """Check SDR Engineering for the latest HeatMeister firmware."""

    def __init__(self, hass: HomeAssistant, session: aiohttp.ClientSession) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name="HeatMeister firmware",
            update_interval=timedelta(hours=FIRMWARE_CHECK_INTERVAL_HOURS),
        )
        self._session = session

    async def _async_update_data(self) -> str | None:
        try:
            async with self._session.get(FIRMWARE_VERSION_URL, timeout=10) as response:
                response.raise_for_status()
                body = (await response.text()).strip()
        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Unable to check latest HeatMeister firmware: {err}") from err

        match = re.search(r"[vV]?\d+(?:\.\d+)+", body)
        if not match:
            raise UpdateFailed("Firmware endpoint did not return a recognizable version")
        return normalize_version(match.group(0))
