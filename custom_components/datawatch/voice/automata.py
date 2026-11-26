"""Spoken words about single automata: what they are, why they are stuck, and their tasks."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from .items import Decision, Item
from .reports import Report, words
from .speech import count, join
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
    return words(status) if status else "not started"


def _clean(text: str) -> str:
    return " ".join(text.split()).rstrip(".")


def _reason(text: str) -> str:
    text = _clean(text)
    if len(text) <= _REASON:
        return f"{text}."
    return f"{text[:_REASON].rsplit(' ', 1)[0]}, and more. See datawatch for the rest."


def progress(automaton: Automaton) -> str:
    """How many tasks are done, and what the rest are doing."""
    if not automaton.tasks:
        return "It has no tasks."
    counts = Counter(task.status for task in automaton.tasks)
    done = counts.pop("completed", 0)
    text = f"{done} of {count(len(automaton.tasks), 'task', 'tasks')} completed."
    if counts:
        rest = [f"{number} {task_status(status)}" for status, number in counts.most_common()]
        text += f" The rest: {join(rest)}."
    return text


def summary(automaton: Automaton) -> str:
    """What it is, where it belongs and how far it has got."""
    where = f" Project {automaton.project}." if automaton.project else ""
    return (
        f"{_clean(automaton.title)}: {words(automaton.status)}.{where} {progress(automaton)} "
        "Say why, or tasks."
    )


def results(automaton: Automaton) -> str:
    """What it delivered, as far as datawatch recorded it."""
    done = sum(task.status == "completed" for task in automaton.tasks)
    return delivery(
        automaton.title, automaton.status, done, len(automaton.tasks), automaton.delivered
    )


def why(automaton: Automaton) -> str:
    """What datawatch says about why it is not moving. Never guesses."""
    parts = [f"{_clean(automaton.title)} is {words(automaton.status)}."]
    if automaton.hold:
        parts.append(f"It is on hold: {_reason(automaton.hold)}")
    if automaton.reason:
        parts.append(f"datawatch says: {_reason(automaton.reason)}")
    stuck = [task for task in automaton.tasks if task.status in _STUCK]
    if stuck:
        first = stuck[0]
        needs = "task is" if len(stuck) == 1 else "tasks are"
        parts.append(
            f"{len(stuck)} {needs} stuck. First: {_clean(first.title)}, "
            f"{task_status(first.status)}."
        )
    waiting = next((task for task in automaton.tasks if task.reason), None)
    if waiting is not None and not automaton.reason:
        parts.append(f"For the task {_clean(waiting.title)}: {_reason(waiting.reason)}")
    if len(parts) == 1:
        parts.append("datawatch gives no reason.")
    return " ".join(parts)


def tasks(automaton: Automaton) -> Report:
    """Its tasks in order."""
    if not automaton.tasks:
        return Report(f"{_clean(automaton.title)} has no tasks.")
    lines = tuple(
        f"Task {number}, {_clean(task.title)}: {task_status(task.status)}."
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
    text = (
        f"Task {_clean(task.title)}: {task_status(task.status)}. In the automaton "
        f"{_clean(automaton_title)}."
    )
    return f"{text} datawatch says: {_reason(task.reason)}" if task.reason else text


def choices(spoken: str, found: Sequence[tuple[str, str]]) -> Report:
    """Several automata fit a spoken name: (id, title) pairs to choose between."""
    return Report(
        f"I found {len(found)} matching {spoken}. Say a number.",
        tuple(f"{n}, {_clean(title)}." for n, (_, title) in enumerate(found, start=1)),
        tuple(Item("automaton", ident, title) for ident, title in found),
    )
