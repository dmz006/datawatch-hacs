"""Reports the user defines: a name, and which things go in it."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

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
    text = text.lower().replace("'", "")
    text = " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())
    text = text.removesuffix(" please").removeprefix("please ")
    text = re.sub(r"^(?:give me|read|run|play)(?: me)?(?: my| the)? ", "", text)
    text = re.sub(r"^(?:my|the) ", "", text)
    return text.removesuffix(" report")


def match(heard: str, reports: Sequence[CustomReport]) -> CustomReport | None:
    """The report heard names, exactly. "daily" and "daily report" both name "Daily report"."""
    wanted = spoken_form(heard)
    return next((r for r in reports if wanted and spoken_form(r.name) == wanted), None)


def listing(reports: Sequence[CustomReport]) -> str:
    """The names of the reports."""
    if not reports:
        return "You have no reports yet. Add one on the datawatch page in Home Assistant."
    names = ", ".join(report.name for report in reports)
    count = "1 report" if len(reports) == 1 else f"{len(reports)} reports"
    return f"You have {count}: {names}. Say a name."


def compose(name: str, parts: Mapping[str, str], items: Sequence[str]) -> str:
    """The spoken report: each chosen part, in the standard order."""
    chosen = [parts[item] for item in ITEMS if item in items and parts.get(item)]
    if not chosen:
        return f"{name} has nothing in it. Change it on the datawatch page in Home Assistant."
    return f"{name}. {' '.join(chosen)}"
