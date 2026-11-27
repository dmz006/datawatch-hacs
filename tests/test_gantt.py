"""The Gantt card's data and how the card is offered. All data is made up."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from fake_datawatch import NEVER, SECRET_SPEC, Fake, made_up_live_work
from homeassistant.components import frontend as ha_frontend
from homeassistant.core import HomeAssistant
from test_assistant import posts
from test_dashboard import enable, read, state
from test_voice import Certificate, FakeSatellite, voice_test

from custom_components.datawatch import frontend, gantt
from custom_components.datawatch.const import DASHBOARD, DOMAIN

NOW = datetime(2026, 3, 10, 12, tzinfo=UTC)
SENSOR = "dashboard_data_live_work"


def at(hours_ago: float) -> str:
    return (NOW - timedelta(hours=hours_ago)).isoformat(timespec="seconds")


def chart() -> dict[str, Any]:
    return gantt.build(*made_up_live_work(NOW), NOW)


def test_the_window_is_the_six_hours_up_to_datawatchs_own_time() -> None:
    lanes, listed = made_up_live_work(NOW)
    later = gantt.build(lanes, listed, NOW + timedelta(hours=2))
    assert (later["from"], later["to"]) == (at(6), at(0))
    del lanes["window_end"]
    assert gantt.build(lanes, listed, NOW)["to"] == at(0)


def test_lanes_keep_idle_ones_and_cut_bars_to_the_window() -> None:
    red, blue = chart()["lanes"]
    assert blue == {"name": "blue", "bars": []}
    assert red["bars"] == [
        {"title": "Made-up long run", "start": at(6), "end": at(3), "live": False},
        {"title": "Made-up open run", "start": at(1), "end": at(0), "live": True},
    ]


def test_task_bars_follow_datawatchs_own_rules() -> None:
    found = chart()
    (work,) = found["work"]
    assert (work["title"], work["status"]) == ("Made-up fence", "running")
    assert work["bars"] == [
        {"title": "Sand", "status": "completed", "start": at(5), "end": at(4), "live": False},
        {"title": "Paint", "status": "in_progress", "start": at(2), "end": at(0), "live": True},
    ]
    assert (found["task_count"], found["automata"], found["not_read"]) == (2, 2, 1)


def test_instructions_and_history_are_never_kept() -> None:
    assert SECRET_SPEC not in json.dumps(chart())


@pytest.mark.parametrize(
    "value", [None, 5, "", "soon", NEVER, "2026-03-10T11:00:00", "1999-01-01T00:00:00Z"]
)
def test_a_task_without_a_usable_start_has_no_bar(value: object) -> None:
    task = {"title": "x", "status": "in_progress", "started_at": value}
    listed = {"prds": [{"stories": [{"tasks": [task]}]}]}
    assert gantt.build({}, listed, NOW)["work"] == []


def test_times_with_nine_decimal_places_are_read() -> None:
    task = {"status": "verifying", "started_at": "2026-03-10T05:00:00.123456789-04:00"}
    listed = {"prds": [{"stories": [{"tasks": [task, {"started_at": at(-1)}]}]}]}
    (work,) = gantt.build({}, listed, NOW)["work"]
    assert work["title"] == "untitled"
    assert [bar["live"] for bar in work["bars"]] == [True]


def test_replies_of_an_unexpected_shape_give_an_empty_chart() -> None:
    lanes = {"lanes": [None, {"runs": "x"}, {"id": "a", "runs": [None, {}]}]}
    found = gantt.build(lanes, {"prds": [None, {"stories": [None, {"tasks": 4}]}]}, NOW)
    assert found["work"] == []
    assert [lane["bars"] for lane in found["lanes"]] == [[], []]


def test_the_live_work_sensor_reads_only_two_things_and_only_when_enabled(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await hass.async_block_till_done(wait_background_tasks=True)
        wanted = "/api/autonomous/lane-utilization"
        await read(hass)
        assert wanted not in [path for _, path, *_ in fake.seen]
        await enable(hass, [SENSOR])
        fake.seen.clear()
        await read(hass)
        asked = [(path, query) for _, path, query, _ in fake.seen if "/autonomous/" in path]
        assert (wanted, {"window": "6h"}) in asked
        query = {"status": "running,blocked,planning", "full": "true", "limit": "20"}
        assert ("/api/autonomous/prds", query) in asked
        found = state(hass, SENSOR)
        assert found.state == "2"
        assert found.state_info is not None
        assert "data" in found.state_info["unrecorded_attributes"]
        assert SECRET_SPEC not in json.dumps(found.attributes["data"])
        assert posts(fake) == [] and fake.changes == []

    voice_test(certificate, tmp_path, body)


@pytest.mark.parametrize(
    "broken",
    [
        ("lanes", {}),
        ("listed", {"total": 0}),
        ("listed", {"prds": [{"title": "x", "task_count": 3}]}),
    ],
)
def test_a_reply_that_cannot_be_trusted_is_unavailable_not_empty(
    certificate: Certificate, tmp_path: Path, broken: tuple[str, dict[str, Any]]
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await hass.async_block_till_done(wait_background_tasks=True)
        await enable(hass, [SENSOR])
        setattr(fake, f"live_{broken[0]}", broken[1])
        await read(hass)
        assert state(hass, SENSOR).state == "unavailable"
        assert hass.data[DASHBOARD].last_update_success

    voice_test(certificate, tmp_path, body)


class _Pages:
    """Stands in for Home Assistant's web server."""

    def __init__(self) -> None:
        self.served: list[Any] = []

    async def async_register_static_paths(self, paths: list[Any]) -> None:
        self.served += paths


def test_the_card_is_offered_once_withdrawn_on_removal_and_offered_again(
    certificate: Certificate, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    offered: list[str] = []
    monkeypatch.setattr(ha_frontend, "add_extra_js_url", lambda hass, url: offered.append(url))
    monkeypatch.setattr(ha_frontend, "remove_extra_js_url", lambda hass, url: offered.remove(url))

    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        frontend.withdraw_cards(hass)  # Nothing was offered where there are no pages.
        assert offered == []
        pages = _Pages()
        monkeypatch.setattr(hass, "http", pages, raising=False)
        hass.config.components.add("frontend")
        await frontend.async_offer_cards(hass)
        await frontend.async_offer_cards(hass)
        (url,) = offered
        assert url.startswith("/datawatch_static/datawatch-cards.js?v=")
        (path,) = pages.served
        assert path.url_path == "/datawatch_static/datawatch-cards.js"
        assert Path(path.path).is_file()
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        await hass.config_entries.async_remove(entry.entry_id)
        assert offered == []
        await frontend.async_offer_cards(hass)
        assert offered == [url] and len(pages.served) == 1
        hass.config.components.remove("frontend")

    voice_test(certificate, tmp_path, body)


def test_a_card_that_cannot_be_offered_does_not_stop_the_integration(
    certificate: Certificate, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    class Broken:
        async def async_register_static_paths(self, paths: list[Any]) -> None:
            raise RuntimeError("made-up failure")

    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        hass.http = Broken()  # type: ignore[assignment]
        hass.config.components.add("frontend")
        await frontend.async_offer_cards(hass)
        assert "Could not add the datawatch dashboard cards" in caplog.text
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        assert entry.state.name == "LOADED"
        hass.config.components.remove("frontend")

    voice_test(certificate, tmp_path, body)
