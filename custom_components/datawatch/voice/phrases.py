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
    # Like "confirm answer", each of these sends one kind of thing and nothing else.
    Kind.CONFIRM_AUTOMATON: ("confirm automation", "confirm automaton"),
    Kind.CONFIRM_BUG: ("confirm bug",),
    Kind.CONFIRM_SEND: ("confirm send",),
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
    Kind.RUNNING: ("running", "whats running", "what is running", "running automata"),
    Kind.HELD: (
        "held",
        "held items",
        "whats held",
        "what is held",
        "whats on hold",
        "what is on hold",
        "on hold",
    ),
    Kind.WHY: (
        "why",
        "why is it blocked",
        "why is it held",
        "why is it on hold",
        "why is that blocked",
        "why is that held",
        "why is that one blocked",
        "why is that one held",
        "why did it fail",
        "why is it stuck",
    ),
    Kind.TASKS: ("tasks", "show tasks", "list tasks", "its tasks", "what are the tasks"),
    Kind.PROGRESS: ("progress", "how far along is it", "how is it going"),
    Kind.SESSIONS: ("sessions", "list sessions", "list the sessions"),
    Kind.WAITING: ("waiting sessions", "whats waiting", "what is waiting", "waiting for input"),
    Kind.RUNNING_SESSIONS: ("running sessions", "which sessions are running"),
    Kind.FAILED_SESSIONS: ("failed sessions", "which sessions failed"),
    Kind.FINISHED: (
        "finished",
        "what finished",
        "whats finished",
        "recently finished",
        "completed",
        "what completed",
    ),
    Kind.RESULTS: (
        "results",
        "the results",
        "what did it deliver",
        "what did it change",
        "what did it do",
    ),
    Kind.REPORTS: ("reports", "list reports", "my reports", "list my reports"),
    Kind.SET_THIS: (
        "set it",
        "set that",
        "set this",
        "set that one",
        "focus on it",
        "focus on that",
    ),
    Kind.GO_BACK: ("go back", "back", "go up"),
    Kind.ALL_QUESTIONS: ("all questions", "all the questions", "all open questions"),
    Kind.ITS_QUESTIONS: (
        "its questions",
        "questions for it",
        "questions for that",
        "questions about it",
    ),
    Kind.HISTORY: ("history", "what happened", "show history", "decisions"),
    Kind.AUTOMATA: ("automata", "list automata", "its automata", "show automata"),
    Kind.ALERTS: (
        "alerts",
        "list alerts",
        "any alerts",
        "my alerts",
        "unread alerts",
        "what are my alerts",
    ),
}
_PHRASES[Kind.ORDER] = (
    "list order",
    "what order",
    "sort order",
    "what is the list order",
    "whats the list order",
)
_PHRASES[Kind.ORDER_NAME] = (
    "sort by name",
    "order by name",
    "alphabetical",
    "alphabetical order",
    "sort alphabetically",
)
_PHRASES[Kind.ORDER_RECENT] = (
    "most recent first",
    "newest first",
    "recent first",
    "sort by recent",
    "sort by most recent",
    "order by recent",
)
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


# "set plan two", "set the automaton roof repair".
_SET_ITEM = re.compile(
    r"(?:the )?(?:focus )?(?:to )?(?:the )?(plan|automation|automaton|task|session) (.+)"
)


def _parse_set(rest: str) -> Command:
    number = _as_number(rest)
    if number is not None:
        return Command(Kind.SET_NUMBER, number=number)
    item = _SET_ITEM.fullmatch(rest)
    if item is not None:
        kind, chosen = item.group(1), item.group(2).removeprefix("number ")
        number = _as_number(chosen)
        if number is not None:
            return Command(Kind.SET_NUMBER, number=number, item=kind)
        return Command(Kind.SET_NAME, name=chosen, item=kind)
    rest = re.sub(r"^(?:the )?(?:focus )?(?:to )?", "", rest)
    kind = None
    if rest.startswith("project "):
        kind, rest = "project", rest.removeprefix("project ")
    rest = rest.removeprefix("number ")
    number = _as_number(rest)
    if number is not None:
        return Command(Kind.SET_NUMBER, number=number, item=kind)
    return Command(Kind.SET_NAME, name=rest, item=kind)


# "option two", "answer two", "choose option two".
_CHOOSE = re.compile(
    r"(?:(?:answer|choose|pick) )?option (?:number )?(.+)|(?:answer|choose|pick) (.+)"
)
# "why is two blocked", "tasks for two", "tell me about two".
_ABOUT_ONE: tuple[tuple[Kind, re.Pattern[str]], ...] = (
    (Kind.WHY, re.compile(r"why (?:is |did )?(?:number )?(.+?)(?: blocked| held| fail| stuck)?")),
    (Kind.TASKS, re.compile(r"(?:show )?tasks (?:for|of) (?:number )?(.+)")),
    (Kind.PROGRESS, re.compile(r"progress (?:of|on|for) (?:number )?(.+)")),
    (Kind.RESULTS, re.compile(r"results (?:of|for) (?:number )?(.+)")),
    (Kind.ITS_QUESTIONS, re.compile(r"(?:the )?questions (?:for|about|on|of) (?:number )?(.+)")),
    (Kind.HISTORY, re.compile(r"history (?:of|for) (?:number )?(.+)")),
)
_ABOUT = re.compile(r"(?:tell me )?about (?:number )?(.+)")
_OWN_WORDS = re.compile(r"^\W*(?:please\W+)?my\W+answer\W+is\b[\s,:.\-]*", re.IGNORECASE)


def _starting(opening: str) -> re.Pattern[str]:
    """Words that open an action, matched on what speech-to-text wrote."""
    return re.compile(rf"^\W*(?:please\W+)?(?:{opening})\b[\s,:.\-]*", re.IGNORECASE)


# Each may be said alone, or with the words for it in the same breath.
_ACTIONS: tuple[tuple[Kind, re.Pattern[str]], ...] = (
    (
        Kind.ADD_AUTOMATON,
        _starting(r"(?:add|new)\W+(?:(?:a|an|new)\W+){0,2}(?:automation|automaton)"),
    ),
    (Kind.ADD_BUG, _starting(r"(?:add|new|report)\W+(?:(?:a|an|new)\W+){0,2}bug")),
    (
        Kind.SEND_SESSION,
        _starting(r"send\W+to\W+(?:the\W+)?session|send\W+(?:a\W+)?command|tell\W+the\W+session"),
    ),
)


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
    for kind, pattern in _ACTIONS:
        opening = pattern.match(heard)
        if opening is not None:
            words = heard[opening.end() :].strip()
            return Command(kind, text=words if words.strip(" .,!?") else None)
    for kind, pattern in _ABOUT_ONE:
        found = pattern.fullmatch(text)
        if found is not None:
            chosen = _as_number(found.group(1))
            if chosen is not None:
                return Command(kind, number=chosen)
    about = _ABOUT.fullmatch(text)
    if about is not None:
        chosen = _as_number(about.group(1))
        if chosen is not None:
            return Command(Kind.PICK, number=chosen)
        return Command(Kind.ABOUT, name=about.group(1))
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
