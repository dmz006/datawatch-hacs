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
