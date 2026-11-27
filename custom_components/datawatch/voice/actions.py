"""Things the user can ask datawatch to do. Each is read back and confirmed first."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from .items import Item
from .language import N_, t

# The longest name given to something made from spoken words.
TITLE_LIMIT = 80


class Act(Enum):
    """The kinds of action."""

    AUTOMATON = "automaton"
    BUG = "bug"
    SESSION = "session"


# Whole sentences for each action. Each names its own confirming words, which differ so
# that confirming one thing can never send another.
_ASK = {
    Act.AUTOMATON: N_("Go ahead. Say what the automation should do, or cancel."),
    Act.BUG: N_("Go ahead. Describe the bug, or cancel."),
    Act.SESSION: N_("Go ahead. Say what to send, or cancel."),
}
_CONFIRM_TO_SEND = {
    Act.AUTOMATON: N_("Say confirm automation to send it, or cancel."),
    Act.BUG: N_("Say confirm bug to send it, or cancel."),
    Act.SESSION: N_("Say confirm send to send it, or cancel."),
}
_WAITING = {
    Act.AUTOMATON: N_("Not sent yet. Say confirm automation, or cancel."),
    Act.BUG: N_("Not sent yet. Say confirm bug, or cancel."),
    Act.SESSION: N_("Not sent yet. Say confirm send, or cancel."),
}
_NOT_SENT = {
    Act.AUTOMATON: N_("Your automation was not sent."),
    Act.BUG: N_("Your bug was not sent."),
    Act.SESSION: N_("Your message was not sent."),
}
SESSION_SEND_OFF = N_(
    "Sending to a session is not turned on yet. It is waiting for datawatch's access "
    "controls. Nothing was sent."
)
NEEDS_PROJECT = N_("Set a project first: say list projects, or set and a project name.")
NEEDS_SESSION = N_("Choose a session first: say sessions, then its number.")
CANCELLED = N_("Cancelled. Nothing was sent.")


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
            return t("a message to the {item}", item=self.session.spoken())
        if self.act is Act.BUG:
            return t("a bug for project {project}", project=self.project)
        return t("a new draft automaton in project {project}", project=self.project)


@dataclass(frozen=True)
class Action:
    """An action the user has worded. words are exactly as speech-to-text wrote them."""

    target: Target
    words: str


def ask(act: Act) -> str:
    """What to say before listening for the words."""
    return t(_ASK[act])


def _sentence(text: str) -> str:
    text = text.strip()
    return text if text.endswith((".", "?", "!")) else f"{text}."


def read_back(action: Action) -> str:
    """Exactly what will be sent, where, and how to send or drop it."""
    start = t(
        "Not sent yet. This is {target}. Your words: {words}",
        target=action.target.spoken(),
        words=_sentence(action.words),
    )
    return f"{start} {t(_CONFIRM_TO_SEND[action.target.act])}"


def waiting(act: Act) -> str:
    """The reply to anything else while an action waits."""
    return t(_WAITING[act])


def not_sent(act: Act) -> str:
    """Said when the user leaves with an action waiting."""
    return t(_NOT_SENT[act])


def title_of(words: str) -> str:
    """A short name: the first sentence of the words, cut at a word if still long."""
    text = " ".join(words.split())
    # Japanese ends a sentence with its own marks, and puts no space after them.
    text = re.split(r"[.?!] |[。？！]", text, maxsplit=1)[0]
    text = text.rstrip(".?! 、")
    if len(text) > TITLE_LIMIT:
        text = text[:TITLE_LIMIT].rsplit(" ", 1)[0].rstrip(",;: ")
    return text[:1].upper() + text[1:]
