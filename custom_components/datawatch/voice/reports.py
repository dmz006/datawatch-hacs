"""Spoken reports about work: what needs attention, plans, what is next, and automations."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from .speech import count, join


@dataclass(frozen=True)
class Report:
    """A summary, and the lines that can be read after it.

    refs: for lines that can be chosen by number, the automaton id behind each line.
    """

    summary: str
    items: tuple[str, ...] = ()
    refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class Attention:
    """An automaton datawatch lists as needing the user."""

    title: str
    status: str
    held_tasks: int = 0
    id: str = ""


@dataclass(frozen=True)
class Listed:
    """An automaton in a list."""

    id: str
    title: str
    project: str = ""
    done: int = 0
    tasks: int = 0


@dataclass(frozen=True)
class Held:
    """Something on hold, and why."""

    id: str
    title: str
    reason: str = ""
    next_look: str = ""
    project: str = ""


@dataclass(frozen=True)
class Plan:
    """One plan of a project, in datawatch's order."""

    title: str
    state: str
    done: int = 0
    total: int = 0


@dataclass(frozen=True)
class Overview:
    """A project's plans at a glance."""

    project: str
    plan_states: tuple[tuple[str, int], ...] = ()
    plans: int = 0
    archived: int = 0
    done: int = 0
    total: int = 0
    next_automaton: str = ""
    next_plan: str = ""


@dataclass(frozen=True)
class Automation:
    """One automation."""

    name: str
    status: str
    members: int = 0


# The order datawatch's attention statuses are read in.
_ATTENTION_ORDER = ("blocked", "needs_review", "paused")
_STATUS_WORDS = {"needs_review": "waiting for review", "in_progress": "in progress"}
# The order datawatch's web app lists automations in.
_AUTOMATION_ORDER = ("active", "blocked", "paused", "draft", "completed", "cancelled")
_FINISHED = ("completed", "cancelled")
# The most of a reason read as part of a list.
_BRIEF = 100


def words(status: str) -> str:
    """A status as it is said."""
    return _STATUS_WORDS.get(status, status.replace("_", " ")) or "unknown"


def _rank(order: Sequence[str], status: str) -> int:
    return order.index(status) if status in order else len(order)


def _title(text: str) -> str:
    return " ".join(text.split()).rstrip(".") or "untitled"


def attention(rows: Sequence[Attention]) -> Report:
    """Blocked first, then waiting for review, paused, and any other with held tasks."""
    if not rows:
        return Report("Nothing needs your attention.")
    ordered = sorted(rows, key=lambda row: _rank(_ATTENTION_ORDER, row.status))
    counts = Counter(row.status for row in ordered)
    parts = [f"{counts[s]} {words(s)}" for s in _ATTENTION_ORDER if counts[s]]
    others = sum(number for status, number in counts.items() if status not in _ATTENTION_ORDER)
    if others:
        parts.append(f"{others} finished or set aside with tasks held for review")
    need = "automaton needs" if len(rows) == 1 else "automata need"
    summary = f"{len(rows)} {need} attention, across all projects: {join(parts)}."
    items = []
    for number, row in enumerate(ordered, start=1):
        line = f"{number}, {_title(row.title)}: {words(row.status)}"
        if row.held_tasks:
            line += f", {count(row.held_tasks, 'task', 'tasks')} held for review"
        items.append(f"{line}.")
    return Report(summary, tuple(items), tuple(row.id for row in ordered))


def running(rows: Sequence[Listed], total: int, project: str | None) -> Report:
    """The automata running now."""
    where = f"in project {project}" if project else "across all projects"
    if not total:
        return Report(f"No automata are running {where}.")
    summary = f"{count(total, 'automaton is', 'automata are')} running {where}."
    items = []
    for number, row in enumerate(rows, start=1):
        line = f"{number}, {_title(row.title)}"
        if project is None and row.project:
            line += f", project {row.project}"
        if row.tasks:
            line += f", {row.done} of {row.tasks} tasks completed"
        items.append(f"{line}.")
    return Report(summary, tuple(items), tuple(row.id for row in rows))


def _brief(reason: str) -> str:
    """The start of a reason: its first sentence or clause, kept short enough for a list."""
    first = re.split(r"(?<=[.!?;])\s", " ".join(reason.split()), maxsplit=1)[0].rstrip(".;")
    if len(first) <= _BRIEF:
        return first
    return f"{first[:_BRIEF].rsplit(' ', 1)[0]}, and more"


def held(rows: Sequence[Held], total: int) -> Report:
    """What is on hold, with datawatch's reason for each."""
    if not total:
        return Report("Nothing is on hold.")
    summary = (
        f"{count(total, 'item is', 'items are')} on hold, across all projects. "
        "For a full reason say why and its number."
    )
    items = []
    for number, row in enumerate(rows, start=1):
        line = f"{number}, {_title(row.title)}"
        if row.project:
            line += f", project {row.project}"
        line += f". Reason: {_brief(row.reason)}" if row.reason else ". No reason given"
        items.append(f"{line}.")
    return Report(summary, tuple(items), tuple(row.id for row in rows))


def _states(overview: Overview) -> str:
    return join([f"{number} {words(state)}" for state, number in overview.plan_states if number])


def _plan_count(overview: Overview) -> str:
    text = count(overview.plans, "plan", "plans")
    states = _states(overview)
    return f"{text}, {states}" if states else text


def plans_everywhere(overviews: Sequence[Overview]) -> Report:
    """How many plans there are, and which projects have them."""
    with_plans = [o for o in overviews if o.plans]
    total = sum(o.plans for o in with_plans)
    archived = sum(o.archived for o in overviews)
    old = f" Also {archived} archived." if archived else ""
    if not total:
        return Report(f"There are no current plans.{old}")
    summary = (
        f"{count(total, 'current plan', 'current plans')} in "
        f"{count(len(with_plans), 'project', 'projects')}.{old}"
    )
    return Report(summary, tuple(f"Project {o.project}: {_plan_count(o)}." for o in with_plans))


def plans_of(project: str, plans: Sequence[Plan], total: int, archived: int) -> Report:
    """One project's plans, in datawatch's order."""
    old = f" Also {archived} archived." if archived else ""
    if not total:
        return Report(f"Project {project} has no current plans.{old}")
    summary = f"Project {project} has {count(total, 'current plan', 'current plans')}.{old}"
    items = []
    for number, plan in enumerate(plans, start=1):
        line = f"Plan {number}, {_title(plan.title)}: {words(plan.state)}"
        if plan.total:
            line += f", {plan.done} of {plan.total} automata done"
        items.append(f"{line}.")
    return Report(summary, tuple(items))


def _next(overview: Overview) -> str:
    if not overview.next_automaton:
        return "Nothing is marked as next."
    text = f"Next: {_title(overview.next_automaton)}"
    if overview.next_plan:
        text += f", in the plan {_title(overview.next_plan)}"
    return f"{text}."


def overview(data: Overview) -> Report:
    """One project at a glance."""
    parts = [f"Project {data.project}: {_plan_count(data)}."]
    if data.total:
        parts.append(f"{data.done} of {data.total} automata done.")
    if data.archived:
        parts.append(f"{data.archived} plans archived.")
    parts.append(_next(data))
    return Report(" ".join(parts))


def next_everywhere(overviews: Sequence[Overview]) -> Report:
    """What is next in every project that marks something."""
    marked = [o for o in overviews if o.next_automaton]
    if not marked:
        return Report("Nothing is marked as next in any project.")
    summary = f"{count(len(marked), 'project has', 'projects have')} something next."
    return Report(summary, tuple(f"Project {o.project}. {_next(o)}" for o in marked))


def next_in(data: Overview) -> Report:
    """What is next in one project."""
    return Report(f"Project {data.project}. {_next(data)}")


def automations(rows: Sequence[Automation], project: str | None) -> Report:
    """Counts by status, then the unfinished ones in datawatch's order."""
    where = f"Project {project}" if project else "All projects"
    if not rows:
        return Report(f"{where}: no automations.")
    counts = Counter(row.status for row in rows)
    order = sorted(counts, key=lambda status: _rank(_AUTOMATION_ORDER, status))
    parts = join([f"{counts[status]} {words(status)}" for status in order])
    summary = f"{where}: {count(len(rows), 'automation', 'automations')}, {parts}."
    unfinished = sorted(
        (row for row in rows if row.status not in _FINISHED),
        key=lambda row: (_rank(_AUTOMATION_ORDER, row.status), row.name.casefold()),
    )
    items = tuple(
        f"{_title(row.name)}: {words(row.status)}, {count(row.members, 'member', 'members')}."
        for row in unfinished
    )
    return Report(summary, items)
