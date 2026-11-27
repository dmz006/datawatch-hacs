"""The things that can have the focus, and the words about them.

The focus is a project (or none) and then a path of items: for example a plan, one of its
automata, and one of that automaton's tasks.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .language import N_, t, tn
from .speech import join

KINDS = ("plan", "automation", "automaton", "task", "session")
_SPOKEN = {
    "plan": N_("plan {title}"),
    "automation": N_("automation {title}"),
    "automaton": N_("automaton {title}"),
    "task": N_("task {title}"),
    "session": N_("session {title}"),
}


@dataclass(frozen=True)
class Item:
    """Something that can have the focus.

    parent is what is needed to find it again: a plan's project, or a task's automaton.
    """

    kind: str
    id: str
    title: str
    parent: str = ""

    def spoken(self) -> str:
        """'the automaton Paint the fence'."""
        return t(_SPOKEN[self.kind], title=clean(self.title))


@dataclass(frozen=True)
class Card:
    """A fresh reading of one item, already in words."""

    status: str
    detail: str
    history: str = ""
    # The project datawatch puts it in, if it says.
    project: str = ""
    # The automata of a plan or an automation, which questions can be linked to.
    automata: frozenset[str] = frozenset()


# What a reading gives when datawatch no longer has the item.
GONE = Card("", "")


def linked(
    item: Item,
    automata: frozenset[str],
    automaton_id: str,
    task_id: str,
    asked_by: str,
    tags: Sequence[str],
) -> bool:
    """Whether datawatch records a question as belonging to an item."""
    if item.kind == "task":
        return task_id == item.id
    if item.kind == "session":
        return asked_by == item.id
    wanted = frozenset({item.id}) if item.kind == "automaton" else automata
    return automaton_id in wanted or any(f"automaton:{ident}" in tags for ident in wanted)


@dataclass(frozen=True)
class Decision:
    """One thing datawatch recorded as done or decided about an item."""

    kind: str
    actor: str = ""
    note: str = ""
    at: str = ""


def clean(text: str) -> str:
    """Tidy a title or note for saying."""
    return " ".join(text.split()).rstrip(".") or t("untitled")


def shorten(text: str, limit: int) -> str:
    """The start of a long text, saying that there is more."""
    text = " ".join(text.split()).rstrip(".")
    if len(text) <= limit:
        return f"{text}."
    return t("{start}, and more. See datawatch for the rest.", start=text[:limit].rsplit(" ", 1)[0])


def describe(project: str | None, path: Sequence[Item]) -> str:
    """'project oak, automaton Paint the fence'. Empty with no focus."""
    parts = [t("project {project}", project=project)] if project else []
    parts += [item.spoken() for item in path]
    return t(", ").join(parts)


def stored(path: Sequence[Item]) -> list[dict[str, str]]:
    """The path in a form that can be saved."""
    return [{"kind": i.kind, "id": i.id, "title": i.title, "parent": i.parent} for i in path]


def restored(saved: Any) -> tuple[Item, ...]:
    """A saved path. Anything that is not one is ignored."""
    if not isinstance(saved, list):
        return ()
    path = []
    for row in saved:
        if not isinstance(row, Mapping) or row.get("kind") not in KINDS:
            return ()
        values = [row.get(key) for key in ("kind", "id", "title", "parent")]
        if not all(isinstance(value, str) for value in values):
            return ()
        path.append(Item(*map(str, values)))
    return tuple(path)


def _latest(decision: Decision) -> str:
    # datawatch's own word for what happened: translated where a language lists it.
    text = t(decision.kind.replace("_", " "))
    if decision.actor:
        text = t("{what}, by {actor}", what=text, actor=decision.actor)
    return f"{text}: {shorten(decision.note, 200)}" if decision.note else f"{text}."


def history(title: str, decisions: Sequence[Decision]) -> str:
    """The last few things recorded, newest first."""
    if not decisions:
        return t("datawatch has no history for {title}.", title=clean(title))
    recent = list(reversed(decisions))[:3]
    lines = [f"{number}, {_latest(d)}" for number, d in enumerate(recent, start=1)]
    return tn(
        len(decisions),
        "{title} has {number} entry. The latest: {lines}",
        "{title} has {number} entries. The latest: {lines}",
        title=clean(title),
        lines=" ".join(lines),
    )


def member_summary(statuses: Sequence[str]) -> str:
    """'5 members: 2 completed and 3 running'. Only the total if any status is unknown."""
    total = tn(len(statuses), "{number} member", "{number} members")
    if not statuses or not all(statuses):
        return total
    counts = Counter(statuses)
    parts = join(
        [
            t("{number} {state}", number=n, state=t(status.replace("_", " ")))
            for status, n in counts.most_common()
        ]
    )
    return f"{total}: {parts}"
