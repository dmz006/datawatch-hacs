"""Datawatch mode on a voice device: say something, listen, answer, until the user leaves.

Speaking and listening use Home Assistant's public Assist satellite actions. Anything that
goes wrong is said out loud where possible: the user may not be looking at a screen.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from dataclasses import replace
from typing import Any

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
    DatawatchClosedError,
    DatawatchError,
    DatawatchMissingError,
    DatawatchRefusedError,
    DatawatchSecretError,
)
from .cards import read_card, read_children, search_items
from .const import (
    CONF_ASSISTANT,
    CONF_ITEMS,
    CONF_ORDER,
    DISCUSSING,
    DOMAIN,
    SESSION_SEND,
    SUBENTRY_REPORT,
)
from .doing import perform
from .reporting import build, find, read_automaton, run
from .voice.actions import Action
from .voice.conversation import Conversation, Needs, Reply, topic_of
from .voice.custom import CustomReport
from .voice.items import GONE, Card, Item, restored, stored
from .voice.language import N_, current, for_tag, speaking, t
from .voice.order import Order, chosen
from .voice.phrases import Kind, parse
from .voice.questions import Draft
from .voice.reports import Report

_LOGGER = logging.getLogger(__name__)

# Seconds allowed for one spoken reply plus the answer to it. A device that is interrupted
# may never answer, and this stops the mode waiting for ever.
TURN_LIMIT = 90.0
# A long question takes longer to say: allow for slow speech on top of TURN_LIMIT.
CHARACTERS_PER_SECOND = 10
# Seconds to wait for the AI assistant.
ASSISTANT_LIMIT = 120.0
# Seconds to wait for the device to finish the request that opened the mode.
IDLE_WAIT = 10.0

_SATELLITE = "assist_satellite"
_NEEDED = AssistSatelliteEntityFeature.ANNOUNCE | AssistSatelliteEntityFeature.START_CONVERSATION
_CLOSING = N_("Closing datawatch.")
_CERTIFICATE = N_(
    "The datawatch certificate has changed. Check it in Home Assistant. Closing datawatch."
)
_REFUSED = N_("datawatch refused access. Check the token in Home Assistant. Closing datawatch.")
_FAULT = N_("Something went wrong in datawatch mode. Closing datawatch.")
_SENT = N_("Answer sent. Say next question.")
_ALREADY_CLOSED = N_("That question was already answered or withdrawn. Nothing was sent.")
_SECRET = N_(
    "datawatch refused that answer because it looks like it holds a secret. Nothing was sent."
)
_NOT_ACCEPTED = N_("datawatch refused that answer. Nothing was sent.")
_NOT_CHECKED = N_("I can't reach datawatch, so nothing was sent. Say my answer or option again.")
_UNSURE = N_("I don't know whether the answer was sent. Say questions to check.")
_NO_ASSISTANT = N_("Your assistant didn't answer. Try again, or say stop.")
_SILENT_ASSISTANT = N_("Your assistant had nothing to say.")
_SETTING = (Kind.SET_THIS, Kind.SET_NUMBER, Kind.SET_NAME)


def custom_reports(entry: ConfigEntry) -> tuple[CustomReport, ...]:
    """The reports the user has defined."""
    return tuple(
        CustomReport(subentry.title, tuple(subentry.data[CONF_ITEMS]))
        for subentry in entry.subentries.values()
        if subentry.subentry_type == SUBENTRY_REPORT
    )


def _turn_limit(text: str) -> float:
    return TURN_LIMIT + len(text) / CHARACTERS_PER_SECOND


class SharedFocus:
    """The focus, shared by every voice device and kept until the user clears it."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store: Store[dict[str, Any]] = Store(hass, 1, f"{DOMAIN}.focus")
        self.project: str | None = None
        # The plan, automaton or other items focused inside the project.
        self.path: tuple[Item, ...] = ()

    async def async_load(self) -> None:
        saved = await self._store.async_load() or {}
        self.project = saved.get("project")
        self.path = restored(saved.get("path"))

    async def async_set(self, project: str | None, path: tuple[Item, ...] = ()) -> None:
        if (project, path) != (self.project, self.path):
            self.project, self.path = project, path
            await self._store.async_save({"project": project, "path": stored(path)})

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

    async def async_entry_phrase(self, satellite_id: str | None, heard_in: str | None) -> str:
        """An entry phrase was heard. An empty reply means nothing is spoken here.

        heard_in is the voice assistant's language. The whole visit uses it, or English
        where voice does not have it.
        """
        tag = heard_in or self._hass.config.language
        with speaking(for_tag(tag)):
            return current().tidy(self._entered(satellite_id, tag))

    def _entered(self, satellite_id: str | None, tag: str) -> str:
        if satellite_id is None:
            return t("Datawatch mode works from a voice device.")
        state = self._hass.states.get(satellite_id)
        features = state.attributes.get(ATTR_SUPPORTED_FEATURES, 0) if state else 0
        if features & _NEEDED != _NEEDED:
            return t("This voice device can't hold a datawatch conversation.")
        if satellite_id not in self._active:
            self._active.add(satellite_id)
            # Not started eagerly: this request has to finish before the mode speaks.
            self._entry.async_create_background_task(
                self._hass, self._visit(satellite_id, tag), f"{DOMAIN} voice", eager_start=False
            )
        return ""

    async def _visit(self, satellite_id: str, tag: str) -> None:
        with speaking(for_tag(tag)):
            await self._visit_in_language(satellite_id, tag)

    async def _visit_in_language(self, satellite_id: str, tag: str) -> None:
        try:
            await self._wait_until_idle(satellite_id)
            await self._converse(satellite_id, tag)
        except HomeAssistantError, TimeoutError:
            _LOGGER.warning("The voice device could not continue datawatch mode", exc_info=True)
            await self._announce(satellite_id, t(_CLOSING))
        except Exception:
            _LOGGER.exception("datawatch mode failed")
            await self._announce(satellite_id, t(_FAULT))
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

    async def _converse(self, satellite_id: str, tag: str) -> None:
        assistant = self._entry.options.get(CONF_ASSISTANT)
        conversation = Conversation(
            self._focus.project,
            assistant=bool(assistant),
            reports=custom_reports(self._entry),
            path=self._focus.path,
            session_send=SESSION_SEND,
            order=chosen(self._entry.options.get(CONF_ORDER)),
        )
        chat: str | None = None
        reply = conversation.enter()
        try:
            while not reply.ends:
                question = conversation.current_question
                # So that the AI assistant can tell which question is being discussed.
                self._hass.data[DISCUSSING] = question.id if question else None
                heard = await self._ask(satellite_id, reply.text)
                if heard is None:
                    reply = conversation.silence()
                else:
                    reply = await self._answer(conversation, heard)
                if reply.order is not None:
                    self._save_order(reply.order)
                if reply.send is not None:
                    reply = await self._send(conversation, reply.send)
                elif reply.act is not None:
                    reply = await self._act(conversation, reply.act)
                elif reply.forward is not None and assistant:
                    text, chat = await self._talk(assistant, reply.forward, chat, tag)
                    reply = conversation.said(text)
        finally:
            self._hass.data[DISCUSSING] = None
        await self._announce(satellite_id, reply.text)

    @callback
    def _save_order(self, order: Order) -> None:
        """A spoken choice changes the same setting as the settings screen."""
        options = {**self._entry.options, CONF_ORDER: order.value}
        self._hass.config_entries.async_update_entry(self._entry, options=options)

    async def _ask(self, satellite_id: str, text: str) -> str | None:
        """Say text and listen. None means nothing was heard."""
        text = current().tidy(text)
        try:
            async with asyncio.timeout(_turn_limit(text)):
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
        conversation.focus, conversation.path = self._focus.project, self._focus.path
        snapshot = None
        questions = None
        report = None
        automaton = None
        composed = None
        card = None
        needs = conversation.needs(heard)
        client = self._entry.runtime_data
        try:
            if needs is Needs.SNAPSHOT:
                snapshot = await client.snapshot(conversation.focus)
            elif needs is Needs.QUESTIONS:
                questions = list(await client.questions())
                scope = conversation.wanted_card(heard)
                if scope is not None:
                    card = await read_card(client, scope)
            elif needs is Needs.CARD:
                item = conversation.wanted_card(heard)
                assert item is not None, "an item was asked for"
                card = await self._read_item(item, parse(heard).kind in _SETTING)
            elif needs is Needs.CHILDREN:
                children = conversation.wanted_children(heard)
                assert children is not None, "a list inside an item was asked for"
                try:
                    report = await read_children(client, *children)
                except DatawatchMissingError:
                    report = Report(
                        t("datawatch no longer has the {item}.", item=children[0].spoken())
                    )
            elif needs is Needs.FIND_ITEM:
                search = conversation.wanted_item_search(heard)
                assert search is not None, "an item was named"
                report = await search_items(client, *search, conversation.focus, conversation.path)
                matches = conversation.matching(report.refs, *search)
                if len(matches) == 1:
                    card = await self._read_item(matches[0], True)
            elif needs is Needs.AUTOMATON:
                wanted = conversation.wanted_automaton(heard)
                assert wanted is not None, "an automaton was asked for"
                automaton = await read_automaton(client, wanted)
            elif needs is Needs.SEARCH:
                automaton, report = await find(client, parse(heard).name or "")
            elif needs is Needs.CUSTOM:
                chosen = conversation.wanted_report(heard)
                assert chosen is not None, "a report was named"
                composed = await run(client, chosen, conversation.focus)
            elif needs is Needs.REPORT:
                topic = topic_of(heard)
                assert topic is not None, "a report was asked for"
                if conversation.focus is not None:
                    names = await client.project_names()
                    if conversation.focus not in names:
                        gone = conversation.focus
                        conversation.focus, conversation.path = None, ()
                        await self._focus.async_set(None)
                        report = await build(client, topic, None, order=conversation.order)
                        notice = t(
                            "Project {project} no longer exists, so the focus is cleared.",
                            project=gone,
                        )
                        report = Report(
                            f"{notice} {report.summary}",
                            report.items,
                        )
                if report is None:
                    report = await build(
                        client,
                        topic,
                        conversation.focus,
                        conversation.report_scope(topic),
                        conversation.order,
                    )
        except DatawatchCertificateError:
            return Reply(t(_CERTIFICATE), ends=True)
        except DatawatchAuthError:
            return Reply(t(_REFUSED), ends=True)
        except DatawatchError:
            _LOGGER.warning("datawatch could not be read", exc_info=True)
        reply = conversation.hear(heard, snapshot, questions, report, automaton, composed, card)
        await self._focus.async_set(conversation.focus, conversation.path)
        return reply

    async def _read_item(self, item: Item, to_focus: bool) -> Card:
        """One item. Before focusing it, a project datawatch does not register is dropped."""
        client = self._entry.runtime_data
        card = await read_card(client, item)
        if not (to_focus and card is not GONE and card.project):
            return card
        if card.project in await client.project_names():
            return card
        return replace(card, project="")

    async def _send(self, conversation: Conversation, draft: Draft) -> Reply:
        """Send an answer the user has just confirmed, and say what happened."""
        client = self._entry.runtime_data
        option = draft.option.id if draft.option else None
        try:
            try:
                still_open = await client.question_is_open(draft.question.id)
            except DatawatchCertificateError, DatawatchAuthError:
                raise
            except DatawatchError:
                _LOGGER.warning("datawatch could not be read before answering", exc_info=True)
                return conversation.sent(t(_NOT_CHECKED))
            if not still_open:
                return conversation.sent(t(_ALREADY_CLOSED))
            await client.answer(draft.question.id, option, draft.quote)
        except DatawatchCertificateError:
            return Reply(t(_CERTIFICATE), ends=True)
        except DatawatchAuthError:
            return Reply(t(_REFUSED), ends=True)
        except DatawatchClosedError:
            return conversation.sent(t(_ALREADY_CLOSED))
        except DatawatchSecretError:
            return conversation.sent(t(_SECRET))
        except DatawatchRefusedError:
            _LOGGER.warning("datawatch refused an answer", exc_info=True)
            return conversation.sent(t(_NOT_ACCEPTED))
        except DatawatchError:
            _LOGGER.warning("An answer may not have reached datawatch", exc_info=True)
            return conversation.sent(t(_UNSURE))
        return conversation.sent(t(_SENT))

    async def _act(self, conversation: Conversation, action: Action) -> Reply:
        """Carry out an action the user has just confirmed, and say what happened."""
        try:
            outcome = await perform(self._entry.runtime_data, action, SESSION_SEND)
        except DatawatchCertificateError:
            return Reply(t(_CERTIFICATE), ends=True)
        except DatawatchAuthError:
            return Reply(t(_REFUSED), ends=True)
        return conversation.sent(outcome)

    async def _talk(
        self, assistant: str, words: str, chat: str | None, tag: str
    ) -> tuple[str, str | None]:
        """Pass talk that is not a command to the AI assistant. Returns its reply."""
        data = {"agent_id": assistant, "text": words, "language": tag}
        if chat is not None:
            data["conversation_id"] = chat
        try:
            # The assistant's tools would otherwise inherit the voice language: what they
            # give an AI is always in English.
            with speaking(for_tag("en")):
                async with asyncio.timeout(ASSISTANT_LIMIT):
                    result = await self._hass.services.async_call(
                        "conversation", "process", data, blocking=True, return_response=True
                    )
            response: Any = (result or {})["response"]
            if response.get("response_type") == "error":
                _LOGGER.warning("The AI assistant reported an error: %s", response)
                return t(_NO_ASSISTANT), chat
            speech = response.get("speech", {}).get("plain", {}).get("speech", "")
        except Exception:
            _LOGGER.warning("The AI assistant could not be asked", exc_info=True)
            return t(_NO_ASSISTANT), chat
        following = (result or {}).get("conversation_id")
        return str(speech).strip() or t(_SILENT_ASSISTANT), str(following) if following else chat

    async def _announce(self, satellite_id: str, text: str) -> None:
        """Say text without listening. A device that cannot is only logged."""
        text = current().tidy(text)
        try:
            async with asyncio.timeout(_turn_limit(text)):
                await self._hass.services.async_call(
                    _SATELLITE,
                    "announce",
                    {"entity_id": satellite_id, "message": text, "preannounce": False},
                    blocking=True,
                )
        except HomeAssistantError, TimeoutError:
            _LOGGER.warning("Could not speak on the voice device", exc_info=True)
