"""The two dashboard cards' data and how a card asks for it. All data is made up."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import probatio
import pytest
from aiohttp import web
from fake_datawatch import SECRET_SPEC, Fake, made_up_chart_data
from homeassistant.components import frontend as ha_frontend
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from test_assistant import posts
from test_voice import Certificate, FakeSatellite, voice_test

from custom_components.datawatch import charts, frontend
from custom_components.datawatch.const import DOMAIN

NOW = datetime(2026, 3, 10, 12, tzinfo=UTC)


def at(**gap: float) -> str:
    return (NOW - timedelta(**gap)).isoformat(timespec="seconds")


def chart(days: int = 30) -> dict[str, Any]:
    timeline, automations, _ = made_up_chart_data(NOW)
    return charts.gantt(timeline, automations, NOW, days)


def test_every_automation_holding_the_projects_automata_has_a_row_open_ones_first() -> None:
    found = chart(0)
    assert [row["name"] for row in found["rows"]] == [
        "Made-up fence",
        "Not started",
        "Finished long ago",
    ]
    assert (found["automations"], found["automata"], found["done"], found["hidden"]) == (3, 7, 4, 0)


def test_a_row_counts_only_this_projects_automata_each_once() -> None:
    fence = chart()["rows"][0]
    assert (fence["done"], fence["total"], fence["counts"]) == (1, 2, {"running": 1})
    assert (fence["open"], fence["finished"], fence["running"]) == (True, False, True)
    assert (fence["start"], fence["last"]) == (at(days=5), at(days=1))
    # Unfinished first.
    assert [item["title"] for item in fence["automata"]] == ["Paint", "Sand"]


def test_all_automata_done_shows_finished_whatever_datawatch_calls_the_automation() -> None:
    old = chart(0)["rows"][2]
    assert (old["finished"], old["open"], old["state"]) == (True, False, "draft")
    assert (old["start"], old["last"]) == (at(days=70), at(days=50))


def test_the_rest_are_automata_in_no_automation() -> None:
    loose = chart()["loose"]
    assert (loose["done"], loose["total"], loose["open"]) == (1, 2, True)
    # Finished work older than the range is not listed, but is counted.
    assert [item["title"] for item in loose["automata"]] == ["Stray"]
    assert [item["title"] for item in chart(0)["loose"]["automata"]] == [
        "Stray",
        "Long gone stray",
    ]


def test_a_range_hides_only_finished_work_older_than_it() -> None:
    found = chart(7)
    assert [row["name"] for row in found["rows"]] == ["Made-up fence", "Not started"]
    assert (found["hidden"], found["automations"], found["from"]) == (1, 3, at(days=7))
    assert chart(0)["from"] == at(days=90)


def test_unstarted_work_has_no_dates_and_long_lists_are_cut() -> None:
    waiting = chart()["rows"][1]
    assert (waiting["start"], waiting["last"], waiting["open"]) == (None, None, True)
    many = {"projects": [{"automata": [{"id": str(n), "status": "completed"} for n in range(130)]}]}
    row = charts.gantt(many, [{"members": [{"prd_id": str(n)} for n in range(130)]}], NOW, 0)
    assert (row["rows"][0]["total"], len(row["rows"][0]["automata"]), row["rows"][0]["more"]) == (
        130,
        100,
        30,
    )
    assert row["rows"][0]["name"] == "unnamed" and row["loose"] is None


def test_a_cancelled_automation_with_unfinished_automata_is_not_open() -> None:
    timeline = {"projects": [{"automata": [{"id": "z", "status": "cancelled"}]}]}
    automations = [{"name": "n", "status": "cancelled", "members": [{"prd_id": "z"}]}]
    (row,) = charts.gantt(timeline, automations, NOW, 0)["rows"]
    assert (row["open"], row["finished"]) == (False, False)


def test_rows_with_work_left_come_first_however_old_it_is() -> None:
    def entry(ident: str, status: str, days: int) -> dict[str, Any]:
        return {"id": ident, "status": status, "start": at(days=days)}

    entries = [entry("c", "cancelled", 1), entry("w", "blocked", 20), entry("d", "completed", 2)]
    automations = [
        {"id": ident, "name": ident, "status": status, "members": [{"prd_id": ident}]}
        for ident, status in (("c", "draft"), ("d", "completed"), ("w", "draft"))
    ]
    found = charts.gantt({"projects": [{"automata": entries}]}, automations, NOW, 30)
    assert [(row["name"], row["unfinished"]) for row in found["rows"]] == [
        ("w", 1),
        ("c", 0),
        ("d", 0),
    ]


def test_replies_of_an_unexpected_shape_give_an_empty_chart() -> None:
    odd: dict[str, Any] = {"projects": [None, {"automata": [None, {"id": 5}]}]}
    found = charts.gantt(odd, [{"members": "x"}, {"members": [None, {"prd_id": 5}]}], NOW, 30)
    assert (found["rows"], found["loose"], found["automata"]) == ([], None, 0)
    assert charts.lanes({"lanes": [None, {"buckets": "x", "busy_share": True}]}, NOW) == {
        "from": at(hours=6),
        "to": at(),
        "lanes": [{"name": "unnamed lane", "average": None, "points": []}],
    }


def test_nothing_but_names_titles_states_and_times_is_kept() -> None:
    timeline, automations, lanes = made_up_chart_data(NOW)
    kept = json.dumps([charts.gantt(timeline, automations, NOW, 0), charts.lanes(lanes, NOW)])
    assert SECRET_SPEC not in kept


def test_lane_points_are_percentages_and_unreadable_steps_are_left_out() -> None:
    red, blue = charts.lanes(made_up_chart_data(NOW)[2], NOW)["lanes"]
    assert red == {
        "name": "red",
        "average": 62.5,
        "points": [[at(minutes=15), 50], [at(), 100]],
    }
    assert blue == {"name": "blue", "average": 0, "points": []}


class Connection:
    """Stands in for a signed-in card."""

    def __init__(self) -> None:
        self.results: list[Any] = []
        self.errors: list[str] = []

    def send_result(self, ident: int, result: Any) -> None:
        self.results.append(result)

    def send_error(self, ident: int, code: str, message: str) -> None:
        self.errors.append(code)


async def ask(hass: HomeAssistant, kind: str, **given: Any) -> Connection:
    handler, schema = hass.data["websocket_api"][f"{DOMAIN}/{kind}"]
    connection = Connection()
    message = {"id": 1, "type": f"{DOMAIN}/{kind}", **given}
    # Home Assistant keeps no checker for a command that takes nothing but its type.
    handler(hass, connection, schema(message) if schema else message)
    await hass.async_block_till_done(wait_background_tasks=True)
    return connection


def setup(fake: Fake) -> None:
    fake.override["/api/automations"] = lambda: web.json_response(fake.chart_automations)


def test_the_gantt_command_reads_the_project_asked_for_and_changes_nothing(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        setup(fake)
        fake.seen.clear()
        (result,) = (await ask(hass, "gantt", project="elm", days=7)).results
        assert (result["project"], result["projects"], result["days"]) == ("elm", ["elm", "oak"], 7)
        timeline = [query for _, path, query, _ in fake.seen if path.endswith("/timeline")]
        assert timeline == [{"project": "elm"}]
        assert SECRET_SPEC not in json.dumps(result)
        assert posts(fake) == [] and fake.changes == []

    voice_test(certificate, tmp_path, body)


@pytest.mark.parametrize("project", [None, "no such project"])
def test_without_a_known_project_it_shows_the_one_with_the_most_automations(
    certificate: Certificate, tmp_path: Path, project: str | None
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        setup(fake)
        given = {} if project is None else {"project": project}
        (result,) = (await ask(hass, "gantt", **given)).results
        assert (result["project"], result["days"]) == ("oak", 30)

    voice_test(certificate, tmp_path, body)


def test_with_no_projects_it_says_so(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        fake.override["/api/projects"] = lambda: web.json_response([])
        (result,) = (await ask(hass, "gantt")).results
        assert result == {"projects": [], "project": None}

    voice_test(certificate, tmp_path, body)


def test_only_the_offered_ranges_are_accepted(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        with pytest.raises(probatio.Invalid):
            await ask(hass, "gantt", days=5000)

    voice_test(certificate, tmp_path, body)


def test_the_lanes_command(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        fake.seen.clear()
        (result,) = (await ask(hass, "lanes")).results
        assert [lane["name"] for lane in result["lanes"]] == ["red", "blue"]
        assert (fake.seen[0][1], fake.seen[0][2]) == (
            "/api/autonomous/lane-utilization",
            {"window": "6h"},
        )

    voice_test(certificate, tmp_path, body)


@pytest.mark.parametrize(
    ("kind", "path", "reply"),
    [
        ("gantt", "/api/autonomous/timeline", {"today": "x"}),
        ("gantt", "/api/automations", {"no": "list"}),
        ("lanes", "/api/autonomous/lane-utilization", {}),
    ],
)
def test_a_reply_that_cannot_be_trusted_is_an_error_not_an_empty_chart(
    certificate: Certificate, tmp_path: Path, kind: str, path: str, reply: dict[str, str]
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        setup(fake)
        fake.override[path] = lambda: web.json_response(reply)
        found = await ask(hass, kind)
        assert (found.results, found.errors) == ([], ["unreachable"])

    voice_test(certificate, tmp_path, body)


@pytest.mark.parametrize("kind", ["gantt", "lanes"])
def test_a_removed_integration_says_it_is_not_set_up(
    certificate: Certificate, tmp_path: Path, kind: str
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        assert await hass.config_entries.async_unload(entry.entry_id)
        assert (await ask(hass, kind)).errors == ["not_loaded"]

    voice_test(certificate, tmp_path, body)


def test_the_retired_live_work_sensor_is_taken_away(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        registry = er.async_get(hass)
        old = registry.async_get_or_create(
            "sensor", DOMAIN, f"{entry.entry_id}_data_live_work", config_entry=entry
        )
        before = len(er.async_entries_for_config_entry(registry, entry.entry_id))
        assert await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert registry.async_get(old.entity_id) is None
        assert len(er.async_entries_for_config_entry(registry, entry.entry_id)) == before - 1

    voice_test(certificate, tmp_path, body)


class _Pages:
    """Stands in for Home Assistant's web server."""

    def __init__(self) -> None:
        self.served: list[Any] = []

    async def async_register_static_paths(self, paths: list[Any]) -> None:
        self.served += paths


def test_the_cards_are_offered_once_withdrawn_on_removal_and_offered_again(
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


def test_cards_that_cannot_be_offered_do_not_stop_the_integration(
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
