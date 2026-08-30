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
    """Fetch the latest firmware version from SDR Engineering every 12 hours."""

    def __init__(self, hass: HomeAssistant, session: aiohttp.ClientSession) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="HeatMeister firmware",
            update_interval=timedelta(hours=FIRMWARE_CHECK_INTERVAL_HOURS),
        )
        self._session = session
        self.last_error: str | None = None

    async def _async_update_data(self) -> str | None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Home Assistant HeatMeister/0.2.7)",
            "Accept": "text/plain,*/*",
        }

        try:
            async with self._session.get(
                FIRMWARE_VERSION_URL,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                response.raise_for_status()
                body = (await response.text()).strip()

        except (aiohttp.ClientError, TimeoutError) as err:
            self.last_error = str(err)
            raise UpdateFailed(
                f"Unable to check latest HeatMeister firmware: {err}"
            ) from err

        latest_version = normalize_version(body)

        if latest_version is None:
            self.last_error = (
                "Firmware endpoint did not return a recognizable numeric version"
            )
            raise UpdateFailed(self.last_error)

        self.last_error = None
        return latest_version
