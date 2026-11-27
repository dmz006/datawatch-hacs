"""Operator questions: their order, how they are read out, and an answer waiting to be sent."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .language import t

# How much of a question is read back before an answer is sent. It was read in full earlier.
_REMINDER = 160


@dataclass(frozen=True)
class Option:
    """One of the answers a question offers."""

    id: str
    label: str
    tradeoffs: str = ""


@dataclass(frozen=True)
class Question:
    """A question datawatch is asking the user."""

    id: str
    text: str
    options: tuple[Option, ...] = ()
    asker_kind: str = ""
    blocking: bool = False
    recommended: str | None = None
    rationale: str = ""
    # What it is about, as datawatch records it.
    automaton_id: str = ""
    task_id: str = ""
    asked_by: str = ""
    tags: tuple[str, ...] = ()

    def number_of(self, option_id: str | None) -> int | None:
        """The spoken number of an option."""
        return next(
            (n for n, option in enumerate(self.options, start=1) if option.id == option_id), None
        )


@dataclass(frozen=True)
class Draft:
    """An answer the user has given but not yet confirmed."""

    question: Question
    option: Option | None = None
    quote: str | None = None


def ordered(questions: Iterable[Question]) -> list[Question]:
    """The supervisor's first, and blocking ones first in each group. Otherwise as given."""
    return sorted(questions, key=lambda q: (q.asker_kind != "supervisor", not q.blocking))


def _sentence(text: str) -> str:
    text = text.strip()
    return text if text.endswith((".", "?", "!")) else f"{text}."


def spoken(question: Question, number: int, total: int) -> str:
    """The whole question, its options and the asker's recommendation."""
    opening = (
        t("Question {number} of {total}, from the supervisor.", number=number, total=total)
        if question.asker_kind == "supervisor"
        else t("Question {number} of {total}, from datawatch.", number=number, total=total)
    )
    parts = [opening]
    if question.blocking:
        parts.append(t("It is blocking work."))
    parts.append(_sentence(question.text))
    parts += [
        _sentence(t("Option {number}: {label}", number=n, label=option.label))
        for n, option in enumerate(question.options, start=1)
    ]
    recommended = question.number_of(question.recommended)
    if recommended is not None:
        parts.append(t("The asker recommends option {number}.", number=recommended))
    parts.append(t("Say option and a number, my answer, more detail, or next question."))
    return " ".join(parts)


def explained(question: Question) -> str:
    """What each option costs or gives, and why the asker recommends one."""
    parts = [
        _sentence(t("Option {number}: {label}", number=n, label=option.tradeoffs))
        for n, option in enumerate(question.options, start=1)
        if option.tradeoffs
    ]
    if question.rationale:
        why = t("Why the asker recommends it: {reason}", reason=question.rationale)
        parts.append(_sentence(why))
    return " ".join(parts) or t("This question has no more detail.")


def _reminder(text: str) -> str:
    text = " ".join(text.split())
    if len(text) <= _REMINDER:
        return text
    return text[:_REMINDER].rsplit(" ", 1)[0]


def read_back(draft: Draft) -> str:
    """Exactly what will be sent, and how to send or drop it."""
    parts = [
        t("Not sent yet."),
        _sentence(t("The question begins: {words}", words=_reminder(draft.question.text))),
    ]
    if draft.option is not None:
        number = draft.question.number_of(draft.option.id)
        choice = t("Your choice: option {number}, {label}", number=number, label=draft.option.label)
        parts.append(_sentence(choice))
    if draft.quote is not None:
        parts.append(_sentence(t("Your words: {words}", words=draft.quote)))
    parts.append(t("Say confirm answer to send it, or cancel."))
    return " ".join(parts)
