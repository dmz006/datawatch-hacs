"""Turn what speech-to-text heard into a command, using fixed phrases only."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto


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
    UNKNOWN = auto()


@dataclass(frozen=True)
class Command:
    """A recognised command. UNKNOWN keeps what was heard."""

    kind: Kind
    number: int | None = None
    name: str | None = None
    text: str | None = None


_PHRASES: dict[Kind, tuple[str, ...]] = {
    Kind.STATUS: ("status", "whats the status", "what is the status", "give me status"),
    Kind.DETAIL: ("more detail", "more details", "details", "tell me more"),
    Kind.LIST_PROJECTS: ("list projects", "list the projects", "projects", "list my projects"),
    Kind.MORE: ("more", "next", "next ones", "keep going"),
    Kind.WHERE: ("where am i", "whats my focus", "what is my focus", "whats the focus"),
    Kind.UNSET: ("unset", "un set", "clear focus", "clear the focus"),
    Kind.REPEAT: ("repeat", "repeat that", "say that again", "again"),
    Kind.HELP: ("help", "what can i say"),
    Kind.EXIT: ("stop", "exit", "done", "close datawatch", "close data watch"),
}
_LOOKUP = {phrase: kind for kind, phrases in _PHRASES.items() for phrase in phrases}

_UNITS = [
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
]
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50}
_NUMBER_WORDS = {word: value for value, word in enumerate(_UNITS, start=1)} | _TENS
# What speech-to-text often writes when a number is said on its own.
_HOMOPHONES = {"won": 1, "to": 2, "too": 2, "for": 4, "ate": 8}


def _normalise(heard: str) -> str:
    text = heard.lower().replace("'", "").replace("\N{RIGHT SINGLE QUOTATION MARK}", "")
    text = " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())
    return text.removesuffix(" please").removeprefix("please ")


def _as_number(text: str) -> int | None:
    if text.isdigit():
        return int(text)
    if text in _NUMBER_WORDS:
        return _NUMBER_WORDS[text]
    if text in _HOMOPHONES:
        return _HOMOPHONES[text]
    tens, _, unit = text.partition(" ")
    if tens in _TENS and unit in _UNITS[:9]:
        return _TENS[tens] + _NUMBER_WORDS[unit]
    return None


def _parse_set(rest: str) -> Command:
    number = _as_number(rest)
    if number is not None:
        return Command(Kind.SET_NUMBER, number=number)
    rest = re.sub(r"^(?:the )?(?:focus )?(?:to )?(?:project |number )?", "", rest)
    number = _as_number(rest)
    if number is not None:
        return Command(Kind.SET_NUMBER, number=number)
    return Command(Kind.SET_NAME, name=rest)


def parse(heard: str) -> Command:
    """Return the command for heard, or UNKNOWN. Never guesses."""
    text = _normalise(heard)
    if text in _LOOKUP:
        return Command(_LOOKUP[text])
    if text.startswith("set "):
        return _parse_set(text.removeprefix("set "))
    number = _as_number(text.removeprefix("number "))
    if number is not None:
        return Command(Kind.NUMBER, number=number)
    return Command(Kind.UNKNOWN, text=" ".join(heard.lower().split()))
