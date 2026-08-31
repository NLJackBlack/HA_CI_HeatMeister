from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import (
    HeatMeisterApi,
    HeatMeisterApiError,
    HeatMeisterAuthenticationRequired,
    HeatMeisterInvalidAuthentication,
)
from .const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    DEFAULT_USERNAME,
    DOMAIN,
)


class HeatMeisterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure HeatMeister from the Home Assistant UI."""

    VERSION = 1

    def __init__(self) -> None:
        self._host: str | None = None

    async def async_step_user(self, user_input=None):
        """Validate the host and continue to auth only when required."""
        errors = {}

        if user_input is not None:
            api = HeatMeisterApi(
                user_input[CONF_HOST],
                async_get_clientsession(self.hass),
            )
            try:
                data = await api.async_get_status()
            except HeatMeisterAuthenticationRequired:
                self._host = api.host
                return await self.async_step_auth()
            except HeatMeisterApiError:
                errors["base"] = "cannot_connect"
            else:
                return await self._async_create_entry(api, data)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_HOST, default="192.168.68.116"): str}
            ),
            errors=errors,
        )

    async def async_step_auth(self, user_input=None):
        """Validate Digest credentials for a protected HeatMeister."""
        errors = {}

        if not self._host:
            return self.async_abort(reason="cannot_connect")

        if user_input is not None:
            username = user_input[CONF_USERNAME].strip()
            password = user_input[CONF_PASSWORD]
            api = HeatMeisterApi(
                self._host,
                async_get_clientsession(self.hass),
                username=username,
                password=password,
            )
            try:
                data = await api.async_get_status()
            except (HeatMeisterInvalidAuthentication, HeatMeisterAuthenticationRequired):
                errors["base"] = "invalid_auth"
            except HeatMeisterApiError:
                errors["base"] = "cannot_connect"
            else:
                return await self._async_create_entry(
                    api,
                    data,
                    username=username,
                    password=password,
                )

        return self.async_show_form(
            step_id="auth",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
                    vol.Required(CONF_PASSWORD): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                }
            ),
            errors=errors,
        )

    async def _async_create_entry(
        self,
        api: HeatMeisterApi,
        data: dict,
        username: str | None = None,
        password: str | None = None,
    ):
        """Create the config entry after successful validation."""
        node_name = str(data.get("NODE_NAME") or api.host)
        unique_id = str(data.get("WIFI_HOSTNAME") or node_name)
        await self.async_set_unique_id(unique_id)

        entry_data = {CONF_HOST: api.host}
        if username:
            entry_data[CONF_USERNAME] = username
            entry_data[CONF_PASSWORD] = password or ""

        self._abort_if_unique_id_configured(updates=entry_data)
        return self.async_create_entry(title=node_name, data=entry_data)
