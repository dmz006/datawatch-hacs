"""Set up datawatch from the Home Assistant UI: the address, then certificate approval."""

from __future__ import annotations

from typing import Any, override

import probatio
from homeassistant.config_entries import (
    SOURCE_RECONFIGURE,
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    OptionsFlow,
    SubentryFlowResult,
)
from homeassistant.const import CONF_TOKEN, CONF_URL
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    ConversationAgentSelector,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
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
from .const import CONF_ASSISTANT, CONF_FINGERPRINT, CONF_ITEMS, DOMAIN, SUBENTRY_REPORT
from .voice.custom import ITEMS, spoken_form
from .voice.phrases import Kind, parse

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

    @classmethod
    @callback
    @override
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Reports the user defines."""
        return {SUBENTRY_REPORT: ReportSubentryFlow}

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


class ReportSubentryFlow(ConfigSubentryFlow):
    """Add or change a spoken report: its name and what goes in it."""

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        return self._step("user", user_input)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        return self._step("reconfigure", user_input)

    def _step(self, step: str, user_input: dict[str, Any] | None) -> SubentryFlowResult:
        current = self._get_reconfigure_subentry() if step == "reconfigure" else None
        errors: dict[str, str] = {}
        if user_input is not None:
            name = " ".join(str(user_input["name"]).split())
            items = [item for item in ITEMS if item in user_input[CONF_ITEMS]]
            if error := self._name_problem(name, current.subentry_id if current else None):
                errors["name"] = error
            elif not items:
                errors[CONF_ITEMS] = "no_items"
            elif current is None:
                return self.async_create_entry(title=name, data={CONF_ITEMS: items})
            else:
                return self.async_update_and_abort(
                    self._get_entry(), current, title=name, data={CONF_ITEMS: items}
                )
        suggested = user_input
        if suggested is None and current is not None:
            suggested = {"name": current.title, CONF_ITEMS: current.data[CONF_ITEMS]}
        schema = probatio.Schema(
            {
                probatio.Required("name"): str,
                probatio.Required(CONF_ITEMS): SelectSelector(
                    SelectSelectorConfig(
                        options=list(ITEMS),
                        multiple=True,
                        mode=SelectSelectorMode.LIST,
                        translation_key="report_items",
                    )
                ),
            }
        )
        return self.async_show_form(
            step_id=step,
            data_schema=self.add_suggested_values_to_schema(schema, suggested or {}),
            errors=errors,
        )

    def _name_problem(self, name: str, own_id: str | None) -> str | None:
        """A name must be something you can say that means nothing else."""
        spoken = spoken_form(name)
        if not spoken:
            return "no_name"
        if any(parse(said).kind is not Kind.UNKNOWN for said in (name, spoken)):
            return "name_is_a_command"
        if spoken in ("datawatch", "data watch", "open datawatch", "use datawatch"):
            return "name_is_a_command"
        for subentry in self._get_entry().subentries.values():
            if subentry.subentry_id != own_id and spoken_form(subentry.title) == spoken:
                return "name_taken"
        return None
