"""Optional dashboard data sensors. All data is made up."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest
from aiohttp import web
from fake_datawatch import Fake, made_up_dashboards
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import entity_registry as er
from test_assistant import posts
from test_voice import Certificate, FakeSatellite, voice_test

from custom_components.datawatch import dashboard
from custom_components.datawatch.const import DASHBOARD, DOMAIN

VALUES = {
    "dashboard_data_overview": "4",
    "dashboard_data_lane_activity": "2",
    "dashboard_data_lane_use": "2",
    "dashboard_data_bugs": "6",
    "dashboard_data_review_backlog": "3",
    "dashboard_data_forecast": "2.5",
    "weekly_usage_used": "40",
    "weekly_usage_pace_line": "55.5",
    "weekly_usage_used_per_24_hours": "12.2",
    "held_questions_awaiting_a_decision": "1",
    "longest_wait_for_a_decision": "1.5",
    "forecast_days_to_finish_low": "3.5",
    "forecast_days_to_finish_high": "9",
    "lane_red_busy_last_full_hour": "25.4",
    "lane_blue_busy_last_full_hour": "unknown",
}


def entries(hass: HomeAssistant) -> dict[str, er.RegistryEntry]:
    (entry,) = hass.config_entries.async_entries(DOMAIN)
    found = er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    return {item.entity_id.removeprefix("sensor.datawatch_"): item for item in found}


async def read(hass: HomeAssistant) -> None:
    await hass.data[DASHBOARD].async_refresh()
    await hass.async_block_till_done()


async def enable(hass: HomeAssistant, names: list[str]) -> None:
    registry = er.async_get(hass)
    for name in names:
        registry.async_update_entity(entries(hass)[name].entity_id, disabled_by=None)
    (entry,) = hass.config_entries.async_entries(DOMAIN)
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done(wait_background_tasks=True)


def state(hass: HomeAssistant, name: str) -> State:
    found = hass.states.get(f"sensor.datawatch_{name}")
    assert found is not None, name
    return found


def asked(fake: Fake) -> list[str]:
    return sorted(
        path.removeprefix("/api/dashboard/")
        for _, path, *_ in fake.seen
        if path.startswith("/api/dashboard/")
    )


def test_every_dashboard_sensor_starts_off_and_only_the_lanes_are_read(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await hass.async_block_till_done(wait_background_tasks=True)
        found = entries(hass)
        for name in VALUES:
            assert found[name].disabled_by is er.RegistryEntryDisabler.INTEGRATION, name
            assert hass.states.get(found[name].entity_id) is None
        fake.seen.clear()
        await read(hass)
        assert asked(fake) == ["series/lane-utilization"]
        assert hass.data[DASHBOARD].update_interval == timedelta(minutes=5)

    voice_test(certificate, tmp_path, body)


def test_enabled_sensors_show_numbers_with_history_and_data_without_it(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await hass.async_block_till_done(wait_background_tasks=True)
        await enable(hass, list(VALUES))
        fake.seen.clear()
        await read(hass)
        assert asked(fake) == sorted(fake.dashboards)
        for name, value in VALUES.items():
            found = state(hass, name)
            assert found.state == value, name
            # A measurement is what Home Assistant keeps long-term statistics for.
            assert found.attributes["state_class"] == "measurement", name
            if name.startswith("dashboard_data_"):
                assert found.state_info is not None
                assert "data" in found.state_info["unrecorded_attributes"], name
            else:
                assert "data" not in found.attributes, name
        titles = state(hass, "dashboard_data_review_backlog").attributes["data"]["plans"]
        assert titles == [{"title": "Made-up waiting work"}]
        release = state(hass, "dashboard_data_overview").attributes["data"]["ci_release"]
        assert release["release"] == {"watch_mode": "on"}
        assert state(hass, "lane_red_busy_last_full_hour").name == (
            "datawatch Lane red busy, last full hour"
        )
        assert posts(fake) == [] and fake.changes == []

    voice_test(certificate, tmp_path, body)


def test_only_what_is_enabled_is_read(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await hass.async_block_till_done(wait_background_tasks=True)
        await enable(hass, ["longest_wait_for_a_decision"])
        fake.seen.clear()
        await read(hass)
        assert asked(fake) == ["series/lane-utilization", "series/review-backlog"]

    voice_test(certificate, tmp_path, body)


def test_a_data_set_that_cannot_be_read_hides_only_its_own_sensors(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await hass.async_block_till_done(wait_background_tasks=True)
        await enable(hass, ["dashboard_data_bugs", "dashboard_data_review_backlog"])
        fake.override["/api/dashboard/series/defects-per-day"] = lambda: web.Response(status=500)
        await read(hass)
        assert state(hass, "dashboard_data_bugs").state == "unavailable"
        assert "data" not in state(hass, "dashboard_data_bugs").attributes
        assert state(hass, "dashboard_data_review_backlog").state == "3"
        for path in fake.dashboards:
            fake.override[f"/api/dashboard/{path}"] = lambda: web.Response(status=500)
        await read(hass)
        assert state(hass, "dashboard_data_review_backlog").state == "unavailable"
        fake.override.clear()
        await read(hass)
        assert state(hass, "dashboard_data_bugs").state == "6"

    voice_test(certificate, tmp_path, body)


def test_lanes_seen_before_return_after_a_restart_and_new_ones_appear(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await hass.async_block_till_done(wait_background_tasks=True)
        await enable(hass, ["lane_red_busy_last_full_hour"])
        fake.dashboards["series/lane-utilization"] = {"lanes": []}
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        assert await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done(wait_background_tasks=True)
        # Quiet lane: the sensor is still there, and not shown as zero.
        assert state(hass, "lane_red_busy_last_full_hour").state == "unknown"
        hours = [{"busy_fraction": 0.1}, {"busy_fraction": 0}]
        fake.dashboards["series/lane-utilization"] = {
            "lanes": [{"lane": "green", "hours": hours}, {"lane": "green", "hours": hours}]
        }
        await read(hass)
        await read(hass)
        assert "lane_green_busy_last_full_hour" in entries(hass)

    voice_test(certificate, tmp_path, body)


@pytest.mark.parametrize(
    ("burn", "shown"),
    [
        ({"available": True, "points": 7}, 7),
        ({"available": True, "points": 7, "stale": True}, None),
        ({"available": False, "points": 0}, None),
        ({"available": True, "points": True}, None),
        (None, None),
    ],
)
def test_usage_that_is_missing_or_old_is_unknown(burn: Any, shown: int | None) -> None:
    (used,) = [number for number in dashboard.NUMBERS if number.key == "usage_used"]
    assert used.value({"burn": burn}) == shown


@pytest.mark.parametrize(("age", "current"), [(0, True), (1, True), (2, False), (30, False)])
def test_an_old_forecast_is_not_shown_as_current(age: int, current: bool) -> None:
    today = date(2026, 3, 10)
    point = {"date": (today - timedelta(days=age)).isoformat(), "throughput_per_day": 0}
    assert dashboard.latest_forecast({"points": [point]}, today) == (point if current else {})


@pytest.mark.parametrize(
    "data", [{}, {"points": []}, {"points": "x"}, {"points": [{"date": "soon"}]}]
)
def test_a_forecast_without_a_usable_date_is_unknown(data: dict[str, Any]) -> None:
    assert dashboard.latest_forecast(data, date(2026, 3, 10)) == {}


def test_replies_of_an_unexpected_shape_give_unknown_never_an_error() -> None:
    odd: dict[str, Any] = {"lanes": [None, {"lane": 5}, {"lane": "a", "hours": "x"}]}
    assert dashboard.lane_names(odd) == ["a"]
    assert dashboard.lane_names(None) == []
    assert dashboard.lane_busy("a")(odd) is None
    assert dashboard.lane_busy("a")({"lanes": [{"lane": "a", "hours": [{}]}]}) is None
    empty = made_up_dashboards()["console"]
    del empty["ci_release"]
    assert dashboard.details(empty) is empty
    for number in dashboard.DATA_SENSORS + dashboard.NUMBERS:
        assert number.value({}) is None, number.key
