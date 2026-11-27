"""Reports the user defines: a name, and which things go in it."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .grammar import normalise
from .language import current, t, tn

# What a report can hold, in the order it is read.
ITEMS = (
    "status",
    "detail",
    "attention",
    "questions",
    "next",
    "plans",
    "running",
    "held",
    "sessions",
    "automations",
)


@dataclass(frozen=True)
class CustomReport:
    """One report the user defined."""

    name: str
    items: tuple[str, ...]


def spoken_form(text: str) -> str:
    """A report name, or what was heard, reduced to the words that identify the report."""
    grammar = current().grammar
    text = grammar.polite.sub("", normalise(text, grammar.apostrophes))
    for filler in grammar.report_filler:
        text = filler.sub("", text)
    return text


def match(heard: str, reports: Sequence[CustomReport]) -> CustomReport | None:
    """The report heard names, exactly. "daily" and "daily report" both name "Daily report"."""
    wanted = spoken_form(heard)
    return next((r for r in reports if wanted and spoken_form(r.name) == wanted), None)


def listing(reports: Sequence[CustomReport]) -> str:
    """The names of the reports."""
    if not reports:
        return t("You have no reports yet. Add one on the datawatch page in Home Assistant.")
    names = t(", ").join(report.name for report in reports)
    return tn(
        len(reports),
        "You have {number} report: {names}. Say a name.",
        "You have {number} reports: {names}. Say a name.",
        names=names,
    )


def compose(name: str, parts: Mapping[str, str], items: Sequence[str]) -> str:
    """The spoken report: each chosen part, in the standard order."""
    chosen = [parts[item] for item in ITEMS if item in items and parts.get(item)]
    if not chosen:
        return t(
            "{name} has nothing in it. Change it on the datawatch page in Home Assistant.",
            name=name,
        )
    return f"{name}. {' '.join(chosen)}"
