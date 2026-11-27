"""The user's own reports and the dashboard sensors, in a throwaway Home Assistant."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest
from aiohttp import web
from fake_datawatch import Fake
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from test_assistant import add_assistant, call, choose, posts
from test_voice import Certificate, FakeSatellite, visit, voice_test

from custom_components.datawatch.const import COUNTS, DOMAIN, FOCUS
from custom_components.datawatch.voice import custom
from custom_components.datawatch.voice.conversation import Conversation, Needs
from custom_components.datawatch.voice.custom import CustomReport

DAILY = CustomReport("Daily report", ("next", "status", "attention"))


@pytest.mark.parametrize(
    "heard",
    [
        "daily report",
        "Daily.",
        "read my daily report",
        "Give me the daily report, please.",
        "run daily",
    ],
)
def test_ways_of_naming_a_report(heard: str) -> None:
    assert custom.match(heard, [DAILY]) is DAILY


@pytest.mark.parametrize("heard", ["daily news", "report", "", "the daily report of everything"])
def test_only_the_name_names_it(heard: str) -> None:
    assert custom.match(heard, [DAILY]) is None


def test_listing_and_composing() -> None:
    assert custom.listing([]).startswith("You have no reports yet.")
    assert custom.listing([DAILY]) == "You have 1 report: Daily report. Say a name."
    assert custom.listing([DAILY, CustomReport("Evening", ())]).startswith("You have 2 reports:")
    parts = {"status": "S.", "next": "N.", "held": "H.", "attention": ""}
    assert custom.compose("R", parts, ("next", "status", "attention")) == "R. S. N."
    assert custom.compose("R", {}, ("next",)).startswith("R has nothing in it.")


def test_a_report_name_is_a_command_only_when_defined() -> None:
    conversation = Conversation(reports=(DAILY,), assistant=True)
    conversation.enter()
    assert conversation.needs("daily report") is Needs.CUSTOM
    reply = conversation.hear("daily report", None, composed="All well.")
    assert (reply.text, reply.forward) == ("All well.", None)
    assert conversation.hear("daily report", None).text.startswith("I can't reach")
    assert conversation.hear("weekly report", None).forward == "weekly report"
    assert conversation.hear("reports", None).text == (
        "You have 1 report: Daily report. Say a name."
    )


async def new_report(hass: HomeAssistant, name: str, items: list[str]) -> dict[str, Any]:
    """Use the Add report screen. Returns what Home Assistant answered."""
    (entry,) = hass.config_entries.async_entries(DOMAIN)
    flows = hass.config_entries.subentries
    form = await flows.async_init((entry.entry_id, "report"), context={"source": "user"})
    assert form["step_id"] == "user"
    result: Any = await flows.async_configure(form["flow_id"], {"name": name, "items": items})
    await hass.async_block_till_done()
    return dict(result)


def test_adding_and_changing_a_report(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        made = await new_report(hass, "  Daily   report ", ["attention", "status"])
        assert made["type"] == "create_entry" and made["title"] == "Daily report"
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        (subentry,) = entry.subentries.values()
        assert dict(subentry.data) == {"items": ["status", "attention"]}

        flows = hass.config_entries.subentries
        form: Any = await flows.async_init(
            (entry.entry_id, "report"),
            context={"source": "reconfigure", "subentry_id": subentry.subentry_id},
        )
        done = await flows.async_configure(
            form["flow_id"], {"name": "Daily report", "items": ["next"]}
        )
        assert done["reason"] == "reconfigure_successful"
        (subentry,) = entry.subentries.values()
        assert dict(subentry.data) == {"items": ["next"]}

    voice_test(certificate, tmp_path, body)


@pytest.mark.parametrize(
    ("name", "items", "field", "error"),
    [
        ("  ", ["status"], "name", "no_name"),
        ("Status", ["status"], "name", "name_is_a_command"),
        ("My status report", ["status"], "name", "name_is_a_command"),
        ("Confirm answer", ["status"], "name", "name_is_a_command"),
        ("Datawatch", ["status"], "name", "name_is_a_command"),
        # Voice follows each assistant's language, so no language's command can be a name.
        ("Hilfe", ["status"], "name", "name_is_a_command"),
        ("ヘルプ", ["status"], "name", "name_is_a_command"),
        ("Ouvre datawatch", ["status"], "name", "name_is_a_command"),
        ("daily", ["status"], "name", "name_taken"),
        ("Evening", [], "items", "no_items"),
    ],
)
def test_names_that_cannot_be_used(
    certificate: Certificate,
    tmp_path: Path,
    name: str,
    items: list[str],
    field: str,
    error: str,
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await new_report(hass, "Daily report", ["status"])
        refused = await new_report(hass, name, items)
        assert refused["errors"] == {field: error}

    voice_test(certificate, tmp_path, body)


def test_saying_a_report_s_name(certificate: Certificate, tmp_path: Path) -> None:
    every = [
        "status", "detail", "attention", "questions", "next", "plans", "running", "held",
        "sessions", "automations",
    ]  # fmt: skip

    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await new_report(hass, "Everything", every)
        assistant = await add_assistant(hass)
        await choose(hass, assistant.entity_id)
        await visit(hass, satellite, "reports", "give me the everything report", "stop")
        assert satellite.asked[1] == "You have 1 report: Everything. Say a name."
        said = satellite.asked[2]
        for expected in (
            "Everything. New work is paused. 4 open questions",
            "failed or blocked automata",
            "3 automata need attention",
            "4 open questions, across all projects.",
            "1 project has something next. Project oak. Next:",
            "2 current plans in 1 project.",
            "1 automaton is running",
            "7 items are on hold, across all projects.",
            "All projects: sessions,",
            "All projects: 4 automations",
        ):
            assert expected in said, expected
        assert "say why and its number" not in said and "Say more" not in said
        assert assistant.asked == [] and posts(fake) == []

        listed, _ = await call(hass, "report")
        assert listed == {"reports": ["Everything"]}
        ran, _ = await call(hass, "report", name="the everything report")
        assert ran["report"].startswith("Everything.")
        assert "tell_the_user" not in ran
        await hass.data[FOCUS].async_set("oak")
        ran, _ = await call(hass, "report", name="everything")
        assert "only project oak" in ran["tell_the_user"]
        unknown, _ = await call(hass, "report", name="nope")
        assert unknown == {"reports": ["Everything"]}

    voice_test(certificate, tmp_path, body)


def test_a_report_without_counts_reads_only_what_it_needs(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await new_report(hass, "Short", ["attention"])
        await visit(hass, satellite, "short report", "stop")
        assert satellite.asked[1].startswith("Short. 3 automata need attention")
        assert [path for _, path, *_ in fake.seen] == ["/api/autonomous/attention"]

    voice_test(certificate, tmp_path, body)


def states(hass: HomeAssistant) -> dict[str, str]:
    registry = er.async_get(hass)
    found = {}
    (entry,) = hass.config_entries.async_entries(DOMAIN)
    for item in er.async_entries_for_config_entry(registry, entry.entry_id):
        if item.disabled:
            continue
        state = hass.states.get(item.entity_id)
        assert state is not None
        found[item.entity_id] = state.state
    return found


async def refresh(hass: HomeAssistant) -> None:
    await hass.data[COUNTS].async_refresh()
    await hass.async_block_till_done()


EXPECTED = {
    "binary_sensor.datawatch_new_work_paused": "on",
    "sensor.datawatch_open_questions": "4",
    "sensor.datawatch_automata_needing_attention": "3",
    "sensor.datawatch_sessions_waiting_for_input": "3",
    "sensor.datawatch_sessions_running": "2",
    "sensor.datawatch_sessions_failed": "5",
    "sensor.datawatch_automata_failed_or_blocked": "2",
    "sensor.datawatch_items_on_hold": "7",
}


def test_sensors_show_the_counts_and_never_zero_when_datawatch_cannot_be_read(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        assert states(hass) == EXPECTED
        fake.questions = 9
        await refresh(hass)
        assert states(hass)["sensor.datawatch_open_questions"] == "9"

        fake.override["/api/pause"] = lambda: web.Response(status=500)
        await refresh(hass)
        assert set(states(hass).values()) == {"unavailable"}

        del fake.override["/api/pause"]
        await refresh(hass)
        assert states(hass)["binary_sensor.datawatch_new_work_paused"] == "on"
        assert posts(fake) == []

    voice_test(certificate, tmp_path, body)


def test_sensors_read_once_a_minute_and_stop_when_removed(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        assert hass.data[COUNTS].update_interval == timedelta(seconds=60)
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
        fake.seen.clear()
        hass.bus.async_fire("time_changed", {"now": dt_util.utcnow() + timedelta(minutes=5)})
        await hass.async_block_till_done()
        assert fake.seen == []
        assert set(states(hass).values()) == {"unavailable"}

    voice_test(certificate, tmp_path, body)


def test_setup_does_not_need_datawatch(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        fake.override["/api/projects"] = lambda: web.Response(status=500)
        assert await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert entry.state.name == "LOADED"
        assert set(states(hass).values()) == {"unavailable"}

    voice_test(certificate, tmp_path, body)
