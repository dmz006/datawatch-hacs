"""What the conversation needs to know about datawatch at one moment."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    """Something to count. project is None when it cannot be tied to a project."""

    project: str | None


@dataclass(frozen=True)
class Snapshot:
    """A read-only picture. A failed read must raise, never appear as an empty list."""

    paused: bool = False
    projects: tuple[str, ...] = ()
    questions: tuple[Item, ...] = ()
    waiting: tuple[Item, ...] = ()
    running: tuple[Item, ...] = ()
    failed: tuple[Item, ...] = ()
    held: tuple[Item, ...] = ()
