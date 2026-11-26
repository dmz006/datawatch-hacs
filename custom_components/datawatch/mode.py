"""Datawatch mode on a voice device: say something, listen, answer, until the user leaves.

Speaking and listening use Home Assistant's public Assist satellite actions. Anything that
goes wrong is said out loud where possible: the user may not be looking at a screen.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging

from homeassistant.components.assist_satellite import AssistSatelliteEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_SUPPORTED_FEATURES
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.storage import Store

from .api import (
    DatawatchAuthError,
    DatawatchCertificateError,
    DatawatchClient,
    DatawatchError,
)
from .const import DOMAIN
from .voice.conversation import Conversation, Reply, needs_data

_LOGGER = logging.getLogger(__name__)

# Seconds allowed for one spoken reply plus the answer to it. A device that is interrupted
# may never answer, and this stops the mode waiting for ever.
TURN_LIMIT = 90.0
# Seconds to wait for the device to finish the request that opened the mode.
IDLE_WAIT = 10.0

_SATELLITE = "assist_satellite"
_NEEDED = AssistSatelliteEntityFeature.ANNOUNCE | AssistSatelliteEntityFeature.START_CONVERSATION
_CLOSING = "Closing datawatch."
_CERTIFICATE = f"The datawatch certificate has changed. Check it in Home Assistant. {_CLOSING}"
_REFUSED = f"datawatch refused access. Check the token in Home Assistant. {_CLOSING}"
_FAULT = f"Something went wrong in datawatch mode. {_CLOSING}"


class SharedFocus:
    """The focus, shared by every voice device and kept until the user clears it."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store: Store[dict[str, str | None]] = Store(hass, 1, f"{DOMAIN}.focus")
        self.project: str | None = None

    async def async_load(self) -> None:
        self.project = (await self._store.async_load() or {}).get("project")

    async def async_set(self, project: str | None) -> None:
        if project != self.project:
            self.project = project
            await self._store.async_save({"project": project})

    async def async_remove(self) -> None:
        await self._store.async_remove()


class DatawatchMode:
    """Runs visits to datawatch mode, at most one per voice device."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry[DatawatchClient],
        focus: SharedFocus,
    ) -> None:
        self._hass = hass
        self._entry = entry
        self._focus = focus
        self._active: set[str] = set()

    async def async_entry_phrase(self, satellite_id: str | None) -> str:
        """An entry phrase was heard. An empty reply means nothing is spoken here."""
        if satellite_id is None:
            return "Datawatch mode works from a voice device."
        state = self._hass.states.get(satellite_id)
        features = state.attributes.get(ATTR_SUPPORTED_FEATURES, 0) if state else 0
        if features & _NEEDED != _NEEDED:
            return "This voice device can't hold a datawatch conversation."
        if satellite_id not in self._active:
            self._active.add(satellite_id)
            # Not started eagerly: this request has to finish before the mode speaks.
            self._entry.async_create_background_task(
                self._hass, self._visit(satellite_id), f"{DOMAIN} voice", eager_start=False
            )
        return ""

    async def _visit(self, satellite_id: str) -> None:
        try:
            await self._wait_until_idle(satellite_id)
            await self._converse(satellite_id)
        except HomeAssistantError, TimeoutError:
            _LOGGER.warning("The voice device could not continue datawatch mode", exc_info=True)
            await self._announce(satellite_id, _CLOSING)
        except Exception:
            _LOGGER.exception("datawatch mode failed")
            await self._announce(satellite_id, _FAULT)
        finally:
            self._active.discard(satellite_id)

    async def _wait_until_idle(self, satellite_id: str) -> None:
        idle = asyncio.Event()

        def check() -> None:
            state = self._hass.states.get(satellite_id)
            if state is not None and state.state == "idle":
                idle.set()

        @callback
        def changed(event: Event[EventStateChangedData]) -> None:
            check()

        stop = async_track_state_change_event(self._hass, [satellite_id], changed)
        try:
            check()
            with contextlib.suppress(TimeoutError):
                async with asyncio.timeout(IDLE_WAIT):
                    await idle.wait()
        finally:
            stop()

    async def _converse(self, satellite_id: str) -> None:
        conversation = Conversation(self._focus.project)
        reply = conversation.enter()
        while not reply.ends:
            heard = await self._ask(satellite_id, reply.text)
            if heard is None:
                reply = conversation.silence()
            else:
                reply = await self._answer(conversation, heard)
        await self._announce(satellite_id, reply.text)

    async def _ask(self, satellite_id: str, text: str) -> str | None:
        """Say text and listen. None means nothing was heard."""
        try:
            async with asyncio.timeout(TURN_LIMIT):
                response = await self._hass.services.async_call(
                    _SATELLITE,
                    "ask_question",
                    {"entity_id": satellite_id, "question": text},
                    blocking=True,
                    return_response=True,
                )
        except HomeAssistantError as error:
            if error.translation_key == "no_answer":
                return None
            raise
        return str((response or {}).get("sentence") or "").strip() or None

    async def _answer(self, conversation: Conversation, heard: str) -> Reply:
        conversation.focus = self._focus.project
        snapshot = None
        if needs_data(heard):
            try:
                snapshot = await self._entry.runtime_data.snapshot(conversation.focus)
            except DatawatchCertificateError:
                return Reply(_CERTIFICATE, ends=True)
            except DatawatchAuthError:
                return Reply(_REFUSED, ends=True)
            except DatawatchError:
                _LOGGER.warning("datawatch could not be read", exc_info=True)
        reply = conversation.hear(heard, snapshot)
        await self._focus.async_set(conversation.focus)
        return reply

    async def _announce(self, satellite_id: str, text: str) -> None:
        """Say text without listening. A device that cannot is only logged."""
        try:
            async with asyncio.timeout(TURN_LIMIT):
                await self._hass.services.async_call(
                    _SATELLITE,
                    "announce",
                    {"entity_id": satellite_id, "message": text, "preannounce": False},
                    blocking=True,
                )
        except HomeAssistantError, TimeoutError:
            _LOGGER.warning("Could not speak on the voice device", exc_info=True)
