"""Sessions and finished work. Data is made up."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import aiohttp
import pytest
from aiohttp import web
from fake_datawatch import Fake, serve
from homeassistant.core import HomeAssistant
from test_assistant import call, choose, posts
from test_voice import Certificate, FakeSatellite, visit, voice_test

from custom_components.datawatch.api import DatawatchClient, DatawatchError
from custom_components.datawatch.voice import work
from custom_components.datawatch.voice.conversation import Conversation
from custom_components.datawatch.voice.model import Snapshot
from custom_components.datawatch.voice.work import Delivery, Finished, Session

NOW = datetime(2026, 11, 2, 12, tzinfo=UTC)
RAW = "raw terminal text"
EARLIER = (NOW - timedelta(hours=2)).isoformat()
TOTALS = [("waiting_input", 2), ("running", 1), ("failed", 0)]


@pytest.mark.parametrize(
    ("back", "said"),
    [
        (timedelta(seconds=5), "just now"),
        (timedelta(minutes=2), "2 minutes ago"),
        (timedelta(hours=1, minutes=40), "1 hour ago"),
        (timedelta(days=3, hours=2), "3 days ago"),
    ],
)
def test_ages(back: timedelta, said: str) -> None:
    assert work.age((NOW - back).isoformat(), NOW) == said


@pytest.mark.parametrize("moment", ["", "yesterday", "2026-11-02T11:00:00"])
def test_a_time_that_cannot_be_understood_is_left_out(moment: str) -> None:
    assert work.age(moment, NOW) == ""


def test_session_lines_and_details() -> None:
    rows = [
        Session(
            "a",
            "Helper.",
            "waiting_input",
            "oak",
            "a-model",
            (NOW - timedelta(hours=2)).isoformat(),
        ),
        Session("b", state="waiting_input"),
    ]
    report = work.sessions(TOTALS, rows, None, NOW)
    assert report.summary == "All projects: sessions, 2 waiting for input, 1 running and 0 failed."
    assert report.items == (
        "1, session named Helper, waiting for input, project oak, active 2 hours ago.",
        "2, session named unnamed, waiting for input.",
    )
    assert report.details[0] == (
        "Session named Helper: waiting for input. Project oak. It uses a-model. Last activity "
        "2 hours ago. To see what it said, open it in datawatch."
    )
    assert work.sessions(TOTALS, [], "oak", NOW).summary.startswith("Project oak: sessions,")


def test_finished_lines_and_what_was_delivered() -> None:
    report = work.finished(
        [Finished("a", "Shed.", True, "9.9"), Finished("b", "Path", False),
         Finished("c", "Stars"), Finished("d", "Gate", True)],
        40, None,
    )  # fmt: skip
    assert report.summary == (
        "40 automata have completed across all projects. The most recently updated come "
        "first, which may not be the order they finished."
    )
    assert report.items == (
        "1, Shed, shipped in 9.9.", "2, Path, not shipped.", "3, Stars.", "4, Gate, shipped."
    )  # fmt: skip
    assert work.finished([], 0, "oak").summary == "No automata have completed in project oak."
    assert work.delivery("Shed", "completed", 2, 2, Delivery(2, 1, 3)) == (
        "Shed: completed. 2 of 2 tasks completed. It changed 2 files in 1 package, and added "
        "3 tests."
    )
    assert work.delivery("S", "waiting_review", 0, 0, None) == (
        "S: waiting review. datawatch has no change record for it."
    )


def listed() -> Conversation:
    conversation = Conversation()
    conversation.enter()
    conversation.hear("sessions", None, report=work.sessions(
        TOTALS, [Session("a", "Helper"), Session("b", "Other")], None, NOW
    ))  # fmt: skip
    return conversation


@pytest.mark.parametrize("words", ["two", "number two", "tell me about two"])
def test_choosing_a_session_needs_no_read(words: str) -> None:
    conversation = listed()
    assert conversation.needs(words).name == "NOTHING"
    assert conversation.hear(words, None).text.startswith("Session named Other")


def test_a_session_has_no_tasks_or_reason() -> None:
    conversation = listed()
    assert conversation.hear("why two", None).text.startswith("That is a session.")
    assert conversation.hear("nine", None).text.startswith("I haven't read a number 9.")


def test_a_new_list_forgets_session_details() -> None:
    conversation = listed()
    conversation.hear("list projects", Snapshot(projects=("oak",)))
    assert conversation.wanted_automaton("one") is None
    assert not conversation.hear("tell me about one", None).text.startswith("Session")


def test_voice_sessions_and_finished_work_never_read_terminal_output(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await visit(
            hass, satellite,
            "sessions", "one", "waiting sessions", "running sessions", "failed sessions",
            "what finished", "one", "results", "results for two",
            "tell me about stars", "stop",
        )  # fmt: skip
        said = satellite.asked[1:]
        assert said[0].startswith(
            "All projects: sessions, 3 waiting for input, 2 running and 5 failed."
        )
        assert said[1].startswith("Session named Made-up helper: waiting for input. Project oak.")
        assert said[2].startswith(
            "All projects: sessions, 3 waiting for input. 1, session named Made-up"
        )
        assert said[3].startswith(
            "All projects: sessions, 2 running. 1, session named Made-up runner"
        )
        assert said[4] == "All projects: sessions, 5 failed."
        assert "1, Build the made-up shed, shipped in 9.9.9." in said[5]
        assert said[6].startswith("Build the made-up shed: completed.")
        assert "It changed 2 files in 1 package, and added 3 tests." in said[7]
        assert "datawatch has no change record for it." in said[8]
        assert said[9].startswith("Count the made-up stars: completed.")
        assert not any(RAW in reply for reply in satellite.asked)
        paths = {path for _, path, *_ in fake.seen}
        assert not paths & {"/api/sessions/response", "/api/sessions/prompt", "/api/output"}
        assert posts(fake) == []

    voice_test(certificate, tmp_path, body)


def test_the_tools_give_session_facts_only(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await choose(hass, "conversation.home_assistant")
        for topic in ("sessions", "waiting_sessions", "running_sessions", "failed_sessions"):
            found, _ = await call(hass, "work", topic=topic)
            assert RAW not in str(found)
            assert "A name is a title, not a message." in found["what_is_not_here"], topic
        found, _ = await call(hass, "work", topic="sessions")
        assert found["lines"][0].startswith("1, session named ")
        other, _ = await call(hass, "work", topic="plans")
        assert "what_is_not_here" not in other
        done, _ = await call(hass, "work", topic="finished", project="oak")
        assert "shipped in 9.9.9" in done["lines"][0]
        one, _ = await call(hass, "automaton", name="made-up shed")
        assert "It changed 2 files" in one["delivered"]
        paths = {path for _, path, *_ in fake.seen}
        assert not paths & {"/api/sessions/response", "/api/sessions/prompt"}

    voice_test(certificate, tmp_path, body)


@pytest.mark.parametrize(
    ("path", "reply", "method", "args"),
    [
        ("/api/sessions", {"sessions": [{"name": "x"}], "total": 1}, "sessions", ("running",)),
        ("/api/autonomous/prds", {"prds": [{"title": "No id"}], "total": 1}, "finished", ()),
        ("/api/autonomous/prds/a/change-record", [], "delivery", ("a",)),
    ],
)
def test_unexpected_replies_raise(
    certificate: Certificate, path: str, reply: Any, method: str, args: tuple[str, ...]
) -> None:
    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        with pytest.raises(DatawatchError):
            await getattr(DatawatchClient(session, url, certificate[2]), method)(*args)

    fake = Fake()
    fake.override[path] = lambda: web.json_response(reply)
    serve(certificate, body, fake)


def test_a_change_record_may_be_counts_or_lists(certificate: Certificate) -> None:
    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        client = DatawatchClient(session, url, certificate[2])
        assert await client.delivery("f9") == Delivery(4, 2, 0)
        assert await client.delivery("none") is None
        with pytest.raises(DatawatchError, match="automaton id"):
            await client.delivery("..")

    fake = Fake()
    fake.change_records["f9"] = {"files": 4, "packages": {"a": 1, "b": 2}, "tests_added": "?"}
    serve(certificate, body, fake)
