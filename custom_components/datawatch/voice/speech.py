"""Words for counts: status and detail replies."""

from __future__ import annotations

from collections.abc import Sequence

from .model import Snapshot, Tally

# (count, singular, plural)
_Counted = tuple[Tally, str, str]


def join(parts: Sequence[str]) -> str:
    """'a', 'a and b', or 'a, b and c'."""
    if len(parts) < 2:
        return "".join(parts)
    return f"{', '.join(parts[:-1])} and {parts[-1]}"


def count(number: int, singular: str, plural: str) -> str:
    """'1 project', '2 projects'."""
    return f"{number} {singular if number == 1 else plural}"


def _total(tally: Tally, singular: str, plural: str) -> str:
    words = count(tally.total, singular, plural)
    return f"at least {words}" if tally.capped else words


def _summary(counted: Sequence[_Counted], snapshot: Snapshot, focus: str | None, lead: str) -> str:
    everything = join([_total(*entry) for entry in counted])
    if focus is None:
        return f"{lead}{everything}."

    # Counts fetched for another focus must not be reported as this one's.
    usable = snapshot.focus == focus
    filtered = [e for e in counted if usable and e[0].in_focus is not None]
    unfiltered = [e for e in counted if e not in filtered]
    if not filtered:
        return f"In project {focus}: {lead}{everything} across all projects."

    here = [(tally.in_focus or 0, one, many) for tally, one, many in filtered]
    there = [(tally.total - (tally.in_focus or 0), one, many) for tally, one, many in filtered]
    text = f"In project {focus}: {lead}{join([count(*entry) for entry in here])}."
    if any(number > 0 for number, _, _ in there):
        text += f" Elsewhere: {join([count(*entry) for entry in there])}."
    if unfiltered:
        text += f" {join([_total(*entry) for entry in unfiltered])} across all projects."
    return text


def status(snapshot: Snapshot, focus: str | None) -> str:
    """The short status: paused or not, questions, waiting and running sessions."""
    lead = ""
    if snapshot.paused:
        lead = "all new work is paused. " if focus else "New work is paused. "
    counted: list[_Counted] = [
        (snapshot.questions, "open question", "open questions"),
        (snapshot.waiting, "session waiting for input", "sessions waiting for input"),
        (snapshot.running, "running", "running"),
    ]
    return _summary(counted, snapshot, focus, lead) + " Say more detail for more."


def detail(snapshot: Snapshot, focus: str | None) -> str:
    """The follow-up: failed sessions."""
    return _summary([(snapshot.failed, "failed session", "failed sessions")], snapshot, focus, "")
