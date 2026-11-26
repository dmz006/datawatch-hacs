"""Words for counts: status and detail replies."""

from __future__ import annotations

from collections.abc import Sequence

from .model import Item, Snapshot

# (items, singular, plural)
_Counted = tuple[tuple[Item, ...], str, str]


def join(parts: Sequence[str]) -> str:
    """'a', 'a and b', or 'a, b and c'."""
    if len(parts) < 2:
        return "".join(parts)
    return f"{', '.join(parts[:-1])} and {parts[-1]}"


def count(number: int, singular: str, plural: str) -> str:
    """'1 project', '2 projects'."""
    return f"{number} {singular if number == 1 else plural}"


def _summary(counted: Sequence[_Counted], focus: str | None, prefix: str) -> str:
    if focus is None:
        return prefix + join([count(len(items), one, many) for items, one, many in counted]) + "."

    inside, elsewhere, unlinked = [], [], []
    for items, one, many in counted:
        here = sum(item.project == focus for item in items)
        nowhere = sum(item.project is None for item in items)
        inside.append((here, count(here, one, many)))
        elsewhere.append(
            (len(items) - here - nowhere, count(len(items) - here - nowhere, one, many))
        )
        unlinked.append((nowhere, count(nowhere, one, many)))

    text = f"In project {focus}: {prefix}{join([words for _, words in inside])}."
    if any(number for number, _ in elsewhere):
        text += f" Elsewhere: {join([words for _, words in elsewhere])}."
    if any(number for number, _ in unlinked):
        text += f" Not linked: {join([words for number, words in unlinked if number])}."
    return text


def status(snapshot: Snapshot, focus: str | None) -> str:
    """The short status: paused or not, questions, waiting and running sessions."""
    paused = ""
    if snapshot.paused:
        paused = "all new work is paused. " if focus else "New work is paused. "
    counted: list[_Counted] = [
        (snapshot.questions, "open question", "open questions"),
        (snapshot.waiting, "session waiting for input", "sessions waiting for input"),
        (snapshot.running, "running", "running"),
    ]
    return _summary(counted, focus, paused) + " Say more detail for more."


def detail(snapshot: Snapshot, focus: str | None) -> str:
    """The follow-up: alerts, held or blocked items and failed sessions."""
    counted: list[_Counted] = [
        (snapshot.alerts, "unread alert", "unread alerts"),
        (snapshot.held, "held or blocked item", "held or blocked items"),
        (snapshot.failed, "failed session", "failed sessions"),
    ]
    return _summary(counted, focus, "")
