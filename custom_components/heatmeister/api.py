from __future__ import annotations
import asyncio
from typing import Any
import aiohttp

class HeatMeisterApiError(Exception):
    """HeatMeister API error."""

class HeatMeisterApi:
    def __init__(self, host: str, session: aiohttp.ClientSession) -> None:
        self.host = host.strip().replace("http://", "").replace("https://", "").rstrip("/")
        self._session = session

    @property
    def base_url(self) -> str:
        return f"http://{self.host}"

    async def async_get_status(self) -> dict[str, Any]:
        try:
            async with asyncio.timeout(5):
                response = await self._session.get(f"{self.base_url}/getStatus")
                response.raise_for_status()
                data = await response.json(content_type=None)
                if not isinstance(data, dict) or "NODE_NAME" not in data:
                    raise HeatMeisterApiError("Unexpected response from HeatMeister")
                return data
        except HeatMeisterApiError:
            raise
        except (TimeoutError, aiohttp.ClientError, ValueError) as err:
            raise HeatMeisterApiError(f"Could not communicate with HeatMeister at {self.host}") from err

    async def async_set_status(self, **params: Any) -> None:
        try:
            async with asyncio.timeout(5):
                response = await self._session.get(f"{self.base_url}/setStatus", params={k: str(v) for k,v in params.items()})
                response.raise_for_status()
                await response.read()
        except (TimeoutError, aiohttp.ClientError) as err:
            raise HeatMeisterApiError(f"Could not update HeatMeister at {self.host}") from err
