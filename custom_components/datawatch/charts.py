"""What datawatch's two dashboard cards draw: a project's Gantt, and lane activity.

datawatch sends large records; only names, titles, states and times are kept.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from typing import Any

# The Gantt's time ranges in days. 0 is all time.
RANGES = (7, 30, 90, 0)
LANE_HOURS = 6
# The most automata listed inside one row; the counts always cover all of them.
AUTOMATA_SHOWN = 100
_DONE = frozenset({"completed", "archived"})
# datawatch states in which nothing more is expected.
_ENDED = frozenset({"completed", "cancelled", "archived"})


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


def _said(moment: datetime | None) -> str | None:
    return None if moment is None else moment.isoformat(timespec="seconds")


class _Automaton:
    """One automaton: when its first task started, and the latest time work finished."""

    def __init__(self, row: dict[str, Any]) -> None:
        self.title = _text(row.get("title"), "untitled")
        self.status = _text(row.get("status"), "unknown")
        self.start = _time(row.get("start"))
        ends = [_time(row.get("end"))]
        ends += [
            _time(task.get("end"))
            for stage in _rows(row.get("stages"))
            for task in _rows(stage.get("members"))
        ]
        self.last = max((end for end in ends if end), default=None) or self.start

    @property
    def done(self) -> bool:
        return self.status in _DONE

    @property
    def ended(self) -> bool:
        return self.status in _ENDED

    def shown(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "status": self.status,
            "start": _said(self.start),
            "last": _said(self.last),
            "open": not self.ended,
        }


def _recent(item: _Automaton, since: datetime | None) -> bool:
    return since is None or (item.last is not None and item.last >= since)


def _stamp(moment: datetime | None) -> float:
    """For sorting by time. No time sorts as longest ago."""
    return moment.timestamp() if moment else 0.0


def _listed(automata: list[_Automaton]) -> list[_Automaton]:
    """Unfinished first, then the most recently worked on."""
    newest = sorted(automata, key=lambda item: _stamp(item.last), reverse=True)
    return sorted(newest, key=lambda item: item.ended)


def _row(ident: str, name: str, state: str, automata: list[_Automaton]) -> dict[str, Any]:
    """One line of the chart. It is finished when every automaton in it is done."""
    finished = bool(automata) and all(item.done for item in automata)
    starts = [item.start for item in automata if item.start]
    lasts = [item.last for item in automata if item.last]
    listed = _listed(automata)
    return {
        "id": ident,
        "name": name,
        "state": state,
        "finished": finished,
        "open": not finished and state not in _ENDED,
        "running": any(item.status == "running" for item in automata),
        "done": sum(item.done for item in automata),
        "unfinished": sum(not item.ended for item in automata),
        "total": len(automata),
        "counts": dict(Counter(item.status for item in automata if not item.done)),
        "start": _said(min(starts, default=None)),
        "last": _said(max(lasts, default=None)),
        "automata": [item.shown() for item in listed[:AUTOMATA_SHOWN]],
        "more": max(len(listed) - AUTOMATA_SHOWN, 0),
    }


def gantt(
    timeline: dict[str, Any], automations: list[dict[str, Any]], now: datetime, days: int
) -> dict[str, Any]:
    """A project's Gantt: every automation holding any of its automata, then the rest.

    timeline is datawatch's timeline filtered to the project. An automation shows only the
    project's automata. days limits finished work to that long ago; 0 is all of it.
    """
    since = now - timedelta(days=days) if days else None
    automata = {
        row["id"]: _Automaton(row)
        for group in _rows(timeline.get("projects"))
        for row in _rows(group.get("automata"))
        if isinstance(row.get("id"), str)
    }
    held: set[str] = set()
    rows = []
    hidden = 0
    for automation in automations:
        members = (member.get("prd_id") for member in _rows(automation.get("members")))
        inside = [i for i in dict.fromkeys(members) if isinstance(i, str) and i in automata]
        if not inside:
            continue
        held.update(inside)
        found = [automata[ident] for ident in inside]
        row = _row(
            _text(automation.get("id"), ""),
            _text(automation.get("name"), "unnamed"),
            _text(automation.get("status"), ""),
            found,
        )
        # Open work always shows, however long ago it was last touched.
        if row["open"] or any(_recent(item, since) for item in found):
            rows.append(row)
        else:
            hidden += 1
    newest = sorted(rows, key=lambda row: _stamp(_time(row["last"])), reverse=True)
    # Rows with work left to do, then others datawatch still has open, then the rest.
    rows = sorted(newest, key=lambda row: (not row["unfinished"], not row["open"]))
    loose = [item for ident, item in automata.items() if ident not in held]
    alone = None
    if loose:
        alone = _row("loose", "Automata in no automation", "", loose)
        alone["open"] = any(not item.ended for item in loose)
        visible = [item for item in _listed(loose) if not item.ended or _recent(item, since)]
        alone["automata"] = [item.shown() for item in visible[:AUTOMATA_SHOWN]]
        alone["more"] = max(len(visible) - AUTOMATA_SHOWN, 0)
    shown = rows + ([alone] if alone else [])
    starts = [moment for row in shown if (moment := _time(row["start"]))]
    first = since or min(starts, default=now - timedelta(days=1))
    return {
        "from": _said(min(first, now - timedelta(hours=1))),
        "to": _said(now),
        "days": days,
        "automations": len(rows) + hidden,
        "automata": len(automata),
        "done": sum(item.done for item in automata.values()),
        "rows": rows,
        "loose": alone,
        "hidden": hidden,
    }


def _percent(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return round(min(max(value, 0), 1) * 100, 1)


def lanes(reply: dict[str, Any], now: datetime) -> dict[str, Any]:
    """How busy each lane was, step by step. A step without a number is left out."""
    found = []
    for row in _rows(reply.get("lanes")):
        points = []
        for bucket in _rows(row.get("buckets")):
            end, busy = _time(bucket.get("end")), _percent(bucket.get("busy_share"))
            if end is not None and busy is not None:
                points.append([_said(end), busy])
        found.append(
            {
                "name": _text(row.get("id"), "unnamed lane"),
                "average": _percent(row.get("busy_share")),
                "points": points,
            }
        )
    to = _time(reply.get("window_end")) or now
    since = _time(reply.get("window_start")) or to - timedelta(hours=LANE_HOURS)
    return {"from": _said(since), "to": _said(to), "lanes": found}
