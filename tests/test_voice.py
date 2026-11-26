"""Datawatch mode in a real (throwaway) Home Assistant.

Home Assistant's own sentence matching and its ask-question and announce actions are used.
Only the microphone and speaker are fake: the pretend voice device "hears" a script of
text. Speech recognition and speech synthesis are not covered here.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import aiohttp
import pytest
from aiohttp import web
from fake_datawatch import Fake, make_certificate, serve
from ha_harness import add_datawatch, running_hass
from homeassistant.components import conversation
from homeassistant.components.assist_pipeline import (
    Pipeline,
    PipelineEvent,
    PipelineEventType,
    PipelineInput,
    PipelineRun,
    PipelineStage,
)
from homeassistant.components.assist_satellite import (
    AssistSatelliteAnnouncement,
    AssistSatelliteEntity,
    AssistSatelliteEntityFeature,
)
from homeassistant.components.assist_satellite.const import DATA_COMPONENT
from homeassistant.components.conversation.agent_manager import AgentManager
from homeassistant.components.conversation.const import DATA_COMPONENT as CONVERSATION_COMPONENT
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers import chat_session, intent
from homeassistant.helpers import issue_registry as ir
from homeassistant.setup import async_setup_component

from custom_components.datawatch import mode
from custom_components.datawatch.const import DOMAIN

Certificate = tuple[Path, Path, str]
CLOSING = "Closing datawatch."
UNREACHABLE = "I can't reach datawatch. Try again, or say stop."


class FakeSatellite(AssistSatelliteEntity):
    """Speaks into a list and hears from a script. None in the script means silence."""

    _attr_supported_features = (
        AssistSatelliteEntityFeature.ANNOUNCE | AssistSatelliteEntityFeature.START_CONVERSATION
    )

    def __init__(self, name: str) -> None:
        self.entity_id = f"assist_satellite.{name}"
        self.script: list[str | None] = []
        self.asked: list[str] = []
        self.announced: list[str] = []
        self.never_answers = False

    async def _resolve_announcement_media_id(
        self,
        message: str,
        media_id: str | None,
        preannounce_media_id: str | None = None,
    ) -> AssistSatelliteAnnouncement:
        return AssistSatelliteAnnouncement(message, "fake", "fake", None, "tts")

    async def async_announce(self, announcement: AssistSatelliteAnnouncement) -> None:
        self.announced.append(announcement.message)

    async def async_start_conversation(self, announcement: AssistSatelliteAnnouncement) -> None:
        self.asked.append(announcement.message)
        if self.never_answers:
            return
        words = self.script.pop(0) if self.script else None
        if words is not None:
            heard = {"stt_output": {"text": words}}
            self._internal_on_pipeline_event(PipelineEvent(PipelineEventType.STT_END, heard))
        self._internal_on_pipeline_event(PipelineEvent(PipelineEventType.RUN_END))

    def on_pipeline_event(self, event: PipelineEvent) -> None:
        pass

    def async_get_configuration(self) -> Any:
        raise NotImplementedError

    async def async_set_configuration(self, config: Any) -> None:
        raise NotImplementedError

    def busy(self) -> None:
        self._internal_on_pipeline_event(PipelineEvent(PipelineEventType.INTENT_START))


Body = Callable[[HomeAssistant, FakeSatellite, Fake], Awaitable[None]]


async def add_satellite(hass: HomeAssistant, name: str = "office") -> FakeSatellite:
    satellite = FakeSatellite(name)
    await hass.data[DATA_COMPONENT].async_add_entities([satellite])
    await hass.async_block_till_done()
    return satellite


def voice_test(
    certificate: Certificate, tmp_path: Path, body: Body, fake: Fake | None = None
) -> None:
    async def inner(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        async with running_hass(tmp_path) as hass:
            for component in ("homeassistant", "assist_satellite", "conversation"):
                assert await async_setup_component(hass, component, {})
            satellite = await add_satellite(hass)
            await add_datawatch(hass, url)
            fake.seen.clear()
            await body(hass, satellite, fake)

    serve(certificate, inner, fake)


async def say(hass: HomeAssistant, words: str, satellite_id: str | None) -> str:
    """What Home Assistant does with recognised speech. Returns the spoken reply."""
    result = await conversation.async_converse(
        hass, words, None, Context(), language="en", satellite_id=satellite_id
    )
    return str(result.response.speech.get("plain", {}).get("speech", ""))


async def visit(hass: HomeAssistant, satellite: FakeSatellite, *script: str | None) -> None:
    """Enter datawatch mode, speak the script, and wait for the mode to end."""
    satellite.script = list(script)
    satellite.asked.clear()
    satellite.announced.clear()
    assert await say(hass, "open datawatch", satellite.entity_id) == ""
    async with asyncio.timeout(10):
        await hass.async_block_till_done(wait_background_tasks=True)


@pytest.mark.parametrize(
    "words",
    ["open datawatch", "use datawatch", "datawatch", "Datawatch.", "open data watch", "Data watch"],
)
def test_entry_phrases_start_the_mode_with_nothing_else_spoken(
    certificate: Certificate, tmp_path: Path, words: str
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        satellite.script = ["stop"]
        assert await say(hass, words, satellite.entity_id) == ""
        await hass.async_block_till_done(wait_background_tasks=True)
        assert satellite.asked == ["Datawatch."]
        assert satellite.announced == [CLOSING]
        assert fake.seen == [], "entering and leaving read nothing"

    voice_test(certificate, tmp_path, body)


@pytest.mark.parametrize("words", ["what is datawatch doing", "open the garage", "status"])
def test_other_sentences_do_not_start_the_mode(
    certificate: Certificate, tmp_path: Path, words: str
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await say(hass, words, satellite.entity_id)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert satellite.asked == []
        assert fake.seen == []

    voice_test(certificate, tmp_path, body)


def test_a_visit_asks_listens_and_answers_without_the_wake_word(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await visit(hass, satellite, "status", "repeat", "close datawatch")
        status = (
            "New work is paused. 4 open questions, 3 sessions waiting for input and 2 running."
            " Say more detail for more."
        )
        assert satellite.asked == ["Datawatch.", status, status]
        assert satellite.announced == [CLOSING]
        assert {method for method, *_ in fake.seen} == {"GET"}

    voice_test(certificate, tmp_path, body)


def test_silence_asks_once_then_closes(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await visit(hass, satellite, None, None)
        assert satellite.asked == ["Datawatch.", "Still there?"]
        assert satellite.announced == [CLOSING]

    voice_test(certificate, tmp_path, body)


def test_the_focus_is_shared_by_voice_devices_and_survives_a_reload(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await visit(hass, satellite, "set project oak", "stop")
        kitchen = await add_satellite(hass, "kitchen")
        await visit(hass, kitchen, "stop")
        assert kitchen.asked == ["Datawatch. Focus: project oak."]

        (entry,) = hass.config_entries.async_entries(DOMAIN)
        assert await hass.config_entries.async_reload(entry.entry_id)
        await visit(hass, satellite, "unset", "stop")
        assert satellite.asked[0] == "Datawatch. Focus: project oak."
        await visit(hass, kitchen, "stop")
        assert kitchen.asked == ["Datawatch."]

    voice_test(certificate, tmp_path, body)


def test_removing_datawatch_forgets_the_focus(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await visit(hass, satellite, "set project oak", "stop")
        shared = mode.SharedFocus(hass)
        await shared.async_load()
        assert shared.project == "oak"
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        await hass.config_entries.async_remove(entry.entry_id)
        shared = mode.SharedFocus(hass)
        await shared.async_load()
        assert shared.project is None
        await say(hass, "open datawatch", satellite.entity_id)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert satellite.asked[-1] != "Datawatch."

    voice_test(certificate, tmp_path, body)


@pytest.mark.parametrize(
    ("status", "message", "stays"),
    [
        (500, UNREACHABLE, True),
        (401, "datawatch refused access. Check the token in Home Assistant. " + CLOSING, False),
    ],
)
def test_when_datawatch_fails_it_is_said_out_loud(
    certificate: Certificate, tmp_path: Path, status: int, message: str, stays: bool
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        fake.override["/api/pause"] = lambda: web.Response(status=status)
        await visit(hass, satellite, "status", "stop")
        if stays:
            assert satellite.asked == ["Datawatch.", message]
            assert satellite.announced == [CLOSING]
        else:
            assert satellite.asked == ["Datawatch."]
            assert satellite.announced == [message]

    voice_test(certificate, tmp_path, body)


def test_a_changed_certificate_ends_the_mode_and_says_why(
    certificate: Certificate, tmp_path: Path, tmp_path_factory: pytest.TempPathFactory
) -> None:
    other = make_certificate(tmp_path_factory.mktemp("other"), "other")

    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        hass.config_entries.async_update_entry(entry, data={**entry.data, "fingerprint": other[2]})
        assert await hass.config_entries.async_reload(entry.entry_id)
        await visit(hass, satellite, "status")
        assert satellite.announced == [
            "The datawatch certificate has changed. Check it in Home Assistant. " + CLOSING
        ]
        assert fake.seen == []

    voice_test(certificate, tmp_path, body)


def test_an_unexpected_fault_is_never_silent(
    certificate: Certificate, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        (entry,) = hass.config_entries.async_entries(DOMAIN)

        async def broken(focus: str | None) -> None:
            raise RuntimeError("made-up fault")

        monkeypatch.setattr(entry.runtime_data, "snapshot", broken)
        await visit(hass, satellite, "status")
        assert satellite.announced == ["Something went wrong in datawatch mode. " + CLOSING]

    voice_test(certificate, tmp_path, body)


def test_a_device_that_never_answers_does_not_hang_the_mode(
    certificate: Certificate, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(mode, "TURN_LIMIT", 0.2)

    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        satellite.never_answers = True
        await visit(hass, satellite)
        assert satellite.announced == [CLOSING]
        satellite.never_answers = False
        await visit(hass, satellite, "stop")
        assert satellite.asked == ["Datawatch."], "the device can be used again"

    voice_test(certificate, tmp_path, body)


def test_the_mode_waits_for_the_device_to_finish_the_first_request(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        satellite.busy()
        satellite.script = ["stop"]
        await say(hass, "open datawatch", satellite.entity_id)
        await say(hass, "open datawatch", satellite.entity_id)
        await asyncio.sleep(0.1)
        assert satellite.asked == []
        satellite.tts_response_finished()
        await hass.async_block_till_done(wait_background_tasks=True)
        assert satellite.asked == ["Datawatch."], "one visit, even if asked twice"

    voice_test(certificate, tmp_path, body)


def test_a_device_that_stays_busy_is_still_served(
    certificate: Certificate, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(mode, "IDLE_WAIT", 0.1)

    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        satellite.busy()
        await visit(hass, satellite, "stop")
        assert satellite.asked == ["Datawatch."]

    voice_test(certificate, tmp_path, body)


def test_unloading_stops_a_visit_in_progress(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        satellite.never_answers = True
        await say(hass, "open datawatch", satellite.entity_id)
        async with asyncio.timeout(5):
            while not satellite.asked:
                await asyncio.sleep(0.01)
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        async with asyncio.timeout(5):
            assert await hass.config_entries.async_unload(entry.entry_id)
            await hass.async_block_till_done(wait_background_tasks=True)
        assert satellite.announced == []

    voice_test(certificate, tmp_path, body)


def test_typed_chat_and_unsuitable_devices_are_told_why(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        assert await say(hass, "open datawatch", None) == (
            "Datawatch mode works from a voice device."
        )
        plain = FakeSatellite("plain")
        plain._attr_supported_features = AssistSatelliteEntityFeature.ANNOUNCE
        await hass.data[DATA_COMPONENT].async_add_entities([plain])
        for unsuitable in (plain.entity_id, "assist_satellite.missing"):
            assert await say(hass, "open datawatch", unsuitable) == (
                "This voice device can't hold a datawatch conversation."
            )

    voice_test(certificate, tmp_path, body)


def test_if_the_phrase_cannot_be_registered_home_assistant_shows_a_warning(
    certificate: Certificate, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Stands in for an upgrade that changes the Home Assistant code relied on."""

    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        registry = ir.async_get(hass)
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        assert registry.async_get_issue(DOMAIN, "voice_phrase_unavailable") is None
        with monkeypatch.context() as patch:
            patch.delattr(AgentManager, "register_trigger")
            assert await hass.config_entries.async_reload(entry.entry_id)
            issue = registry.async_get_issue(DOMAIN, "voice_phrase_unavailable")
            assert issue and issue.severity == ir.IssueSeverity.ERROR
        assert await hass.config_entries.async_reload(entry.entry_id)
        assert registry.async_get_issue(DOMAIN, "voice_phrase_unavailable") is None

    voice_test(certificate, tmp_path, body)


def test_the_warning_has_text() -> None:
    folder = Path(__file__).resolve().parents[1] / "custom_components" / "datawatch"
    issue = json.loads((folder / "translations" / "en.json").read_text())["issues"]
    assert issue["voice_phrase_unavailable"]["title"]
    assert issue["voice_phrase_unavailable"]["description"]


class FakeAiAssistant(conversation.ConversationEntity):
    """Stands in for an AI assistant, such as one backed by a language model."""

    _attr_supported_features = conversation.ConversationEntityFeature.CONTROL
    entity_id = "conversation.fake_ai"
    _attr_name = "Fake AI"

    def __init__(self) -> None:
        self.asked: list[str] = []

    @property
    def supported_languages(self) -> str:
        return "*"

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        self.asked.append(user_input.text)
        response = intent.IntentResponse(language=user_input.language)
        response.async_set_speech("The AI answered.")
        return conversation.ConversationResult(response=response)


async def through_pipeline(
    hass: HomeAssistant, words: str, satellite_id: str
) -> list[PipelineEvent]:
    """Home Assistant's voice pipeline from recognised text, with the AI as its assistant."""
    events: list[PipelineEvent] = []
    pipeline = Pipeline(
        conversation_engine=FakeAiAssistant.entity_id,
        conversation_language="en",
        language="en",
        name="Assistant with AI",
        stt_engine=None,
        stt_language=None,
        tts_engine=None,
        tts_language=None,
        tts_voice=None,
        wake_word_entity=None,
        wake_word_id=None,
        prefer_local_intents=True,
    )
    with chat_session.async_get_chat_session(hass, context=Context()) as session:
        run = PipelineRun(
            hass,
            context=Context(),
            pipeline=pipeline,
            start_stage=PipelineStage.INTENT,
            end_stage=PipelineStage.INTENT,
            event_callback=events.append,
        )
        request = PipelineInput(
            run=run, session=session, intent_input=words, satellite_id=satellite_id
        )
        await request.validate()
        await request.execute()
    return events


def test_with_an_ai_assistant_the_entry_phrase_never_reaches_the_ai(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        assistant = FakeAiAssistant()
        await hass.data[CONVERSATION_COMPONENT].async_add_entities([assistant])
        await hass.async_block_till_done()

        await through_pipeline(hass, "tell me a story", satellite.entity_id)
        assert assistant.asked == ["tell me a story"], "other speech goes to the AI"
        assert satellite.asked == []

        satellite.script = ["stop"]
        events = await through_pipeline(hass, "Open datawatch.", satellite.entity_id)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert assistant.asked == ["tell me a story"]
        assert satellite.asked == ["Datawatch."]
        (ended,) = [e for e in events if e.type is PipelineEventType.INTENT_END]
        assert ended.data
        speech = ended.data["intent_output"]["response"]["speech"]
        assert speech.get("plain", {}).get("speech", "") == ""

    voice_test(certificate, tmp_path, body)
