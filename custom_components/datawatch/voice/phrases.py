"""Turn what speech-to-text heard into a command, using fixed phrases only.

The words listened for belong to the language: see grammar.py and lang/.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from functools import cache

from .grammar import Grammar
from .language import current


class Kind(Enum):
    """Everything the user can ask for."""

    STATUS = auto()
    DETAIL = auto()
    LIST_PROJECTS = auto()
    MORE = auto()
    SET_NUMBER = auto()
    SET_NAME = auto()
    NUMBER = auto()
    WHERE = auto()
    UNSET = auto()
    REPEAT = auto()
    HELP = auto()
    EXIT = auto()
    QUESTIONS = auto()
    NEXT_QUESTION = auto()
    CHOOSE = auto()
    OWN_WORDS = auto()
    CONFIRM = auto()
    CANCEL = auto()
    ATTENTION = auto()
    PLANS = auto()
    OVERVIEW = auto()
    WHATS_NEXT = auto()
    AUTOMATIONS = auto()
    RUNNING = auto()
    HELD = auto()
    PICK = auto()
    ABOUT = auto()
    WHY = auto()
    TASKS = auto()
    PROGRESS = auto()
    SESSIONS = auto()
    WAITING = auto()
    RUNNING_SESSIONS = auto()
    FAILED_SESSIONS = auto()
    FINISHED = auto()
    RESULTS = auto()
    REPORTS = auto()
    SET_THIS = auto()
    GO_BACK = auto()
    ALL_QUESTIONS = auto()
    ITS_QUESTIONS = auto()
    HISTORY = auto()
    AUTOMATA = auto()
    ADD_AUTOMATON = auto()
    ADD_BUG = auto()
    SEND_SESSION = auto()
    CONFIRM_AUTOMATON = auto()
    CONFIRM_BUG = auto()
    CONFIRM_SEND = auto()
    ALERTS = auto()
    ORDER = auto()
    ORDER_NAME = auto()
    ORDER_RECENT = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class Command:
    """A recognised command. UNKNOWN keeps what was heard.

    item: the kind of thing named in 'set plan two', if one was said.
    """

    kind: Kind
    number: int | None = None
    name: str | None = None
    text: str | None = None
    item: str | None = None


@cache
def _lookup(code: str, phrases: tuple[tuple[str, str], ...]) -> dict[str, Kind]:
    return {phrase: Kind[name] for phrase, name in phrases}


def _fixed(grammar: Grammar, code: str) -> dict[str, Kind]:
    """Each fixed phrase, cleaned as what is heard will be, and the command it gives."""
    pairs = tuple(
        (grammar.clean(said), name) for name, group in grammar.phrases.items() for said in group
    )
    return _lookup(code, pairs)


def _as_number(grammar: Grammar, text: str) -> int | None:
    if text.isdecimal():
        return int(text)
    return grammar.numbers.get(text)


def _unnumbered(grammar: Grammar, text: str) -> str:
    """text without the word for "number", if it was said."""
    found = grammar.number.fullmatch(text)
    return found["chosen"] if found else text


def _parse_set(grammar: Grammar, rest: str) -> Command:
    number = _as_number(grammar, rest)
    if number is not None:
        return Command(Kind.SET_NUMBER, number=number)
    item = grammar.set_item.fullmatch(rest)
    if item is not None:
        kind, chosen = grammar.item_kinds[item["kind"]], _unnumbered(grammar, item["chosen"])
        number = _as_number(grammar, chosen)
        if number is not None:
            return Command(Kind.SET_NUMBER, number=number, item=kind)
        return Command(Kind.SET_NAME, name=chosen, item=kind)
    rest = grammar.set_filler.sub("", rest)
    kind_named = None
    project = grammar.set_project.fullmatch(rest)
    if project is not None:
        kind_named, rest = "project", project["chosen"]
    rest = _unnumbered(grammar, rest)
    number = _as_number(grammar, rest)
    if number is not None:
        return Command(Kind.SET_NUMBER, number=number, item=kind_named)
    return Command(Kind.SET_NAME, name=rest, item=kind_named)


def parse(heard: str) -> Command:
    """Return the command for heard, or UNKNOWN. Never guesses."""
    language = current()
    grammar = language.grammar
    text = grammar.polite.sub("", grammar.clean(heard))
    fixed = _fixed(grammar, language.code)
    if text in fixed:
        return Command(fixed[text])
    own = grammar.own_words.match(heard)
    if own is not None:
        # The user's words exactly as speech-to-text wrote them.
        words = heard[own.end() :].strip()
        return Command(Kind.OWN_WORDS, text=words or None)
    for name, pattern in grammar.actions:
        opening = pattern.match(heard)
        if opening is not None:
            words = heard[opening.end() :].strip()
            return Command(Kind[name], text=words if re.search(r"\w", words) else None)
    for name, pattern in grammar.about_one:
        found = pattern.fullmatch(text)
        if found is not None:
            chosen = _as_number(grammar, found["chosen"])
            if chosen is not None:
                return Command(Kind[name], number=chosen)
    about = grammar.about.fullmatch(text)
    if about is not None:
        chosen = _as_number(grammar, about["chosen"])
        if chosen is not None:
            return Command(Kind.PICK, number=chosen)
        return Command(Kind.ABOUT, name=about["chosen"])
    choice = grammar.choose.fullmatch(text)
    if choice is not None:
        chosen = _as_number(grammar, choice[choice.lastindex or 0])
        if chosen is not None:
            return Command(Kind.CHOOSE, number=chosen)
    setting = grammar.set_command.fullmatch(text)
    if setting is not None:
        return _parse_set(grammar, setting["chosen"])
    number = _as_number(grammar, _unnumbered(grammar, text))
    if number is not None:
        return Command(Kind.NUMBER, number=number)
    return Command(Kind.UNKNOWN, text=" ".join(heard.lower().split()))
