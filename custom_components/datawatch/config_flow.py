"""Set up datawatch from the Home Assistant UI: the address, then certificate approval."""

from __future__ import annotations

from typing import Any, override

import probatio
from homeassistant.config_entries import (
    SOURCE_RECONFIGURE,
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_TOKEN, CONF_URL
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    ConversationAgentSelector,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import (
    DatawatchAuthError,
    DatawatchCertificateError,
    DatawatchClient,
    DatawatchError,
    fetch_fingerprint,
    parse_server_url,
)
from .const import CONF_ASSISTANT, CONF_FINGERPRINT, DOMAIN

_SERVER_SCHEMA = probatio.Schema(
    {
        probatio.Required(CONF_URL): TextSelector(TextSelectorConfig(type=TextSelectorType.URL)),
        probatio.Optional(CONF_TOKEN): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
    }
)


class DatawatchConfigFlow(ConfigFlow, domain=DOMAIN):
    """Ask for the server, show its certificate, and save only once approved."""

    VERSION = 1

    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    @staticmethod
    @callback
    @override
    def async_get_options_flow(config_entry: ConfigEntry) -> DatawatchOptionsFlow:
        """The AI assistant setting."""
        return DatawatchOptionsFlow()

    @override
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """The server address and optional token."""
        return await self._server_step(user_input)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change the address or token later."""
        return await self._server_step(user_input)

    async def _server_step(self, user_input: dict[str, Any] | None) -> ConfigFlowResult:
        if user_input is None:
            return self._server_form()
        try:
            url = parse_server_url(user_input[CONF_URL])
        except ValueError:
            return self._server_form("invalid_url", user_input[CONF_URL])
        try:
            # Only the TLS handshake: nothing is sent to a server not yet approved.
            fingerprint = await fetch_fingerprint(url)
        except DatawatchError:
            return self._server_form("cannot_connect", url)

        saved = self._saved()
        token = str(user_input.get(CONF_TOKEN, "")).strip()
        if not token and url == saved.get(CONF_URL):
            token = saved.get(CONF_TOKEN, "")
        self._data = {CONF_URL: url, CONF_FINGERPRINT: fingerprint}
        if token:
            self._data[CONF_TOKEN] = token
        return await self.async_step_certificate()

    async def async_step_certificate(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show the fingerprint. Submitting approves it, then datawatch is read once."""
        if user_input is None:
            return self.async_show_form(
                step_id="certificate",
                data_schema=probatio.Schema({}),
                description_placeholders={
                    "url": self._data[CONF_URL],
                    "fingerprint": self._data[CONF_FINGERPRINT],
                },
            )
        client = DatawatchClient(
            async_get_clientsession(self.hass),
            self._data[CONF_URL],
            self._data[CONF_FINGERPRINT],
            self._data.get(CONF_TOKEN),
        )
        try:
            await client.project_names()
        except DatawatchCertificateError:
            return self._server_form("certificate_changed", self._data[CONF_URL])
        except DatawatchAuthError:
            return self._server_form("invalid_auth", self._data[CONF_URL])
        except DatawatchError:
            return self._server_form("cannot_connect", self._data[CONF_URL])
        if self.source == SOURCE_RECONFIGURE:
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(), data=self._data
            )
        return self.async_create_entry(title="datawatch", data=self._data)

    def _saved(self) -> dict[str, str]:
        if self.source != SOURCE_RECONFIGURE:
            return {}
        return dict(self._get_reconfigure_entry().data)

    def _server_form(self, error: str | None = None, url: str | None = None) -> ConfigFlowResult:
        suggested = url or self._saved().get(CONF_URL)
        return self.async_show_form(
            step_id="reconfigure" if self.source == SOURCE_RECONFIGURE else "user",
            data_schema=self.add_suggested_values_to_schema(
                _SERVER_SCHEMA, {CONF_URL: suggested} if suggested else {}
            ),
            errors={"base": error} if error else {},
        )


class DatawatchOptionsFlow(OptionsFlow):
    """Choose the AI assistant that may use datawatch. None chosen means AI is off."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            chosen = user_input.get(CONF_ASSISTANT)
            return self.async_create_entry(data={CONF_ASSISTANT: chosen} if chosen else {})
        schema = probatio.Schema({probatio.Optional(CONF_ASSISTANT): ConversationAgentSelector()})
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(schema, self.config_entry.options),
        )
