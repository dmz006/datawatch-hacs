"""What the Gantt card draws: what each lane ran and which tasks ran, over six hours.

The rules for which bars show follow datawatch's own Gantt card. datawatch sends whole
records, including instructions and history; only titles, states and times are kept.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

HOURS = 6
# The most running, blocked and planning automata read at once.
AUTOMATA = 20
STATUSES = "running,blocked,planning"
_LIVE = frozenset({"in_progress", "running_tests", "verifying"})


def _time(value: object) -> datetime | None:
    """A time datawatch gave. Missing, unreadable and its 'never' value are None."""
    if not isinstance(value, str):
        return None
    try:
        found = datetime.fromisoformat(value)
    except ValueError:
        return None
    return found if found.tzinfo is not None and found.year > 2000 else None


def _rows(value: object) -> list[dict[str, Any]]:
    return [row for row in value if isinstance(row, dict)] if isinstance(value, list) else []


def _text(value: object, instead: str) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else instead


class _Window:
    def __init__(self, end: datetime) -> None:
        self.end = end
        self.start = end - timedelta(hours=HOURS)

    def bar(self, start: datetime, end: datetime, live: bool) -> dict[str, Any] | None:
        """The part of a stretch of work inside the window, if any."""
        if start > self.end or end < self.start:
            return None
        begin = max(start, self.start)
        return {
            "start": begin.isoformat(timespec="seconds"),
            "end": min(max(end, begin), self.end).isoformat(timespec="seconds"),
            "live": live,
        }


def _lane(row: dict[str, Any], window: _Window) -> dict[str, Any]:
    bars = []
    for run in _rows(row.get("runs")):
        start = _time(run.get("start"))
        if start is None:
            continue
        end = _time(run.get("end"))
        bar = window.bar(start, end or window.end, end is None)
        if bar is not None:
            bars.append({"title": _text(run.get("title"), "untitled"), **bar})
    return {"name": _text(row.get("id"), "unnamed lane"), "bars": bars}


def _task(row: dict[str, Any], window: _Window) -> dict[str, Any] | None:
    start = _time(row.get("started_at"))
    if start is None:
        return None
    status = _text(row.get("status"), "unknown")
    live = status in _LIVE
    end = _time(row.get("completed_at"))
    if end is None:
        if not live:
            return None
        end = window.end
    else:
        live = False
    bar = window.bar(start, end, live)
    if bar is None:
        return None
    return {"title": _text(row.get("title"), "untitled"), "status": status, **bar}


def build(lanes: dict[str, Any], listed: dict[str, Any], now: datetime) -> dict[str, Any]:
    """The chart, from datawatch's lane runs and its list of unfinished work.

    The window ends at datawatch's own time when it gives one, so its clock is the only one.
    """
    window = _Window(_time(lanes.get("window_end")) or now)
    automata = _rows(listed.get("prds"))
    work = []
    for row in automata:
        found = (
            _task(task, window)
            for story in _rows(row.get("stories"))
            for task in _rows(story.get("tasks"))
        )
        bars = sorted((bar for bar in found if bar is not None), key=lambda bar: bar["start"])
        if bars:
            work.append(
                {
                    "title": _text(row.get("title"), "untitled"),
                    "status": _text(row.get("status"), "unknown"),
                    "bars": bars,
                }
            )
    total = listed.get("total")
    return {
        "from": window.start.isoformat(timespec="seconds"),
        "to": window.end.isoformat(timespec="seconds"),
        "lanes": [_lane(row, window) for row in _rows(lanes.get("lanes"))],
        "work": work,
        "task_count": sum(len(item["bars"]) for item in work),
        "automata": len(automata),
        # Unfinished automata beyond the most that are read.
        "not_read": max(total - len(automata), 0) if isinstance(total, int) else 0,
    }
