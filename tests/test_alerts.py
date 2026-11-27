"""Voice alerts: titles only, newest first, limited to a focused session. Data is made up."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from fake_datawatch import RAW_BODY, Fake, made_up_alert
from homeassistant.core import HomeAssistant
from test_assistant import call, choose, posts
from test_voice import Certificate, FakeSatellite, visit, voice_test

from custom_components.datawatch.voice import work
from custom_components.datawatch.voice.conversation import Conversation, Needs, Topic, topic_of
from custom_components.datawatch.voice.items import Item
from custom_components.datawatch.voice.work import Alert

NOW = datetime(2020, 1, 1, 2, tzinfo=UTC)
AT = "2020-01-01T00:00:00+00:00"
HELPER = Item("session", "host-1111", "Made-up helper")
ROWS = [
    Alert("a", "Newest thing", "info", "host-1111", AT),
    Alert("b", "Disk nearly full.", "warn", "", AT),
    Alert("c", "Job fell over", "error", "host-2222", ""),
]


@pytest.mark.parametrize(
    "words", ["alerts", "Any alerts?", "list alerts", "my alerts", "What are my alerts?"]
)
def test_ways_of_asking(words: str) -> None:
    assert topic_of(words) is Topic.ALERTS
    assert Conversation().needs(words) is Needs.REPORT


def test_alerts_are_counted_and_listed_newest_first_with_warnings_named() -> None:
    report = work.alerts(ROWS, 3, None, NOW)
    assert report.summary == (
        "3 unread alerts, across all projects, newest first. 2 warnings or errors."
    )
    assert report.items == (
        "1, Newest thing, 2 hours ago.",
        "2, warning: Disk nearly full, 2 hours ago.",
        "3, error: Job fell over.",
    )
    assert report.details[1] == (
        "Disk nearly full. A warning from 2 hours ago. To read the rest, open datawatch."
    )
    assert report.details[2] == "Job fell over. An error. To read the rest, open datawatch."


def test_when_datawatch_sends_only_the_newest_the_warning_count_says_so() -> None:
    report = work.alerts(ROWS, 900, None, NOW)
    assert report.summary.endswith("2 warnings or errors among the newest 3.")


def test_no_alerts() -> None:
    assert work.alerts([], 0, None, NOW).summary == "There are no unread alerts."


def test_a_focused_session_hears_only_its_alerts() -> None:
    report = work.alerts(ROWS, 3, HELPER, NOW)
    assert report.summary == "For the session Made-up helper: 1 unread alert, newest first."
    assert report.items == ("1, Newest thing, 2 hours ago.",)
    other = Item("session", "host-9999", "Quiet one")
    assert work.alerts(ROWS, 3, other, NOW).summary == (
        "datawatch links no unread alerts to the session Quiet one. There are 3 unread alerts "
        "in all. Say unset, then alerts."
    )


@pytest.mark.parametrize(
    ("path", "scoped"),
    [
        ((HELPER,), True),
        ((Item("automaton", "a2", "Paint"),), False),
        ((Item("automaton", "a2", "Paint"), HELPER), True),
        ((), False),
    ],
)
def test_only_a_session_focus_limits_alerts(path: tuple[Item, ...], scoped: bool) -> None:
    conversation = Conversation(path=path)
    assert (conversation.report_scope(Topic.ALERTS) == HELPER) is scoped
    assert conversation.report_scope(Topic.SESSIONS) == conversation.session_scope


def test_voice_alerts_never_include_a_body_and_change_nothing(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await visit(hass, satellite, "alerts", "two", "more detail", "stop")
        said = satellite.asked
        assert said[1].startswith("2 unread alerts, across all projects, newest first. 1 warning")
        assert "Already seen" not in said[1]
        assert said[2].startswith("Made-up disk is nearly full. A warning from ")
        assert RAW_BODY not in " ".join(said)
        assert posts(fake) == [] and fake.changes == []

    voice_test(certificate, tmp_path, body)


def test_voice_alerts_for_a_focused_session(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await visit(hass, satellite, "sessions", "one", "set it", "alerts", "stop")
        assert satellite.asked[4].startswith("For the session Made-up helper: 1 unread alert")

    voice_test(certificate, tmp_path, body)


def test_voice_an_alert_without_a_title_does_not_break_the_list(
    certificate: Certificate, tmp_path: Path
) -> None:
    fake = Fake()
    row = made_up_alert("x", "gone")
    del row["title"]
    fake.alerts = [row]

    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await visit(hass, satellite, "alerts", "stop")
        assert "1, untitled" in satellite.asked[1]

    voice_test(certificate, tmp_path, body, fake)


def test_the_assistant_gets_alert_titles_only(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await choose(hass, "conversation.home_assistant")
        found, failed = await call(hass, "work", topic="alerts")
        assert not failed and len(found["lines"]) == 2
        assert RAW_BODY not in str(found)
        assert "titles only" in found["what_is_not_here"]

    voice_test(certificate, tmp_path, body)


@pytest.mark.parametrize("topic", ["attention", "held", "alerts"])
def test_the_assistant_is_not_told_a_list_is_one_project_when_it_is_all(
    certificate: Certificate, tmp_path: Path, topic: str
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await choose(hass, "conversation.home_assistant")
        await visit(hass, satellite, "set oak", "stop")
        found, _ = await call(hass, "work", topic=topic)
        assert "limited_to_project" not in found
        assert found["tell_the_user"].startswith("This covers every project")
        plans, _ = await call(hass, "work", topic="plans")
        assert plans["limited_to_project"] == "oak"

    voice_test(certificate, tmp_path, body)
