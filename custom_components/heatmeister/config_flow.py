from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import HeatMeisterApi, HeatMeisterApiError
from .const import CONF_HOST, DOMAIN

class HeatMeisterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            api = HeatMeisterApi(user_input[CONF_HOST], async_get_clientsession(self.hass))
            try:
                data = await api.async_get_status()
            except HeatMeisterApiError:
                errors["base"] = "cannot_connect"
            else:
                node_name = str(data.get("NODE_NAME") or api.host)
                unique_id = str(data.get("WIFI_HOSTNAME") or node_name)
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured(updates={CONF_HOST: api.host})
                return self.async_create_entry(title=node_name, data={CONF_HOST: api.host})
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST, default="192.168.68.116"): str}),
            errors=errors,
        )
