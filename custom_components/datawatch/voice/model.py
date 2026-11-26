"""What the conversation needs to know about datawatch at one moment."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Tally:
    """A count. in_focus is None when datawatch cannot filter it, or there is no focus."""

    total: int = 0
    in_focus: int | None = None
    capped: bool = False


@dataclass(frozen=True)
class Snapshot:
    """A read-only picture. A failed read must raise, never appear as zero.

    focus is the project the in_focus counts were fetched for.
    """

    paused: bool = False
    projects: tuple[str, ...] = ()
    focus: str | None = None
    questions: Tally = Tally()
    waiting: Tally = Tally()
    running: Tally = Tally()
    failed: Tally = Tally()
    held: Tally = Tally()
    stuck: Tally = Tally()
