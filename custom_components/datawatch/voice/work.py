"""Spoken words about sessions and finished work.

A session's terminal output is deliberately not here: datawatch returns raw screen text,
which can hold secrets and is not something to read aloud or give to an AI assistant.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from .items import Item
from .language import N_, t, tn
from .order import Order, arrange
from .reports import Report
from .speech import join

_STATE_WORDS = {
    "waiting_input": N_("waiting for input"),
    "running": N_("running"),
    "failed": N_("failed"),
}


def _state_words(state: str) -> str:
    return t(_STATE_WORDS.get(state, state))


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


_LEVELS = {"warn": N_("warning"), "warning": N_("warning"), "error": N_("error")}
_KINDS = {"warning": N_("A warning"), "error": N_("An error")}


def alerts(rows: Sequence[Alert], unread: int, session: Item | None, now: datetime) -> Report:
    """Unread alerts, newest first as datawatch gives them. session limits them to one."""
    if session is not None:
        rows = [row for row in rows if row.session_id == session.id]
        if not rows:
            return Report(
                tn(
                    unread,
                    "datawatch links no unread alerts to the {item}. There is {number} unread "
                    "alert in all. Say unset, then alerts.",
                    "datawatch links no unread alerts to the {item}. There are {number} unread "
                    "alerts in all. Say unset, then alerts.",
                    item=session.spoken(),
                )
            )
        summary = tn(
            len(rows),
            "For the {item}: {number} unread alert, newest first.",
            "For the {item}: {number} unread alerts, newest first.",
            item=session.spoken(),
        )
    elif not unread:
        return Report(t("There are no unread alerts."))
    else:
        summary = tn(
            unread,
            "{number} unread alert, across all projects, newest first.",
            "{number} unread alerts, across all projects, newest first.",
        )
        serious = sum(row.level in _LEVELS for row in rows)
        if serious:
            found = tn(serious, "{number} warning or error", "{number} warnings or errors")
            if unread > len(rows):
                found = t("{found} among the newest {number}", found=found, number=len(rows))
            summary += f" {found}."
    lines, details = [], []
    for number, row in enumerate(rows, start=1):
        title = _name(row.title)
        level = _LEVELS.get(row.level, "")
        when = age(row.at, now)
        lead = f"{t(level)}: " if level else ""
        lines.append(f"{number}, {lead}{title}{f', {when}' if when else ''}.")
        spoken_kind = t(_KINDS.get(level, N_("An alert")))
        kind = t("{kind} from {when}", kind=spoken_kind, when=when) if when else spoken_kind
        details.append(f"{title}. {kind}. {t('To read the rest, open datawatch.')}")
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
        return t("just now")
    if seconds >= 86400:
        return tn(int(seconds // 86400), "{number} day ago", "{number} days ago")
    if seconds >= 3600:
        return tn(int(seconds // 3600), "{number} hour ago", "{number} hours ago")
    return tn(int(seconds // 60), "{number} minute ago", "{number} minutes ago")


def _name(text: str) -> str:
    return " ".join(text.split()).rstrip(".") or t("unnamed")


def session_detail(session: Session, now: datetime) -> str:
    state = _state_words(session.state)
    parts = [t("Session named {name}: {state}.", name=_name(session.name), state=state)]
    if session.project:
        parts.append(t("Project {project}.", project=session.project))
    if session.backend:
        parts.append(t("It uses {backend}.", backend=session.backend))
    ago = age(session.last_activity, now)
    if ago:
        parts.append(t("Last activity {when}.", when=ago))
    parts.append(t("To see what it said, open it in datawatch."))
    return " ".join(parts)


def sessions(
    totals: Sequence[tuple[str, int]],
    rows: Sequence[Session],
    project: str | None,
    now: datetime,
    inside: Item | None = None,
    order: Order = Order.NAME,
) -> Report:
    """Counts by state, then the sessions in the user's order, to be chosen by number.

    inside: the focused automaton or automation the sessions were filtered to.
    """
    # By the name that is said, so one without a name sorts as "unnamed".
    rows = arrange(rows, order, lambda row: _name(row.name), lambda row: row.last_activity)
    where = t("Project {project}", project=project) if project else t("All projects")
    if inside is not None:
        where = t("The {item}", item=inside.spoken())
    counts = [
        t("{number} {state}", number=number, state=_state_words(state)) for state, number in totals
    ]
    summary = t("{where}: sessions, {counts}.", where=where, counts=join(counts))
    items = []
    for number, row in enumerate(rows, start=1):
        line = t(
            "{number}, session named {name}, {state}",
            number=number,
            name=_name(row.name),
            state=_state_words(row.state),
        )
        if project is None and row.project:
            line += ", " + t("project {project}", project=row.project)
        ago = age(row.last_activity, now)
        if ago:
            line += ", " + t("active {when}", when=ago)
        items.append(f"{line}.")
    return Report(
        summary,
        tuple(items),
        tuple(Item("session", row.id, row.name or t("unnamed")) for row in rows),
        tuple(session_detail(row, now) for row in rows),
        inside,
    )


def _shipped(row: Finished) -> str:
    if row.release:
        return t("shipped in {release}", release=row.release)
    if row.shipped is None:
        return ""
    return t("shipped") if row.shipped else t("not shipped")


def finished(rows: Sequence[Finished], total: int, project: str | None) -> Report:
    """Completed automata in datawatch's order: most recently updated first."""
    if not total:
        if project:
            return Report(t("No automata have completed in project {project}.", project=project))
        return Report(t("No automata have completed across all projects."))
    if project:
        completed = tn(
            total,
            "{number} automaton has completed in project {project}.",
            "{number} automata have completed in project {project}.",
            project=project,
        )
    else:
        completed = tn(
            total,
            "{number} automaton has completed across all projects.",
            "{number} automata have completed across all projects.",
        )
    order_note = t(
        "The most recently updated come first, which may not be the order they finished."
    )
    items = []
    for number, row in enumerate(rows, start=1):
        shipped = _shipped(row)
        line = f"{number}, {_name(row.title)}"
        items.append(f"{line}, {shipped}." if shipped else f"{line}.")
    refs = tuple(Item("automaton", row.id, row.title) for row in rows)
    return Report(f"{completed} {order_note}", tuple(items), refs)


def delivery(title: str, status: str, done: int, total: int, record: Delivery | None) -> str:
    """What a finished automaton delivered, as far as datawatch recorded it."""
    parts = [f"{_name(title)}: {t(status.replace('_', ' '))}."]
    if total:
        parts.append(
            tn(
                total,
                "{done} of {number} task completed.",
                "{done} of {number} tasks completed.",
                done=done,
            )
        )
    if record is None:
        parts.append(t("datawatch has no change record for it."))
    else:
        parts.append(
            t(
                "It changed {files} in {packages}, and added {tests}.",
                files=tn(record.files, "{number} file", "{number} files"),
                packages=tn(record.packages, "{number} package", "{number} packages"),
                tests=tn(record.tests, "{number} test", "{number} tests"),
            )
        )
    return " ".join(parts)
