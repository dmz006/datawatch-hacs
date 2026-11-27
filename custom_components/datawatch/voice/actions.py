"""Things the user can ask datawatch to do. Each is read back and confirmed first."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .items import Item

# The longest name given to something made from spoken words.
TITLE_LIMIT = 80


class Act(Enum):
    """The kinds of action."""

    AUTOMATON = "automaton"
    BUG = "bug"
    SESSION = "session"


# What sends each one. They differ so that confirming one thing can never send another.
CONFIRM_WORDS = {
    Act.AUTOMATON: "confirm automation",
    Act.BUG: "confirm bug",
    Act.SESSION: "confirm send",
}
_NOUN = {Act.AUTOMATON: "automation", Act.BUG: "bug", Act.SESSION: "message"}
_ASK = {
    Act.AUTOMATON: "Go ahead. Say what the automation should do, or cancel.",
    Act.BUG: "Go ahead. Describe the bug, or cancel.",
    Act.SESSION: "Go ahead. Say what to send, or cancel.",
}
SESSION_SEND_OFF = (
    "Sending to a session is not turned on yet. It is waiting for datawatch's access "
    "controls. Nothing was sent."
)
NEEDS_PROJECT = "Set a project first: say list projects, or set and a project name."
NEEDS_SESSION = "Choose a session first: say sessions, then its number."
CANCELLED = "Cancelled. Nothing was sent."


@dataclass(frozen=True)
class Target:
    """Where an action goes: a project, or one session."""

    act: Act
    project: str = ""
    session: Item | None = None

    def spoken(self) -> str:
        """'a new draft automaton in project oak'."""
        if self.act is Act.SESSION:
            assert self.session is not None
            return f"a message to the {self.session.spoken()}"
        if self.act is Act.BUG:
            return f"a bug for project {self.project}"
        return f"a new draft automaton in project {self.project}"


@dataclass(frozen=True)
class Action:
    """An action the user has worded. words are exactly as speech-to-text wrote them."""

    target: Target
    words: str


def ask(act: Act) -> str:
    """What to say before listening for the words."""
    return _ASK[act]


def _sentence(text: str) -> str:
    text = text.strip()
    return text if text.endswith((".", "?", "!")) else f"{text}."


def read_back(action: Action) -> str:
    """Exactly what will be sent, where, and how to send or drop it."""
    where = action.target.spoken()
    return (
        f"Not sent yet. This is {where}. Your words: {_sentence(action.words)} "
        f"Say {CONFIRM_WORDS[action.target.act]} to send it, or cancel."
    )


def waiting(act: Act) -> str:
    """The reply to anything else while an action waits."""
    return f"Not sent yet. Say {CONFIRM_WORDS[act]}, or cancel."


def not_sent(act: Act) -> str:
    """Said when the user leaves with an action waiting."""
    return f"Your {_NOUN[act]} was not sent."


def title_of(words: str) -> str:
    """A short name: the first sentence of the words, cut at a word if still long."""
    text = " ".join(words.split())
    for mark in (". ", "? ", "! "):
        text = text.split(mark, 1)[0]
    text = text.rstrip(".?! ")
    if len(text) > TITLE_LIMIT:
        text = text[:TITLE_LIMIT].rsplit(" ", 1)[0].rstrip(",;: ")
    return text[:1].upper() + text[1:]
