"""Single automata: choosing one, why it is stuck, and its tasks. Data is made up."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import aiohttp
import pytest
from aiohttp import web
from fake_datawatch import Fake, made_up_attention, serve
from homeassistant.core import HomeAssistant
from test_assistant import call, choose, posts
from test_voice import Certificate, FakeSatellite, visit, voice_test

from custom_components.datawatch.api import DatawatchClient, DatawatchError
from custom_components.datawatch.voice import automata, reports
from custom_components.datawatch.voice.automata import Automaton, Task
from custom_components.datawatch.voice.conversation import Conversation, Needs
from custom_components.datawatch.voice.phrases import Command, Kind, parse
from custom_components.datawatch.voice.reports import Held, Listed, Report

FENCE = Automaton(
    "a2",
    "Paint the fence.",
    "blocked",
    "oak",
    "the paint ran out",
    tasks=(
        Task("Buy paint", "completed"),
        Task("Paint it", "blocked"),
        Task("Tidy up", "", "waiting for the painting"),
    ),
)
NEED_NUMBER = "Say attention, running or held items, then a number."


@pytest.mark.parametrize(
    ("heard", "command"),
    [
        ("Why is two blocked?", Command(Kind.WHY, number=2)),
        ("why 3", Command(Kind.WHY, number=3)),
        ("Why did number one fail", Command(Kind.WHY, number=1)),
        ("Why is that one blocked?", Command(Kind.WHY)),
        ("Tasks for two", Command(Kind.TASKS, number=2)),
        ("progress of one", Command(Kind.PROGRESS, number=1)),
        ("Tell me about two", Command(Kind.PICK, number=2)),
        ("about number to", Command(Kind.PICK, number=2)),
        ("Tell me about the fence", Command(Kind.ABOUT, name="the fence")),
        ("What's on hold?", Command(Kind.HELD)),
        ("what is running", Command(Kind.RUNNING)),
    ],
)
def test_ways_of_asking(heard: str, command: Command) -> None:
    assert parse(heard) == command


def test_words_about_an_automaton() -> None:
    assert automata.summary(FENCE) == (
        "Paint the fence: blocked. Project oak. 1 of 3 tasks completed. The rest: 1 blocked "
        "and 1 not started. Say why, or tasks."
    )
    assert automata.why(FENCE) == (
        "Paint the fence is blocked. datawatch says: the paint ran out. 1 task is stuck. "
        "First: Paint it, blocked."
    )
    assert automata.tasks(FENCE).items[2] == "Task 3, Tidy up: not started."
    assert automata.progress(Automaton("x", "x", "draft")) == "It has no tasks."
    assert automata.tasks(Automaton("x", "x", "draft")).summary == "x has no tasks."


def test_why_never_guesses() -> None:
    quiet = Automaton("x", "Quiet", "paused", tasks=(Task("a", "completed"),))
    assert automata.why(quiet) == "Quiet is paused. datawatch gives no reason."
    held = Automaton("x", "Seed", "draft", hold="waiting for spring")
    assert automata.why(held) == "Seed is draft. It is on hold: waiting for spring."
    waiting = Automaton("x", "W", "running", tasks=(Task("b", "queued", "waiting for a"),))
    assert automata.why(waiting) == "W is running. For the task b: waiting for a."
    long = Automaton("x", "L", "blocked", reason="word " * 300)
    assert automata.why(long).endswith("word, and more. See datawatch for the rest.")


def test_running_and_held_lines() -> None:
    run = reports.running([Listed("r", "Errand", "oak", 1, 4)], 1, None)
    assert run == Report(
        "1 automaton is running across all projects.",
        ("1, Errand, project oak, 1 of 4 tasks completed.",),
        ("r",),
    )
    assert reports.running([], 0, "oak").summary == "No automata are running in project oak."
    held = reports.held([Held("h", "Tree", "spring.", project="elm"), Held("g", "Gate")], 9)
    assert held.summary == (
        "9 items are on hold, across all projects. For a full reason say why and its number."
    )
    long = reports.held([Held("a", "A", "First part. Second part."), Held("b", "B", "go " * 60)], 2)
    assert long.items[0] == "1, A. Reason: First part."
    assert long.items[1].endswith("go, and more.") and len(long.items[1]) < 130
    assert held.items == (
        "1, Tree, project elm. Reason: spring.",
        "2, Gate. No reason given.",
    )
    assert reports.held([], 0).summary == "Nothing is on hold."


def listed() -> Conversation:
    conversation = Conversation()
    conversation.enter()
    report = Report("5.", ("1.", "2.", "3.", "4.", "5."), ("a", "b", "c", "d", "e"))
    conversation.hear("attention", None, report=report)
    return conversation


@pytest.mark.parametrize("words", ["two", "number two", "about two", "why two", "tasks for two"])
def test_a_number_chooses_from_the_list(words: str) -> None:
    conversation = listed()
    assert conversation.needs(words) is Needs.AUTOMATON
    assert conversation.wanted_automaton(words) == "b"


def test_only_numbers_already_read_can_be_chosen() -> None:
    conversation = listed()
    assert conversation.wanted_automaton("four") is None
    assert conversation.hear("why four", None).text == NEED_NUMBER
    conversation.hear("more", None)
    assert conversation.wanted_automaton("four") == "d"


def test_why_tasks_and_progress_follow_the_chosen_one() -> None:
    conversation = listed()
    assert conversation.hear("why", None).text == NEED_NUMBER
    assert conversation.hear("two", None, automaton=FENCE).text == automata.summary(FENCE)
    assert conversation.wanted_automaton("why") == "a2", "read again, so it is fresh"
    assert conversation.hear("why", None, automaton=FENCE).text == automata.why(FENCE)
    assert conversation.hear("progress", None, automaton=FENCE).text == automata.progress(FENCE)
    tasks = conversation.hear("tasks", None, automaton=FENCE).text
    assert "Task 1, Buy paint: completed." in tasks
    assert conversation.wanted_automaton("two") is None, "task numbers do not choose"
    assert conversation.wanted_automaton("why") == "a2"
    assert conversation.hear("why", None).text.startswith("I can't reach datawatch")


def test_a_pending_answer_is_never_replaced_by_choosing_an_automaton() -> None:
    from custom_components.datawatch.voice.questions import Option, Question

    conversation = listed()
    conversation.hear("two", None, automaton=FENCE)
    question = Question("q", "Q", (Option("y", "Yes"), Option("n", "No")))
    conversation.hear("questions", None, [question])
    assert conversation.wanted_automaton("two") is None, "on a question, two is an option"
    assert "option 2" in conversation.hear("two", None).text
    reply = conversation.hear("why two", None)
    assert reply.text == "Not sent yet. Say confirm answer, or cancel."
    sent = conversation.hear("confirm answer", None).send
    assert sent is not None and sent.option == question.options[1]


def test_voice_from_a_list_to_the_reason_and_tasks(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await visit(
            hass, satellite,
            "what needs my attention", "why is one blocked", "tasks", "progress",
            "whats running", "whats on hold", "tell me about one", "why", "stop",
        )  # fmt: skip
        said = satellite.asked[1:]
        assert "datawatch says: the made-up paint ran out." in said[1]
        assert "an old note" not in said[1]
        assert said[2].startswith("1 of 3 tasks completed.")
        assert said[3].startswith("1 of 3 tasks completed.")
        assert said[4].startswith("1 automaton is running across all projects.")
        assert said[5].startswith("7 items are on hold, across all projects.")
        assert "Reason: waiting for spring." in said[5]
        assert said[6].startswith("Plant the made-up tree: draft.")
        assert "It is on hold: waiting for spring." in said[7]
        assert posts(fake) == []

    voice_test(certificate, tmp_path, body)


def test_voice_search_by_name(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await visit(
            hass, satellite,
            "tell me about the made up tree", "tell me about paint", "one",
            "tell me about submarines", "stop",
        )  # fmt: skip
        said = satellite.asked[1:]
        assert said[0].startswith("Plant the made-up tree: draft.")
        assert said[1].startswith("I found 2 matching paint. Say a number.")
        assert said[2].startswith("Paint the made-up fence: blocked.")
        assert said[3].startswith("I couldn't find submarines among")
        unfiltered = [
            q for _, path, q, _ in fake.seen
            if path == "/api/autonomous/prds" and "status" not in q
        ]  # fmt: skip
        assert unfiltered == [], "the slow unfiltered list is never read"

    voice_test(certificate, tmp_path, body)


def test_an_automaton_that_cannot_be_read(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        fake.attention = [made_up_attention("gone", "Vanished", "blocked")]
        await visit(hass, satellite, "attention", "one", "stop")
        assert satellite.asked[2].startswith("I can't reach datawatch.")

    voice_test(certificate, tmp_path, body)


def test_the_tools(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await choose(hass, "conversation.home_assistant")
        one, _ = await call(hass, "automaton", name="fence")
        assert "the made-up paint ran out" in one["why"]
        assert len(one["tasks"]) == 3 and one["more_tasks"] == 0
        many, _ = await call(hass, "automaton", name="paint")
        assert len(many["matches"]) == 2
        running, _ = await call(hass, "work", topic="running")
        assert running["lines"] and "limited_to_project" not in running

        await hass.data[FOCUS].async_set("oak")
        focused, _ = await call(hass, "work", topic="plans")
        assert focused["limited_to_project"] == "oak"
        assert "Say that" in focused["tell_the_user"]
        everything, _ = await call(hass, "work", topic="plans", project="all")
        assert everything["summary"].startswith("2 current plans in 1 project.")
        assert "limited_to_project" not in everything
        chosen, _ = await call(hass, "work", topic="plans", project="oak")
        assert "limited_to_project" not in chosen
        assert posts(fake) == []

    from custom_components.datawatch.const import FOCUS

    voice_test(certificate, tmp_path, body)


@pytest.mark.parametrize(
    ("path", "reply", "method", "args"),
    [
        ("/api/autonomous/prds", {"prds": "none"}, "running", ()),
        ("/api/autonomous/prds", {"prds": [], "total": None}, "running", ()),
        ("/api/autonomous/held", {"held": [{"id": 1}], "total": 1}, "held_items", ()),
        ("/api/autonomous/prds/a2", {"id": "a2"}, "automaton", ("a2",)),
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


@pytest.mark.parametrize("ident", ["..", "a/b", "a?x=1", ""])
def test_an_automaton_id_cannot_change_the_address(certificate: Certificate, ident: str) -> None:
    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        with pytest.raises(DatawatchError, match="automaton id"):
            await DatawatchClient(session, url, certificate[2]).automaton(ident)
        assert fake.seen == []

    serve(certificate, body)
