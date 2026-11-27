"""Spoken words about single automata: what they are, why they are stuck, and their tasks."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from .items import Decision, Item, shorten
from .language import t, tn
from .reports import Report, counted, words
from .speech import join
from .work import Delivery, delivery

# The most of one reason that is read out.
_REASON = 600
_STUCK = ("blocked", "failed", "review_needed", "waiting_decision", "awaiting_approval")


@dataclass(frozen=True)
class Task:
    """One task of an automaton."""

    title: str
    status: str = ""
    reason: str = ""
    id: str = ""


@dataclass(frozen=True)
class Automaton:
    """One automaton in detail. hold is why it is on hold, if it is."""

    id: str
    title: str
    status: str
    project: str = ""
    reason: str = ""
    hold: str = ""
    tasks: tuple[Task, ...] = ()
    delivered: Delivery | None = None
    goal: str = ""
    decisions: tuple[Decision, ...] = ()


def task_status(status: str) -> str:
    """datawatch leaves the status empty until a task is first queued."""
    return words(status) if status else t("not started")


def _clean(text: str) -> str:
    return " ".join(text.split()).rstrip(".")


def _reason(text: str) -> str:
    return shorten(_clean(text), _REASON)


def progress(automaton: Automaton) -> str:
    """How many tasks are done, and what the rest are doing."""
    if not automaton.tasks:
        return t("It has no tasks.")
    counts = Counter(task.status for task in automaton.tasks)
    done = counts.pop("completed", 0)
    text = tn(
        len(automaton.tasks),
        "{done} of {number} task completed.",
        "{done} of {number} tasks completed.",
        done=done,
    )
    if counts:
        rest = [
            counted(number, status) if status else t("{number} not started", number=number)
            for status, number in counts.most_common()
        ]
        text += " " + t("The rest: {parts}.", parts=join(rest))
    return text


def what_next() -> str:
    """What a summary ends with."""
    return t("Say why, or tasks.")


def summary(automaton: Automaton) -> str:
    """What it is, where it belongs and how far it has got."""
    parts = [f"{_clean(automaton.title)}: {words(automaton.status)}."]
    if automaton.project:
        parts.append(t("Project {project}.", project=automaton.project))
    parts += [progress(automaton), what_next()]
    return " ".join(parts)


def results(automaton: Automaton) -> str:
    """What it delivered, as far as datawatch recorded it."""
    done = sum(task.status == "completed" for task in automaton.tasks)
    return delivery(
        automaton.title, automaton.status, done, len(automaton.tasks), automaton.delivered
    )


def why(automaton: Automaton) -> str:
    """What datawatch says about why it is not moving. Never guesses."""
    parts = [t("{title} is {state}.", title=_clean(automaton.title), state=words(automaton.status))]
    if automaton.hold:
        parts.append(t("It is on hold: {reason}", reason=_reason(automaton.hold)))
    if automaton.reason:
        parts.append(t("datawatch says: {reason}", reason=_reason(automaton.reason)))
    stuck = [task for task in automaton.tasks if task.status in _STUCK]
    if stuck:
        first = stuck[0]
        parts.append(
            tn(
                len(stuck),
                "{number} task is stuck. First: {title}, {state}.",
                "{number} tasks are stuck. First: {title}, {state}.",
                title=_clean(first.title),
                state=task_status(first.status),
            )
        )
    waiting = next((task for task in automaton.tasks if task.reason), None)
    if waiting is not None and not automaton.reason:
        parts.append(
            t(
                "For the task {title}: {reason}",
                title=_clean(waiting.title),
                reason=_reason(waiting.reason),
            )
        )
    if len(parts) == 1:
        parts.append(t("datawatch gives no reason."))
    return " ".join(parts)


def tasks(automaton: Automaton) -> Report:
    """Its tasks in order."""
    if not automaton.tasks:
        return Report(t("{title} has no tasks.", title=_clean(automaton.title)))
    lines = tuple(
        t(
            "Task {number}, {title}: {state}.",
            number=number,
            title=_clean(task.title),
            state=task_status(task.status),
        )
        for number, task in enumerate(automaton.tasks, start=1)
    )
    under = Item("automaton", automaton.id, automaton.title)
    refs = tuple(
        Item("task", task.id, task.title, automaton.id) for task in automaton.tasks if task.id
    )
    if len(refs) != len(lines):
        return Report(progress(automaton), lines, under=under)
    details = tuple(task_detail(task, automaton.title) for task in automaton.tasks)
    return Report(progress(automaton), lines, refs, details, under)


def task_detail(task: Task, automaton_title: str) -> str:
    """One task: its status, which automaton it is in, and any recorded reason."""
    state = task_status(task.status)
    first = t("Task {title}: {state}.", title=_clean(task.title), state=state)
    text = f"{first} {t('In the automaton {title}.', title=_clean(automaton_title))}"
    if not task.reason:
        return text
    return f"{text} {t('datawatch says: {reason}', reason=_reason(task.reason))}"


def choices(spoken: str, found: Sequence[tuple[str, str]]) -> Report:
    """Several automata fit a spoken name: (id, title) pairs to choose between."""
    return Report(
        t("I found {number} matching {name}. Say a number.", number=len(found), name=spoken),
        tuple(f"{n}, {_clean(title)}." for n, (_, title) in enumerate(found, start=1)),
        tuple(Item("automaton", ident, title) for ident, title in found),
    )
