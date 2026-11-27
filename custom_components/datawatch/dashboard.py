"""datawatch's dashboard data for users' own cards, read every five minutes.

Numbers are sensor states, so Home Assistant keeps their history. The lists and titles are
one attribute, which is not saved in history. A number datawatch does not give, or gives
only as old, is unknown: it is never shown as zero or as current.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any, override

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from . import gantt
from .api import DASHBOARDS, DatawatchClient, DatawatchError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
INTERVAL = timedelta(minutes=5)
# Always read, to find the lanes there are sensors for. It is small and quick.
LANES = "lane_use"
# The Gantt card's data, which is put together here from two of datawatch's replies.
LIVE_WORK = "live_work"
# A forecast point older than this many days is not current.
_FORECAST_FRESH_DAYS = 1

type Datasets = dict[str, dict[str, Any] | None]
type Value = Callable[[dict[str, Any]], float | None]


class DashboardCoordinator(DataUpdateCoordinator[Datasets]):
    """Reads only the data sets that an enabled sensor shows, plus the lanes."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: DatawatchClient) -> None:
        super().__init__(
            hass, _LOGGER, config_entry=entry, name=f"{DOMAIN} dashboard", update_interval=INTERVAL
        )
        self._client = client

    @override
    async def _async_update_data(self) -> Datasets:
        known = {*DASHBOARDS, LIVE_WORK}
        wanted = {LANES} | {name for name in self.async_contexts() if name in known}
        found: Datasets = {}
        problem = ""
        # One at a time, to go easy on datawatch. One failing does not hide the others.
        for name in sorted(wanted):
            try:
                found[name] = await self._read(name)
            except DatawatchError as error:
                found[name], problem = None, str(error)
        if all(data is None for data in found.values()):
            raise UpdateFailed(problem)
        return found

    async def _read(self, name: str) -> dict[str, Any]:
        if name == LIVE_WORK:
            lanes, listed = await self._client.live_work()
            return gantt.build(lanes, listed, datetime.now(UTC))
        return await self._client.dashboard(name)


def _number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return value


def _rounded(value: object) -> float | None:
    found = _number(value)
    return None if found is None else round(found, 1)


def _table(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _rows(value: object) -> list[dict[str, Any]] | None:
    if not isinstance(value, list):
        return None
    return [row for row in value if isinstance(row, dict)]


def _count(key: str) -> Value:
    def value(data: dict[str, Any]) -> float | None:
        rows = _rows(data.get(key))
        return None if rows is None else len(rows)

    return value


def _field(key: str) -> Value:
    return lambda data: _number(data.get(key))


def _open_questions(data: dict[str, Any]) -> float | None:
    section = _table(data.get("questions_waiting"))
    return _number(section.get("count")) if section.get("available") is True else None


def _usage(key: str) -> Value:
    def value(data: dict[str, Any]) -> float | None:
        burn = _table(data.get("burn"))
        if burn.get("available") is not True or burn.get("stale") is True:
            return None
        return _rounded(burn.get(key))

    return value


def _oldest_hours(data: dict[str, Any]) -> float | None:
    seconds = _number(data.get("oldest_age_seconds"))
    return None if seconds is None else round(seconds / 3600, 1)


def latest_forecast(data: dict[str, Any], today: date) -> dict[str, Any]:
    """The newest forecast point if it is recent, or nothing."""
    points = _rows(data.get("points"))
    if not points:
        return {}
    newest = max(points, key=lambda point: str(point.get("date", "")))
    try:
        day = date.fromisoformat(str(newest.get("date", "")))
    except ValueError:
        return {}
    return newest if (today - day).days <= _FORECAST_FRESH_DAYS else {}


def _forecast(key: str) -> Value:
    return lambda data: _rounded(latest_forecast(data, datetime.now(UTC).date()).get(key))


def lane_names(data: dict[str, Any] | None) -> list[str]:
    """The lanes datawatch reports use for."""
    rows = _rows((data or {}).get("lanes")) or []
    return [name for row in rows if isinstance(name := row.get("lane"), str) and name]


def lane_busy(lane: str) -> Value:
    """The share of the last full clock hour a lane was busy, in percent."""

    def value(data: dict[str, Any]) -> float | None:
        for row in _rows(data.get("lanes")) or []:
            if row.get("lane") == lane:
                hours = _rows(row.get("hours")) or []
                # The last entry is the hour still in progress.
                share = _number(hours[-2].get("busy_fraction")) if len(hours) > 1 else None
                return None if share is None else round(share * 100, 1)
        return None

    return value


def details(data: dict[str, Any]) -> dict[str, Any]:
    """A data set as cards get it: without datawatch's one free-text note."""
    ci = _table(data.get("ci_release"))
    release = _table(ci.get("release"))
    if "ship_last_note" not in release:
        return data
    kept = {key: value for key, value in release.items() if key != "ship_last_note"}
    return {**data, "ci_release": {**ci, "release": kept}}


@dataclass(frozen=True)
class Number:
    """A sensor: which data set it reads, how, and its unit."""

    key: str
    dataset: str
    value: Value
    unit: str | None = None


# One per data set: a headline number, with the whole data set as an attribute.
DATA_SENSORS = (
    Number("data_overview", "console", _open_questions),
    Number("data_lane_activity", "lane_pulse", _count("series")),
    Number("data_lane_use", LANES, _count("lanes")),
    Number("data_bugs", "defects_per_day", _field("total_found")),
    Number("data_review", "review_backlog", _field("plan_count")),
    Number("data_forecast", "throughput_forecast", _forecast("throughput_per_day")),
    Number("data_live_work", LIVE_WORK, _field("task_count")),
)
NUMBERS = (
    Number("usage_used", "lane_pulse", _usage("points"), "%"),
    Number("usage_pace", "lane_pulse", _usage("pace_line"), "%"),
    Number("usage_last_day", "lane_pulse", _usage("burn_per_24h"), "%"),
    Number("review_held_questions", "review_backlog", _field("question_count")),
    Number("review_oldest", "review_backlog", _oldest_hours, "h"),
    Number("forecast_low", "throughput_forecast", _forecast("completion_low_days"), "d"),
    Number("forecast_high", "throughput_forecast", _forecast("completion_high_days"), "d"),
)
