"""Reports: what needs attention, plans, what is next and automations. Data is made up."""

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
from custom_components.datawatch.voice import reports
from custom_components.datawatch.voice.conversation import Conversation, Needs, Topic, topic_of
from custom_components.datawatch.voice.reports import (
    Attention,
    Automation,
    Overview,
    Plan,
    Report,
)

OAK = Overview("oak", (("in_progress", 1), ("planned", 1)), 2, 3, 2, 7, "Dig", "Roots")
ELM = Overview("elm")


@pytest.mark.parametrize(
    ("words", "topic"),
    [
        ("What needs my attention?", Topic.ATTENTION),
        ("attention", Topic.ATTENTION),
        ("How many plans do we have?", Topic.PLANS),
        ("Plans.", Topic.PLANS),
        ("overview", Topic.OVERVIEW),
        ("What's next?", Topic.NEXT),
        ("automations", Topic.AUTOMATIONS),
        ("next", None),
        ("list projects", None),
    ],
)
def test_what_asks_for_which_report(words: str, topic: Topic | None) -> None:
    assert topic_of(words) is topic
    if topic is not None:
        assert Conversation().needs(words) is Needs.REPORT


def test_attention_is_ordered_counted_and_says_it_covers_everything() -> None:
    report = reports.attention(
        [
            Attention("Old.", "cancelled", 2),
            Attention("Paused one", "paused"),
            Attention("Review me", "needs_review", 1),
            Attention("Stuck", "blocked"),
        ]
    )
    assert report.summary == (
        "4 automata need attention, across all projects: 1 blocked, 1 waiting for review, "
        "1 paused and 1 finished or set aside with tasks held for review."
    )
    assert report.items == (
        "1, Stuck: blocked.",
        "2, Review me: waiting for review, 1 task held for review.",
        "3, Paused one: paused.",
        "4, Old: cancelled, 2 tasks held for review.",
    )
    assert reports.attention([]) == Report("Nothing needs your attention.")
    assert reports.attention([Attention("x", "blocked")]).summary.startswith("1 automaton needs")


def test_plan_counts_and_lists() -> None:
    everywhere = reports.plans_everywhere([ELM, OAK])
    assert everywhere.summary == "2 current plans in 1 project. Also 3 archived."
    assert everywhere.items == ("Project oak: 2 plans, 1 in progress and 1 planned.",)
    assert reports.plans_everywhere([ELM]).summary == "There are no current plans."
    one = reports.plans_of("oak", [Plan("Roots", "in_progress", 2, 5), Plan("B", "open")], 2, 3)
    assert one.items == (
        "Plan 1, Roots: in progress, 2 of 5 automata done.",
        "Plan 2, B: open.",
    )
    assert reports.plans_of("elm", [], 0, 0).summary == "Project elm has no current plans."


def test_overview_and_next() -> None:
    assert reports.overview(OAK).summary == (
        "Project oak: 2 plans, 1 in progress and 1 planned. 2 of 7 automata done. "
        "3 plans archived. Next: Dig, in the plan Roots."
    )
    assert reports.overview(ELM).summary == "Project elm: 0 plans. Nothing is marked as next."
    assert reports.next_in(OAK).summary == "Project oak. Next: Dig, in the plan Roots."
    assert reports.next_everywhere([ELM, OAK]).items == (
        "Project oak. Next: Dig, in the plan Roots.",
    )
    assert reports.next_everywhere([ELM]).items == ()


def test_automations_are_counted_and_unfinished_ones_listed_in_datawatch_s_order() -> None:
    report = reports.automations(
        [
            Automation("b", "draft"),
            Automation("done", "completed"),
            Automation("a", "draft", 2),
            Automation("c", "blocked", 1),
            Automation("gone", "cancelled"),
        ],
        None,
    )
    assert report.summary == (
        "All projects: 5 automations, 1 blocked, 2 draft, 1 completed and 1 cancelled."
    )
    assert report.items == (
        "c: blocked, 1 member.",
        "a: draft, 2 members.",
        "b: draft, 0 members.",
    )
    assert reports.automations([], "oak").summary == "Project oak: no automations."


def test_reports_are_read_three_lines_at_a_time() -> None:
    conversation = Conversation()
    conversation.enter()
    report = Report("Seven.", tuple(f"{n}." for n in range(1, 8)))
    assert conversation.hear("plans", None, report=report).text == "Seven. 1. 2. 3. Say more."
    assert conversation.hear("more", None).text == "4. 5. 6. Say more."
    assert conversation.hear("repeat", None).text == "4. 5. 6. Say more."
    assert conversation.hear("next", None).text == "7. That is all."
    assert conversation.hear("more", None).text == "That is the end of the list."
    assert conversation.hear("plans", None).text.startswith("I can't reach datawatch")


def test_more_follows_whatever_was_read_last() -> None:
    conversation = Conversation()
    conversation.enter()
    conversation.hear("plans", None, report=Report("S.", ("1.", "2.", "3.", "4.")))
    conversation.hear("questions", None, [])
    assert conversation.hear("more", None).text == "There is no list yet. Say list projects."


def test_voice_reports_with_and_without_a_focus(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await visit(
            hass, satellite,
            "what needs my attention", "how many plans do we have", "automations",
            "set project oak", "plans", "overview", "what's next", "automations", "stop",
        )  # fmt: skip
        said = satellite.asked[1:]
        assert said[0].startswith("3 automata need attention, across all projects")
        assert "1, Paint the made-up fence: blocked." in said[0]
        assert said[1].startswith("2 current plans in 1 project.")
        assert said[2].startswith("All projects: 4 automations")
        assert said[4].startswith("Project oak has 2 current plans.")
        assert "Plan 1, Roots: in progress, 2 of 5 automata done." in said[4]
        assert said[5].startswith("Project oak: 2 plans")
        assert said[6] == "Project oak. Next: Dig the made-up hole, in the plan Roots."
        assert said[7].startswith("Project oak: 4 automations")
        filtered = [q for _, path, q, _ in fake.seen if path == "/api/automations"]
        assert filtered == [{}, {"project": "oak"}]
        assert posts(fake) == []

    voice_test(certificate, tmp_path, body)


def test_a_focus_that_disappeared_is_cleared_before_a_report(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await visit(hass, satellite, "set project oak", "stop")
        fake.override["/api/projects"] = lambda: web.json_response([{"name": "elm"}])
        await visit(hass, satellite, "automations", "where am i", "stop")
        assert satellite.asked[1].startswith(
            "Project oak no longer exists, so the focus is cleared. All projects:"
        )
        assert satellite.asked[2] == "No focus. Showing everything."

    voice_test(certificate, tmp_path, body)


def test_a_report_that_cannot_be_read_says_so(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        fake.override["/api/autonomous/attention"] = web.Response(status=500)
        await visit(hass, satellite, "attention", "stop")
        assert satellite.asked[1].startswith("I can't reach datawatch.")

    voice_test(certificate, tmp_path, body)


def test_the_work_tool(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await choose(hass, "conversation.home_assistant")
        plans, _ = await call(hass, "work", topic="plans")
        assert plans["summary"].startswith("2 current plans")
        oak, _ = await call(hass, "work", topic="plans", project="OAK")
        assert len(oak["lines"]) == 2 and oak["more_lines"] == 0
        missing, _ = await call(hass, "work", topic="overview", project="nowhere")
        assert missing["note"] == "There is no project named nowhere."
        fake.attention = [made_up_attention(str(n), f"Job {n}", "blocked") for n in range(20)]
        first, _ = await call(hass, "work", topic="attention")
        assert (len(first["lines"]), first["more_lines"]) == (15, 5)
        rest, _ = await call(hass, "work", topic="attention", start=15)
        assert (len(rest["lines"]), rest["more_lines"]) == (5, 0)
        for topic in ("overview", "next", "automations"):
            reply, failed = await call(hass, "work", topic=topic)
            assert reply["summary"] and not failed
        reply, failed = await call(hass, "work", topic="secrets")
        assert failed
        assert posts(fake) == []

    voice_test(certificate, tmp_path, body)


def test_attention_is_chosen_as_datawatch_s_web_app_chooses(
    certificate: Certificate,
) -> None:
    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        rows = await DatawatchClient(session, url, certificate[2]).attention()
        assert [r.title for r in rows] == ["Keep", "Held"]
        assert [r.held_tasks for r in rows] == [0, 1]

    fake = Fake()
    fake.attention = [
        made_up_attention("1", "Keep", "blocked"),
        made_up_attention("1", "Same again", "blocked"),
        made_up_attention("2", "Finished", "completed"),
        made_up_attention("3", "Held", "archived", review_needed=True),
        made_up_attention("4", "A template", "blocked", is_template=True),
    ]
    serve(certificate, body, fake)


@pytest.mark.parametrize(
    ("path", "reply", "method", "args"),
    [
        ("/api/autonomous/attention", {"items": []}, "attention", ()),
        ("/api/autonomous/attention", {"statuses": [], "items": [{}]}, "attention", ()),
        ("/api/automations", {"automations": []}, "automations", ()),
        ("/api/projects/oak/plans", {"plans": [{"title": 1}]}, "plans", ("oak",)),
        ("/api/projects/oak/overview-summary", {"counts": []}, "overview", ("oak",)),
        (
            "/api/projects/oak/overview-summary",
            {"counts": {"plans": {"total": "2"}}, "progress": {"automata": {}}},
            "overview",
            ("oak",),
        ),
    ],
)
def test_unexpected_work_replies_raise(
    certificate: Certificate, path: str, reply: Any, method: str, args: tuple[str, ...]
) -> None:
    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        with pytest.raises(DatawatchError):
            await getattr(DatawatchClient(session, url, certificate[2]), method)(*args)

    fake = Fake()
    fake.override[path] = lambda: web.json_response(reply)
    serve(certificate, body, fake)


@pytest.mark.parametrize("name", ["..", ".", ""])
def test_a_project_name_cannot_change_the_address(certificate: Certificate, name: str) -> None:
    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        with pytest.raises(DatawatchError, match="project name"):
            await DatawatchClient(session, url, certificate[2]).plans(name)
        assert fake.seen == []

    serve(certificate, body)
