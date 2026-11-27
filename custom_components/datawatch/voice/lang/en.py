"""English: what datawatch mode listens for."""

from __future__ import annotations

import re

from ..grammar import Grammar, Language

_PHRASES: dict[str, tuple[str, ...]] = {
    "STATUS": ("status", "whats the status", "what is the status", "give me status"),
    "DETAIL": ("more detail", "more details", "details", "tell me more"),
    "LIST_PROJECTS": ("list projects", "list the projects", "projects", "list my projects"),
    "MORE": ("more", "next", "next ones", "keep going"),
    "WHERE": ("where am i", "whats my focus", "what is my focus", "whats the focus"),
    "UNSET": ("unset", "un set", "clear focus", "clear the focus"),
    "REPEAT": ("repeat", "repeat that", "say that again", "again"),
    "HELP": ("help", "what can i say"),
    "EXIT": ("stop", "exit", "done", "close datawatch", "close data watch"),
    "QUESTIONS": (
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
    "NEXT_QUESTION": ("next question", "skip", "skip question", "skip this question"),
    "OWN_WORDS": ("my answer", "answer in my own words"),
    # Only these send an answer, so there is no shorter form such as "yes".
    "CONFIRM": ("confirm answer", "confirm the answer", "confirm my answer"),
    # Like "confirm answer", each of these sends one kind of thing and nothing else.
    "CONFIRM_AUTOMATON": ("confirm automation", "confirm automaton"),
    "CONFIRM_BUG": ("confirm bug",),
    "CONFIRM_SEND": ("confirm send",),
    "CANCEL": ("cancel", "cancel answer", "cancel the answer", "cancel my answer"),
    "ATTENTION": (
        "attention",
        "needs attention",
        "what needs attention",
        "what needs my attention",
    ),
    "PLANS": (
        "plans",
        "list plans",
        "list the plans",
        "how many plans",
        "how many plans are there",
        "how many plans do we have",
    ),
    "OVERVIEW": ("overview", "project overview"),
    "WHATS_NEXT": ("whats next", "what is next"),
    "AUTOMATIONS": ("automations", "list automations", "list the automations"),
    "RUNNING": ("running", "whats running", "what is running", "running automata"),
    "HELD": (
        "held",
        "held items",
        "whats held",
        "what is held",
        "whats on hold",
        "what is on hold",
        "on hold",
    ),
    "WHY": (
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
    "TASKS": ("tasks", "show tasks", "list tasks", "its tasks", "what are the tasks"),
    "PROGRESS": ("progress", "how far along is it", "how is it going"),
    "SESSIONS": ("sessions", "list sessions", "list the sessions"),
    "WAITING": ("waiting sessions", "whats waiting", "what is waiting", "waiting for input"),
    "RUNNING_SESSIONS": ("running sessions", "which sessions are running"),
    "FAILED_SESSIONS": ("failed sessions", "which sessions failed"),
    "FINISHED": (
        "finished",
        "what finished",
        "whats finished",
        "recently finished",
        "completed",
        "what completed",
    ),
    "RESULTS": (
        "results",
        "the results",
        "what did it deliver",
        "what did it change",
        "what did it do",
    ),
    "REPORTS": ("reports", "list reports", "my reports", "list my reports"),
    "SET_THIS": (
        "set it",
        "set that",
        "set this",
        "set that one",
        "focus on it",
        "focus on that",
    ),
    "GO_BACK": ("go back", "back", "go up"),
    "ALL_QUESTIONS": ("all questions", "all the questions", "all open questions"),
    "ITS_QUESTIONS": (
        "its questions",
        "questions for it",
        "questions for that",
        "questions about it",
    ),
    "HISTORY": ("history", "what happened", "show history", "decisions"),
    "AUTOMATA": ("automata", "list automata", "its automata", "show automata"),
    "ALERTS": (
        "alerts",
        "list alerts",
        "any alerts",
        "my alerts",
        "unread alerts",
        "what are my alerts",
    ),
}
_PHRASES["ORDER"] = (
    "list order",
    "what order",
    "sort order",
    "what is the list order",
    "whats the list order",
)
_PHRASES["ORDER_NAME"] = (
    "sort by name",
    "order by name",
    "alphabetical",
    "alphabetical order",
    "sort alphabetically",
)
_PHRASES["ORDER_RECENT"] = (
    "most recent first",
    "newest first",
    "recent first",
    "sort by recent",
    "sort by most recent",
    "order by recent",
)
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
# What speech-to-text often writes when a number is said on its own.
_HOMOPHONES = {"won": 1, "to": 2, "too": 2, "for": 4, "ate": 8}
_NUMBERS = (
    {word: value for value, word in enumerate(_UNITS, start=1)}
    | _TENS
    | {
        f"{ten} {unit}": tens + value
        for ten, tens in _TENS.items()
        for value, unit in enumerate(_UNITS[:9], start=1)
    }
    | _HOMOPHONES
)
_KINDS = ("plan", "automation", "automaton", "task", "session")


def _starting(opening: str) -> re.Pattern[str]:
    """Words that open an action, matched on what speech-to-text wrote."""
    return re.compile(rf"^\W*(?:please\W+)?(?:{opening})\b[\s,:.\-]*", re.IGNORECASE)


GRAMMAR = Grammar(
    phrases=_PHRASES,
    numbers=_NUMBERS,
    apostrophes="'\N{RIGHT SINGLE QUOTATION MARK}",
    polite=re.compile(r"^please | please$"),
    number=re.compile(r"(?:number )?(?P<chosen>.+)"),
    own_words=re.compile(r"^\W*(?:please\W+)?my\W+answer\W+is\b[\s,:.\-]*", re.IGNORECASE),
    # Each may be said alone, or with the words for it in the same breath.
    actions=(
        (
            "ADD_AUTOMATON",
            _starting(r"(?:add|new)\W+(?:(?:a|an|new)\W+){0,2}(?:automation|automaton)"),
        ),
        ("ADD_BUG", _starting(r"(?:add|new|report)\W+(?:(?:a|an|new)\W+){0,2}bug")),
        (
            "SEND_SESSION",
            _starting(
                r"send\W+to\W+(?:the\W+)?session|send\W+(?:a\W+)?command|tell\W+the\W+session"
            ),
        ),
    ),
    # "why is two blocked", "tasks for two".
    about_one=(
        (
            "WHY",
            re.compile(
                r"why (?:is |did )?(?:number )?(?P<chosen>.+?)(?: blocked| held| fail| stuck)?"
            ),
        ),
        ("TASKS", re.compile(r"(?:show )?tasks (?:for|of) (?:number )?(?P<chosen>.+)")),
        ("PROGRESS", re.compile(r"progress (?:of|on|for) (?:number )?(?P<chosen>.+)")),
        ("RESULTS", re.compile(r"results (?:of|for) (?:number )?(?P<chosen>.+)")),
        (
            "ITS_QUESTIONS",
            re.compile(r"(?:the )?questions (?:for|about|on|of) (?:number )?(?P<chosen>.+)"),
        ),
        ("HISTORY", re.compile(r"history (?:of|for) (?:number )?(?P<chosen>.+)")),
    ),
    about=re.compile(r"(?:tell me )?about (?:number )?(?P<chosen>.+)"),
    # "option two", "answer two", "choose option two".
    choose=re.compile(
        r"(?:(?:answer|choose|pick) )?option (?:number )?(.+)|(?:answer|choose|pick) (.+)"
    ),
    set_command=re.compile(r"set (?P<chosen>.+)"),
    # "set plan two", "set the automaton roof repair".
    set_item=re.compile(
        r"(?:the )?(?:focus )?(?:to )?(?:the )?"
        r"(?P<kind>plan|automation|automaton|task|session) (?P<chosen>.+)"
    ),
    item_kinds={kind: kind for kind in _KINDS},
    set_filler=re.compile(r"^(?:the )?(?:focus )?(?:to )?"),
    set_project=re.compile(r"project (?P<chosen>.+)"),
    report_filler=(
        re.compile(r"^(?:give me|read|run|play)(?: me)?(?: my| the)? "),
        re.compile(r"^(?:my|the) "),
        re.compile(r" report$"),
    ),
    # Speech-to-text may write the name as two words.
    entry_sentences=("(open|use) (datawatch|data watch)", "(datawatch|data watch)"),
    entry_names=("datawatch", "data watch", "open datawatch", "use datawatch"),
)

LANGUAGE = Language(code="en", grammar=GRAMMAR)
