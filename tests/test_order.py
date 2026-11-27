"""List order: by name or most recent first, by voice and in settings. Data is made up."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from fake_datawatch import Fake
from homeassistant.core import HomeAssistant
from test_assistant import call, choose, posts
from test_voice import Certificate, FakeSatellite, visit, voice_test

from custom_components.datawatch.const import CONF_ASSISTANT, CONF_ORDER, DOMAIN
from custom_components.datawatch.voice import order, reports, work
from custom_components.datawatch.voice.conversation import Conversation, Needs
from custom_components.datawatch.voice.order import Order
from custom_components.datawatch.voice.phrases import Kind, parse
from custom_components.datawatch.voice.reports import Automation, Listed, Plan
from custom_components.datawatch.voice.work import Session

# The later of the first two is only later once their time zones are counted.
EARLY = "2026-03-10T09:00:00+00:00"
LATE = "2026-03-10T06:00:00.123456789-04:00"
ROWS = [("beta", EARLY), ("Alpha", EARLY), ("gamma", LATE), ("delta", ""), ("Echo", "soon")]


def names(rows: list[tuple[str, str]], chosen: Order) -> list[str]:
    found = order.arrange(rows, chosen, lambda row: row[0], lambda row: row[1])
    return [row[0] for row in found]


def test_by_name_ignores_capitals() -> None:
    assert names(ROWS, Order.NAME) == ["Alpha", "beta", "delta", "Echo", "gamma"]


def test_most_recent_compares_times_and_puts_unknown_ones_last_by_name() -> None:
    assert names(ROWS, Order.RECENT) == ["gamma", "Alpha", "beta", "delta", "Echo"]
    assert names([("b", "2026-03-10T09:00:00"), ("a", "")], Order.RECENT) == ["a", "b"]


@pytest.mark.parametrize("value", [None, "", "newest", 4, "name"])
def test_anything_but_a_stored_recent_is_by_name(value: object) -> None:
    assert order.chosen(value) is Order.NAME
    assert order.chosen("recent") is Order.RECENT


def test_each_of_the_three_lists_follows_the_order() -> None:
    running = [Listed("1", "Apple", updated=EARLY), Listed("2", "Berry", updated=LATE)]
    automations = [
        Automation("Apple", "draft", updated=EARLY),
        Automation("Berry", "blocked", updated=LATE),
    ]
    sessions = [
        Session("h-1", "Apple", "running", last_activity=EARLY),
        Session("h-2", "Berry", "running", last_activity=LATE),
    ]
    now = datetime(2026, 3, 10, 12, tzinfo=UTC)
    for chosen, first in ((Order.NAME, "Apple"), (Order.RECENT, "Berry")):
        found = (
            reports.running(running, 2, None, chosen),
            reports.automations(automations, None, chosen),
            work.sessions([("running", 2)], sessions, None, now, order=chosen),
        )
        for report in found:
            # What is heard, what a number chooses and its details all stay together.
            assert first in report.items[0] and report.refs[0].title == first
        assert first in found[2].details[0]


def test_plans_keep_datawatchs_order() -> None:
    plans = [Plan("Zinnia", "planned", id="z"), Plan("Aster", "planned", id="a")]
    assert [ref.title for ref in reports.plans_of("oak", plans, 2, 0).refs] == ["Zinnia", "Aster"]


@pytest.mark.parametrize(
    ("words", "kind"),
    [
        ("Sort by name.", Kind.ORDER_NAME),
        ("alphabetical", Kind.ORDER_NAME),
        ("Most recent first", Kind.ORDER_RECENT),
        ("newest first", Kind.ORDER_RECENT),
        ("What's the list order?", Kind.ORDER),
        ("list order", Kind.ORDER),
    ],
)
def test_ways_of_saying_it(words: str, kind: Kind) -> None:
    assert parse(words).kind is kind
    assert Conversation(assistant=True).needs(words) is Needs.NOTHING


def test_changing_and_asking_the_order() -> None:
    conversation = Conversation(assistant=True)
    conversation.enter()
    asked = conversation.hear("list order", None)
    assert asked.text == (
        "Sessions, automations and running work are listed by name. "
        "Say most recent first to switch."
    )
    assert asked.order is None and asked.forward is None
    changed = conversation.hear("most recent first", None)
    assert changed.order is Order.RECENT and changed.forward is None
    assert changed.text == (
        "Order: most recent first, for sessions, automations and running work. "
        "Say the list again to hear it that way. Say sort by name to switch."
    )
    assert conversation.hear("repeat", None).text == changed.text
    assert "listed most recent first" in conversation.hear("list order", None).text
    assert conversation.hear("sort by name", None).order is Order.NAME


def test_the_order_does_not_change_while_something_waits_to_be_confirmed() -> None:
    conversation = Conversation(path=(), focus="oak")
    conversation.enter()
    conversation.hear("add bug the gate is stuck", None)
    reply = conversation.hear("most recent first", None)
    assert reply.order is None and conversation.order is Order.NAME
    assert reply.text.startswith("Not sent yet.")


def two_sessions(fake: Fake) -> None:
    def row(ident: str, name: str, when: str) -> dict[str, Any]:
        return {"full_id": ident, "name": name, "project": "oak", "last_activity": when}

    fake.sessions["waiting_input"] = [
        row("host-1", "Apple", "2020-01-01T00:00:00+00:00"),
        row("host-2", "Berry", "2020-01-02T00:00:00+00:00"),
    ]


def options(hass: HomeAssistant) -> dict[str, Any]:
    (entry,) = hass.config_entries.async_entries(DOMAIN)
    return dict(entry.options)


def test_a_spoken_order_is_used_at_once_saved_and_kept_for_next_time(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        two_sessions(fake)
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        hass.config_entries.async_update_entry(entry, options={CONF_ASSISTANT: "made.up"})
        client = entry.runtime_data
        await visit(hass, satellite, "sessions", "most recent first", "sessions", "stop")
        assert "1, session named Apple" in satellite.asked[1]
        assert "1, session named Berry" in satellite.asked[3]
        assert options(hass) == {CONF_ASSISTANT: "made.up", CONF_ORDER: "recent"}
        # Saving it does not restart the integration.
        assert entry.runtime_data is client
        satellite.asked.clear()
        await visit(hass, satellite, "sessions", "sort by name", "sessions", "stop")
        assert "1, session named Berry" in satellite.asked[1]
        assert "1, session named Apple" in satellite.asked[3]
        assert options(hass)[CONF_ORDER] == "name"
        assert posts(fake) == [] and fake.changes == []

    voice_test(certificate, tmp_path, body)


@pytest.mark.parametrize(
    ("given", "stored"),
    [
        ({CONF_ORDER: "name"}, {}),
        ({}, {}),
        ({CONF_ORDER: "recent"}, {CONF_ORDER: "recent"}),
        (
            {CONF_ORDER: "recent", CONF_ASSISTANT: "conversation.home_assistant"},
            {CONF_ORDER: "recent", CONF_ASSISTANT: "conversation.home_assistant"},
        ),
    ],
)
def test_the_settings_screen_changes_the_order_and_shows_it(
    certificate: Certificate, tmp_path: Path, given: dict[str, str], stored: dict[str, str]
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        form = await hass.config_entries.options.async_init(entry.entry_id)
        await hass.config_entries.options.async_configure(form["flow_id"], given)
        await hass.async_block_till_done()
        assert options(hass) == stored
        again = await hass.config_entries.options.async_init(entry.entry_id)
        shown = {
            str(key): key.description["suggested_value"]
            for key in again["data_schema"].schema
            if key.description and "suggested_value" in key.description
        }
        assert shown == stored

    voice_test(certificate, tmp_path, body)


def test_the_assistant_lists_sessions_in_the_saved_order(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        two_sessions(fake)
        await choose(hass, "conversation.home_assistant")
        found, _ = await call(hass, "work", topic="waiting_sessions")
        assert "Apple" in found["lines"][0]
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        saved = {**entry.options, CONF_ORDER: "recent"}
        hass.config_entries.async_update_entry(entry, options=saved)
        found, _ = await call(hass, "work", topic="waiting_sessions")
        assert "Berry" in found["lines"][0]

    voice_test(certificate, tmp_path, body)
