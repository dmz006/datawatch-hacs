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
    Kind.QUESTIONS: (
        "questions",
        "read questions",
        "read my questions",
        "list questions",
        "any questions",
        "open questions",
        "first question",
        "the first question",
        "read the first question",
        "what is the first question",
        "whats the first question",
    ),
    Kind.NEXT_QUESTION: ("next question", "skip", "skip question", "skip this question"),
    Kind.OWN_WORDS: ("my answer", "answer in my own words"),
    # Only these send an answer, so there is no shorter form such as "yes".
    Kind.CONFIRM: ("confirm answer", "confirm the answer", "confirm my answer"),
    Kind.CANCEL: ("cancel", "cancel answer", "cancel the answer", "cancel my answer"),
    Kind.ATTENTION: (
        "attention",
        "needs attention",
        "what needs attention",
        "what needs my attention",
    ),
    Kind.PLANS: (
        "plans",
        "list plans",
        "list the plans",
        "how many plans",
        "how many plans are there",
        "how many plans do we have",
    ),
    Kind.OVERVIEW: ("overview", "project overview"),
    Kind.WHATS_NEXT: ("whats next", "what is next"),
    Kind.AUTOMATIONS: ("automations", "list automations", "list the automations"),
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


# "option two", "answer two", "choose option two".
_CHOOSE = re.compile(
    r"(?:(?:answer|choose|pick) )?option (?:number )?(.+)|(?:answer|choose|pick) (.+)"
)
_OWN_WORDS = re.compile(r"^\W*(?:please\W+)?my\W+answer\W+is\b[\s,:.\-]*", re.IGNORECASE)


def parse(heard: str) -> Command:
    """Return the command for heard, or UNKNOWN. Never guesses."""
    text = _normalise(heard)
    if text in _LOOKUP:
        return Command(_LOOKUP[text])
    own = _OWN_WORDS.match(heard)
    if own is not None:
        # The user's words exactly as speech-to-text wrote them.
        words = heard[own.end() :].strip()
        return Command(Kind.OWN_WORDS, text=words or None)
    choice = _CHOOSE.fullmatch(text)
    if choice is not None:
        chosen = _as_number(choice.group(1) or choice.group(2))
        if chosen is not None:
            return Command(Kind.CHOOSE, number=chosen)
    if text.startswith("set "):
        return _parse_set(text.removeprefix("set "))
    number = _as_number(text.removeprefix("number "))
    if number is not None:
        return Command(Kind.NUMBER, number=number)
    return Command(Kind.UNKNOWN, text=" ".join(heard.lower().split()))
