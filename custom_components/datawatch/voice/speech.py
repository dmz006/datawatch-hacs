"""Words for counts: status and detail replies."""

from __future__ import annotations

from collections.abc import Sequence

from .language import N_, t, tn
from .model import Snapshot, Tally

# (count, the sentence part for one, and for several)
_Counted = tuple[Tally, str, str]


def join(parts: Sequence[str]) -> str:
    """'a', 'a and b', or 'a, b and c'."""
    if len(parts) < 2:
        return "".join(parts)
    return t("{first} and {last}", first=t(", ").join(parts[:-1]), last=parts[-1])


def _total(tally: Tally, one: str, many: str) -> str:
    words = tn(tally.total, one, many)
    return t("at least {count}", count=words) if tally.capped else words


def _summary(counted: Sequence[_Counted], snapshot: Snapshot, focus: str | None, lead: str) -> str:
    everything = join([_total(*entry) for entry in counted])
    if focus is None:
        return t("{lead}{counts}.", lead=lead, counts=everything)

    # Counts fetched for another focus must not be reported as this one's.
    usable = snapshot.focus == focus
    filtered = [e for e in counted if usable and e[0].in_focus is not None]
    unfiltered = [e for e in counted if e not in filtered]
    if not filtered:
        return t(
            "In project {project}: {lead}{counts} across all projects.",
            project=focus,
            lead=lead,
            counts=everything,
        )

    here = [(tally.in_focus or 0, one, many) for tally, one, many in filtered]
    there = [(tally.total - (tally.in_focus or 0), one, many) for tally, one, many in filtered]
    text = t(
        "In project {project}: {lead}{counts}.",
        project=focus,
        lead=lead,
        counts=join([tn(*entry) for entry in here]),
    )
    if any(number > 0 for number, _, _ in there):
        counts = join([tn(*entry) for entry in there])
        text += " " + t("Elsewhere: {counts}.", counts=counts)
    if unfiltered:
        counts = join([_total(*entry) for entry in unfiltered])
        text += " " + t("{counts} across all projects.", counts=counts)
    return text


def status(snapshot: Snapshot, focus: str | None) -> str:
    """The short status: paused or not, questions, waiting and running sessions."""
    lead = ""
    if snapshot.paused:
        paused = t("all new work is paused.") if focus else t("New work is paused.")
        lead = f"{paused} "
    counted: list[_Counted] = [
        (snapshot.questions, N_("{number} open question"), N_("{number} open questions")),
        (
            snapshot.waiting,
            N_("{number} session waiting for input"),
            N_("{number} sessions waiting for input"),
        ),
        (snapshot.running, N_("{number} running"), N_("{number} running")),
    ]
    return f"{_summary(counted, snapshot, focus, lead)} {more_hint()}"


def more_hint() -> str:
    """What the short status ends with."""
    return t("Say more detail for more.")


def detail(snapshot: Snapshot, focus: str | None) -> str:
    """The follow-up: stuck automata (as datawatch's main view counts them), held, failed."""
    counted: list[_Counted] = [
        (
            snapshot.stuck,
            N_("{number} failed or blocked automaton"),
            N_("{number} failed or blocked automata"),
        ),
        (snapshot.held, N_("{number} held item"), N_("{number} held items")),
        (snapshot.failed, N_("{number} failed session"), N_("{number} failed sessions")),
    ]
    return _summary(counted, snapshot, focus, "")
