"""Spoken words about sessions and finished work.

A session's terminal output is deliberately not here: datawatch returns raw screen text,
which can hold secrets and is not something to read aloud or give to an AI assistant.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from .items import Item
from .reports import Report
from .speech import count, join

_STATE_WORDS = {"waiting_input": "waiting for input", "running": "running", "failed": "failed"}


@dataclass(frozen=True)
class Session:
    """What can safely be said about a session."""

    id: str
    name: str = ""
    state: str = ""
    project: str = ""
    backend: str = ""
    last_activity: str = ""


@dataclass(frozen=True)
class Alert:
    """An unread alert. Its body is never read: it can be raw terminal text."""

    id: str
    title: str
    level: str = ""
    session_id: str = ""
    at: str = ""


_LEVELS = {"warn": "warning", "warning": "warning", "error": "error"}


def alerts(rows: Sequence[Alert], unread: int, session: Item | None, now: datetime) -> Report:
    """Unread alerts, newest first as datawatch gives them. session limits them to one."""
    total = count(unread, "unread alert", "unread alerts")
    if session is not None:
        rows = [row for row in rows if row.session_id == session.id]
        if not rows:
            return Report(
                f"datawatch links no unread alerts to the {session.spoken()}. There "
                f"{'is' if unread == 1 else 'are'} {total} in all. Say unset, then alerts."
            )
        mine = count(len(rows), "unread alert", "unread alerts")
        summary = f"For the {session.spoken()}: {mine}, newest first."
    elif not unread:
        return Report("There are no unread alerts.")
    else:
        summary = f"{total}, across all projects, newest first."
        serious = sum(row.level in _LEVELS for row in rows)
        if serious:
            among = f" among the newest {len(rows)}" if unread > len(rows) else ""
            warnings = count(serious, "warning or error", "warnings or errors")
            summary += f" {warnings}{among}."
    lines, details = [], []
    for number, row in enumerate(rows, start=1):
        title = _name(row.title)
        level = _LEVELS.get(row.level, "")
        when = age(row.at, now)
        lead = f"{level}: " if level else ""
        lines.append(f"{number}, {lead}{title}{f', {when}' if when else ''}.")
        kind = {"warning": "A warning", "error": "An error"}.get(level, "An alert")
        details.append(
            f"{title}. {kind}{f' from {when}' if when else ''}. To read the rest, open datawatch."
        )
    return Report(summary, tuple(lines), details=tuple(details))


@dataclass(frozen=True)
class Finished:
    """A completed automaton. shipped is None when datawatch does not say."""

    id: str
    title: str
    shipped: bool | None = None
    release: str = ""


@dataclass(frozen=True)
class Delivery:
    """Counts from datawatch's record of what a finished automaton changed."""

    files: int = 0
    packages: int = 0
    tests: int = 0


def age(moment: str, now: datetime) -> str:
    """How long ago, roughly. Empty if the time cannot be understood."""
    try:
        then = datetime.fromisoformat(moment)
        seconds = (now - then).total_seconds()
    except ValueError, TypeError:
        return ""
    if seconds < 90:
        return "just now"
    for size, one, many in ((86400, "day", "days"), (3600, "hour", "hours")):
        if seconds >= size:
            return f"{count(int(seconds // size), one, many)} ago"
    return f"{count(int(seconds // 60), 'minute', 'minutes')} ago"


def _name(text: str) -> str:
    return " ".join(text.split()).rstrip(".") or "unnamed"


def session_detail(session: Session, now: datetime) -> str:
    state = _STATE_WORDS.get(session.state, session.state)
    parts = [f"Session named {_name(session.name)}: {state}."]
    if session.project:
        parts.append(f"Project {session.project}.")
    if session.backend:
        parts.append(f"It uses {session.backend}.")
    ago = age(session.last_activity, now)
    if ago:
        parts.append(f"Last activity {ago}.")
    parts.append("To see what it said, open it in datawatch.")
    return " ".join(parts)


def sessions(
    totals: Sequence[tuple[str, int]],
    rows: Sequence[Session],
    project: str | None,
    now: datetime,
    inside: Item | None = None,
) -> Report:
    """Counts by state, then the sessions, which can be chosen by number.

    inside: the focused automaton or automation the sessions were filtered to.
    """
    where = f"Project {project}" if project else "All projects"
    if inside is not None:
        where = f"The {inside.spoken()}"
    counts = [f"{number} {_STATE_WORDS.get(state, state)}" for state, number in totals]
    summary = f"{where}: sessions, {join(counts)}."
    items = []
    for number, row in enumerate(rows, start=1):
        line = (
            f"{number}, session named {_name(row.name)}, {_STATE_WORDS.get(row.state, row.state)}"
        )
        if project is None and row.project:
            line += f", project {row.project}"
        ago = age(row.last_activity, now)
        if ago:
            line += f", active {ago}"
        items.append(f"{line}.")
    return Report(
        summary,
        tuple(items),
        tuple(Item("session", row.id, row.name or "unnamed") for row in rows),
        tuple(session_detail(row, now) for row in rows),
        inside,
    )


def _shipped(row: Finished) -> str:
    if row.release:
        return f"shipped in {row.release}"
    if row.shipped is None:
        return ""
    return "shipped" if row.shipped else "not shipped"


def finished(rows: Sequence[Finished], total: int, project: str | None) -> Report:
    """Completed automata in datawatch's order: most recently updated first."""
    where = f"in project {project}" if project else "across all projects"
    if not total:
        return Report(f"No automata have completed {where}.")
    summary = (
        f"{count(total, 'automaton has', 'automata have')} completed {where}. The most "
        "recently updated come first, which may not be the order they finished."
    )
    items = []
    for number, row in enumerate(rows, start=1):
        shipped = _shipped(row)
        line = f"{number}, {_name(row.title)}"
        items.append(f"{line}, {shipped}." if shipped else f"{line}.")
    refs = tuple(Item("automaton", row.id, row.title) for row in rows)
    return Report(summary, tuple(items), refs)


def delivery(title: str, status: str, done: int, total: int, record: Delivery | None) -> str:
    """What a finished automaton delivered, as far as datawatch recorded it."""
    parts = [f"{_name(title)}: {status.replace('_', ' ')}."]
    if total:
        parts.append(f"{done} of {count(total, 'task', 'tasks')} completed.")
    if record is None:
        parts.append("datawatch has no change record for it.")
    else:
        parts.append(
            f"It changed {count(record.files, 'file', 'files')} in "
            f"{count(record.packages, 'package', 'packages')}, and added "
            f"{count(record.tests, 'test', 'tests')}."
        )
    return " ".join(parts)
