"""Spoken reports about work: what needs attention, plans, what is next, and automations."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from .items import Decision, Item
from .language import N_, t, tn
from .order import Order, arrange
from .speech import join


@dataclass(frozen=True)
class Report:
    """A summary, and the lines that can be read after it.

    refs: for lines that can be chosen by number, the item behind each line. details: what
    to say when a line is chosen, for lines that are not automata. under: the focused item
    these lines belong to, so that choosing one goes a step further in.
    """

    summary: str
    items: tuple[str, ...] = ()
    refs: tuple[Item, ...] = ()
    details: tuple[str, ...] = ()
    under: Item | None = None


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
    updated: str = ""


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
    id: str = ""
    goal: str = ""
    automata: frozenset[str] = frozenset()
    next_automaton: str = ""


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
    id: str = ""
    description: str = ""
    member_ids: tuple[str, ...] = ()
    decisions: tuple[Decision, ...] = ()
    updated: str = ""


# The order datawatch's attention statuses are read in.
_ATTENTION_ORDER = ("blocked", "needs_review", "paused")
# How some of datawatch's statuses are said. Any other is said as datawatch writes it,
# unless a language translates it.
_STATUS_WORDS = {"needs_review": N_("waiting for review"), "in_progress": N_("in progress")}
# The statuses a language can translate.
_KNOWN_STATUSES = (
    N_("active"), N_("approved"), N_("archived"), N_("awaiting approval"), N_("blocked"),
    N_("cancelled"), N_("completed"), N_("done"), N_("draft"), N_("failed"), N_("held"),
    N_("paused"), N_("planning"), N_("queued"), N_("review needed"), N_("running"),
    N_("waiting decision"),
)  # fmt: skip
# The order datawatch's web app lists automations in.
_AUTOMATION_ORDER = ("active", "blocked", "paused", "draft", "completed", "cancelled")
_FINISHED = ("completed", "cancelled")
# The most of a reason read as part of a list.
_BRIEF = 100


def words(status: str) -> str:
    """A status as it is said."""
    return t(_STATUS_WORDS.get(status, status.replace("_", " "))) or t("unknown")


def counted(number: int, status: str) -> str:
    """'2 running'."""
    return t("{number} {state}", number=number, state=words(status))


def _rank(order: Sequence[str], status: str) -> int:
    return order.index(status) if status in order else len(order)


def _title(text: str) -> str:
    return " ".join(text.split()).rstrip(".") or t("untitled")


def attention(rows: Sequence[Attention]) -> Report:
    """Blocked first, then waiting for review, paused, and any other with held tasks."""
    if not rows:
        return Report(t("Nothing needs your attention."))
    ordered = sorted(rows, key=lambda row: _rank(_ATTENTION_ORDER, row.status))
    counts = Counter(row.status for row in ordered)
    parts = [counted(counts[s], s) for s in _ATTENTION_ORDER if counts[s]]
    others = sum(number for status, number in counts.items() if status not in _ATTENTION_ORDER)
    if others:
        parts.append(t("{number} finished or set aside with tasks held for review", number=others))
    summary = tn(
        len(rows),
        "{number} automaton needs attention, across all projects: {parts}.",
        "{number} automata need attention, across all projects: {parts}.",
        parts=join(parts),
    )
    items = []
    for number, row in enumerate(ordered, start=1):
        line = f"{number}, {_title(row.title)}: {words(row.status)}"
        if row.held_tasks:
            held_for_review = tn(
                row.held_tasks,
                "{number} task held for review",
                "{number} tasks held for review",
            )
            line += f", {held_for_review}"
        items.append(f"{line}.")
    refs = tuple(Item("automaton", row.id, row.title) for row in ordered)
    return Report(summary, tuple(items), refs)


def running(
    rows: Sequence[Listed], total: int, project: str | None, order: Order = Order.NAME
) -> Report:
    """The automata running now, in the user's order."""
    rows = arrange(rows, order, lambda row: row.title, lambda row: row.updated)
    if not total:
        if project:
            return Report(t("No automata are running in project {project}.", project=project))
        return Report(t("No automata are running across all projects."))
    if project:
        summary = tn(
            total,
            "{number} automaton is running in project {project}.",
            "{number} automata are running in project {project}.",
            project=project,
        )
    else:
        summary = tn(
            total,
            "{number} automaton is running across all projects.",
            "{number} automata are running across all projects.",
        )
    items = []
    for number, row in enumerate(rows, start=1):
        line = f"{number}, {_title(row.title)}"
        if project is None and row.project:
            line += ", " + t("project {project}", project=row.project)
        if row.tasks:
            line += ", " + t("{done} of {total} tasks completed", done=row.done, total=row.tasks)
        items.append(f"{line}.")
    refs = tuple(Item("automaton", row.id, row.title) for row in rows)
    return Report(summary, tuple(items), refs)


def _brief(reason: str) -> str:
    """The start of a reason: its first sentence or clause, kept short enough for a list."""
    first = re.split(r"(?<=[.!?;])\s", " ".join(reason.split()), maxsplit=1)[0].rstrip(".;")
    if len(first) <= _BRIEF:
        return first
    return t("{start}, and more", start=first[:_BRIEF].rsplit(" ", 1)[0])


def hold_hint() -> str:
    """What the summary of held items ends with."""
    return t("For a full reason say why and its number.")


def held(rows: Sequence[Held], total: int) -> Report:
    """What is on hold, with datawatch's reason for each."""
    if not total:
        return Report(t("Nothing is on hold."))
    on_hold = tn(
        total,
        "{number} item is on hold, across all projects.",
        "{number} items are on hold, across all projects.",
    )
    summary = f"{on_hold} {hold_hint()}"
    items = []
    for number, row in enumerate(rows, start=1):
        line = f"{number}, {_title(row.title)}"
        if row.project:
            line += ", " + t("project {project}", project=row.project)
        reason = (
            t("Reason: {reason}", reason=_brief(row.reason)) if row.reason else t("No reason given")
        )
        items.append(f"{line}. {reason}.")
    refs = tuple(Item("automaton", row.id, row.title) for row in rows)
    return Report(summary, tuple(items), refs)


def _states(overview: Overview) -> str:
    return join([counted(number, state) for state, number in overview.plan_states if number])


def _plan_count(overview: Overview) -> str:
    text = tn(overview.plans, "{number} plan", "{number} plans")
    states = _states(overview)
    return f"{text}, {states}" if states else text


def _archived(number: int) -> str:
    """' Also 2 archived.', or nothing."""
    return " " + t("Also {number} archived.", number=number) if number else ""


def plans_everywhere(overviews: Sequence[Overview]) -> Report:
    """How many plans there are, and which projects have them."""
    with_plans = [o for o in overviews if o.plans]
    total = sum(o.plans for o in with_plans)
    old = _archived(sum(o.archived for o in overviews))
    if not total:
        return Report(t("There are no current plans.") + old)
    summary = t(
        "{plans} in {projects}.",
        plans=tn(total, "{number} current plan", "{number} current plans"),
        projects=tn(len(with_plans), "{number} project", "{number} projects"),
    )
    return Report(
        summary + old,
        tuple(
            t("Project {project}: {plans}.", project=o.project, plans=_plan_count(o))
            for o in with_plans
        ),
    )


def plans_of(project: str, plans: Sequence[Plan], total: int, archived: int) -> Report:
    """One project's plans, in datawatch's order."""
    old = _archived(archived)
    if not total:
        return Report(t("Project {project} has no current plans.", project=project) + old)
    summary = tn(
        total,
        "Project {project} has {number} current plan.",
        "Project {project} has {number} current plans.",
        project=project,
    )
    items = []
    details = []
    for number, plan in enumerate(plans, start=1):
        line = f"{_title(plan.title)}: {words(plan.state)}"
        if plan.total:
            line += ", " + t("{done} of {total} automata done", done=plan.done, total=plan.total)
        items.append(t("Plan {number}, {line}.", number=number, line=line))
        detail = t("Plan {line}.", line=line)
        if plan.goal:
            detail += " " + t("Its goal: {goal}.", goal=_title(plan.goal))
        details.append(detail)
    refs = tuple(Item("plan", plan.id, plan.title, project) for plan in plans)
    return Report(summary + old, tuple(items), refs, tuple(details))


def _next(overview: Overview) -> str:
    if not overview.next_automaton:
        return t("Nothing is marked as next.")
    if overview.next_plan:
        return t(
            "Next: {title}, in the plan {plan}.",
            title=_title(overview.next_automaton),
            plan=_title(overview.next_plan),
        )
    return t("Next: {title}.", title=_title(overview.next_automaton))


def overview(data: Overview) -> Report:
    """One project at a glance."""
    parts = [t("Project {project}: {plans}.", project=data.project, plans=_plan_count(data))]
    if data.total:
        parts.append(t("{done} of {total} automata done.", done=data.done, total=data.total))
    if data.archived:
        parts.append(t("{number} plans archived.", number=data.archived))
    parts.append(_next(data))
    return Report(" ".join(parts))


def next_everywhere(overviews: Sequence[Overview]) -> Report:
    """What is next in every project that marks something."""
    marked = [o for o in overviews if o.next_automaton]
    if not marked:
        return Report(t("Nothing is marked as next in any project."))
    summary = tn(
        len(marked),
        "{number} project has something next.",
        "{number} projects have something next.",
    )
    return Report(
        summary,
        tuple(t("Project {project}. {next}", project=o.project, next=_next(o)) for o in marked),
    )


def next_in(data: Overview) -> Report:
    """What is next in one project."""
    return Report(t("Project {project}. {next}", project=data.project, next=_next(data)))


def automations(
    rows: Sequence[Automation], project: str | None, order: Order = Order.NAME
) -> Report:
    """Counts by status, then the unfinished ones in the user's order."""
    where = t("Project {project}", project=project) if project else t("All projects")
    if not rows:
        return Report(t("{where}: no automations.", where=where))
    counts = Counter(row.status for row in rows)
    statuses = sorted(counts, key=lambda status: _rank(_AUTOMATION_ORDER, status))
    parts = join([counted(counts[status], status) for status in statuses])
    summary = tn(
        len(rows),
        "{where}: {number} automation, {parts}.",
        "{where}: {number} automations, {parts}.",
        where=where,
        parts=parts,
    )
    unfinished = arrange(
        (row for row in rows if row.status not in _FINISHED),
        order,
        lambda row: row.name,
        lambda row: row.updated,
    )
    lines = []
    for row in unfinished:
        members = tn(row.members, "{number} member", "{number} members")
        lines.append(f"{_title(row.name)}: {words(row.status)}, {members}.")
    return Report(
        summary,
        tuple(f"{number}, {line}" for number, line in enumerate(lines, start=1)),
        tuple(Item("automation", row.id, row.name) for row in unfinished),
        tuple(t("Automation {line}", line=line) for line in lines),
    )


@dataclass(frozen=True)
class Child:
    """Something inside a plan or an automation."""

    id: str
    title: str
    status: str = ""
    # For a task, the automaton it is in.
    parent: str = ""
    within: str = ""


# What an item is called when what is inside it is listed.
_HOLDER = {
    "plan": N_("The plan {title}"),
    "automation": N_("The automation {title}"),
    "automaton": N_("The automaton {title}"),
}


def children(under: Item, kind: str, rows: Sequence[Child], total: int) -> Report:
    """The automata or tasks inside an item. total may be more than the rows read."""
    automata = kind == "automaton"
    name = t(_HOLDER[under.kind], title=_title(under.title))
    if not rows:
        none = (
            t("{name} has no automata.", name=name)
            if automata
            else t("{name} has no tasks.", name=name)
        )
        return Report(none, under=under)
    if automata:
        summary = tn(
            total, "{name} has {number} automaton.", "{name} has {number} automata.", name=name
        )
    else:
        summary = tn(total, "{name} has {number} task.", "{name} has {number} tasks.", name=name)
    if total > len(rows):
        summary += " " + t("I can read the first {number}.", number=len(rows))
    lines = []
    details = []
    for number, row in enumerate(rows, start=1):
        state = words(row.status) if row.status else t("not started")
        title = _title(row.title)
        lines.append(f"{number}, {title}: {state}.")
        detail = (
            t("Automaton {title}: {state}.", title=title, state=state)
            if automata
            else t("Task {title}: {state}.", title=title, state=state)
        )
        if row.within:
            detail += " " + t("In the automaton {title}.", title=_title(row.within))
        details.append(detail)
    return Report(
        summary,
        tuple(lines),
        tuple(Item(kind, row.id, row.title, row.parent) for row in rows),
        tuple(details),
        under,
    )
