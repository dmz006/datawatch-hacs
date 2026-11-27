"""The order of the lists the user can choose: by name, or most recent first.

It applies to sessions, automations and running work, which datawatch gives activity times
for. Projects are always by name. Plans, tasks and what is inside a plan or an automation
stay in datawatch's order, which can be the order work runs in.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from enum import StrEnum

# Which lists the choice is about, as said aloud.
APPLIES = "sessions, automations and running work"


class Order(StrEnum):
    """The choices. The values are also what the setting stores."""

    NAME = "name"
    RECENT = "recent"


_SAID = {Order.NAME: "by name", Order.RECENT: "most recent first"}
_OTHER = {Order.NAME: "most recent first", Order.RECENT: "sort by name"}


def chosen(value: object) -> Order:
    """The order a stored setting means. Anything unknown is the default, by name."""
    return Order.RECENT if value == Order.RECENT else Order.NAME


def _when(text: str) -> datetime:
    """A time datawatch gave, to compare. Missing or unreadable counts as longest ago."""
    try:
        found = datetime.fromisoformat(text)
    except ValueError:
        found = None
    return found if found is not None and found.tzinfo else datetime.min.replace(tzinfo=UTC)


def arrange[Row](
    rows: Iterable[Row],
    order: Order,
    name: Callable[[Row], str],
    time: Callable[[Row], str],
) -> list[Row]:
    """rows in the chosen order. Equal or missing times stay in name order."""
    by_name = sorted(rows, key=lambda row: (name(row).casefold(), name(row)))
    if order is Order.NAME:
        return by_name
    return sorted(by_name, key=lambda row: _when(time(row)), reverse=True)


def changed(order: Order) -> str:
    """What to say after the user changes the order."""
    return (
        f"Order: {_SAID[order]}, for {APPLIES}. Say the list again to hear it that way. "
        f"Say {_OTHER[order]} to switch."
    )


def current(order: Order) -> str:
    """What to say when the user asks what the order is."""
    return f"{APPLIES.capitalize()} are listed {_SAID[order]}. Say {_OTHER[order]} to switch."
