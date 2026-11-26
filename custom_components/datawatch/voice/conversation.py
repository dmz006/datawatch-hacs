"""Datawatch mode: what is said back, and what is remembered between turns.

Nothing here reads or changes datawatch. An answer leaves as Reply.send, and only after the
user, heard directly, says "confirm answer".
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from . import speech
from .model import Snapshot
from .names import match_names
from .phrases import Command, Kind, parse
from .questions import Draft, Question, explained, ordered, read_back, spoken

PAGE_SIZE = 3
# So that a television or other talk cannot hold the mode open.
MISSES_BEFORE_CLOSING = 3
_NO_LIST = "There is no list yet. Say list projects."
_NOT_UNDERSTOOD = "Sorry, I didn't get that. Say help."
_CLOSING = "Closing datawatch."
_GAVE_UP = f"I didn't understand three times. {_CLOSING}"
_UNREACHABLE = "I can't reach datawatch. Try again, or say stop."
_NEEDS_DATA = frozenset({Kind.STATUS, Kind.DETAIL, Kind.LIST_PROJECTS, Kind.SET_NAME})
_NO_QUESTION = "I haven't read a question yet. Say questions."
_NOT_SENT = "Your answer was not sent."
_WAITING = "Not sent yet. Say confirm answer, or cancel."
_HELP = (
    "You can say: questions, next question, option and a number, my answer, confirm answer, "
    "cancel, status, more detail, list projects, more, set and a number or name, "
    "where am I, unset, repeat, or stop."
)


@dataclass(frozen=True)
class Reply:
    """What to say, and whether datawatch mode ends.

    send is a confirmed answer to send. forward is talk for the AI assistant. The caller
    does either, then reports what happened with sent() or said().
    """

    text: str
    ends: bool = False
    send: Draft | None = None
    forward: str | None = None


class Needs(Enum):
    """What has to be read from datawatch before replying."""

    NOTHING = auto()
    SNAPSHOT = auto()
    QUESTIONS = auto()


def alphabetical(names: tuple[str, ...]) -> list[str]:
    """The default list order."""
    return sorted(names, key=lambda name: (name.casefold(), name))


class Conversation:
    """One user's datawatch mode. The focus outlives each visit to the mode."""

    def __init__(
        self,
        focus: str | None = None,
        silences_before_closing: int | None = 2,
        assistant: bool = False,
    ) -> None:
        """silences_before_closing=None keeps the mode open until the user leaves.

        assistant: whether talk that is not a command goes to an AI assistant.
        """
        self.focus = focus
        self._silence_limit = silences_before_closing
        self._assistant = assistant
        self._reset()

    def _reset(self) -> None:
        self._silences = 0
        # Phrases not understood in a row. Silence does not restart this count.
        self._misses = 0
        self._listed: list[str] | None = None
        self._heard = 0
        self._choosing = False
        self._last = ""
        self._questions: list[Question] = []
        self._at = 0
        # What "more" and "more detail" are about.
        self._reading_questions = False
        self._draft: Draft | None = None
        self._dictating = False

    @property
    def current_question(self) -> Question | None:
        """The question being discussed, if any."""
        if self._reading_questions and self._at < len(self._questions):
            return self._questions[self._at]
        return None

    def needs(self, words: str) -> Needs:
        """What to read from datawatch before calling hear(words, ...)."""
        if self._dictating or self._draft is not None:
            return Needs.NOTHING
        kind = parse(words).kind
        if kind is Kind.QUESTIONS:
            return Needs.QUESTIONS
        if kind is Kind.DETAIL and self.current_question is not None:
            return Needs.NOTHING
        return Needs.SNAPSHOT if kind in _NEEDS_DATA else Needs.NOTHING

    def enter(self) -> Reply:
        """Start a visit: say the focus, forget the previous list."""
        self._reset()
        self._last = "Datawatch activated."
        if self.focus:
            self._last += f" Focus: project {self.focus}."
        return Reply(self._last)

    def silence(self) -> Reply:
        """Nothing was heard."""
        self._silences += 1
        if self._silence_limit is not None and self._silences >= self._silence_limit:
            return self._close(_CLOSING)
        return Reply("Still there?")

    def sent(self, outcome: str) -> Reply:
        """What happened to the answer that was sent."""
        self._last = outcome
        return Reply(outcome)

    def said(self, text: str) -> Reply:
        """What the AI assistant replied."""
        self._last = text
        return Reply(text)

    def hear(
        self,
        words: str,
        snapshot: Snapshot | None,
        questions: list[Question] | None = None,
    ) -> Reply:
        """Answer one thing the user said.

        snapshot and questions are None when they were not read, either because the command
        does not need them or because they could not be.
        """
        self._silences = 0
        command = parse(words)
        reply = self._reply_to(command, words, snapshot, questions)
        if reply.text.endswith((_NOT_UNDERSTOOD, _WAITING)) and command.kind is not Kind.REPEAT:
            self._misses += 1
            if self._misses >= MISSES_BEFORE_CLOSING:
                return self._close(_GAVE_UP)
        else:
            self._misses = 0
        return reply

    def _close(self, text: str) -> Reply:
        if self._draft is not None:
            self._draft = None
            text = f"{_NOT_SENT} {text}"
        return Reply(text, ends=True)

    def _reply_to(
        self,
        command: Command,
        words: str,
        snapshot: Snapshot | None,
        questions: list[Question] | None,
    ) -> Reply:
        if command.kind is Kind.EXIT:
            return self._close(_CLOSING)
        if command.kind is Kind.REPEAT:
            return Reply(self._last)
        if self._dictating:
            return self._dictated(command, words)
        if self._draft is not None:
            return self._confirming(self._draft, command)
        if command.kind is Kind.UNKNOWN and self._assistant:
            return Reply("", forward=words)
        asked = self._about_questions(command, questions)
        if asked is not None:
            return self._say(asked)

        if snapshot is None and command.kind in _NEEDS_DATA:
            return self._say(_UNREACHABLE)

        notice = ""
        if snapshot is not None and self.focus and self.focus not in snapshot.projects:
            notice = f"Project {self.focus} no longer exists, so the focus is cleared. "
            self.focus = None
        if command.kind in (Kind.STATUS, Kind.LIST_PROJECTS, Kind.SET_NAME):
            self._reading_questions = False
        return self._say(notice + self._answer(command, snapshot or Snapshot()))

    def _say(self, text: str) -> Reply:
        self._last = text
        return Reply(text)

    def _about_questions(self, command: Command, questions: list[Question] | None) -> str | None:
        """The reply to a question command, or None if this is some other command."""
        current = self.current_question
        match command.kind:
            case Kind.QUESTIONS:
                if questions is None:
                    return _UNREACHABLE
                self._questions, self._at = ordered(questions), 0
                self._reading_questions = bool(self._questions)
                return self._read_current() if self._questions else "There are no open questions."
            case Kind.NEXT_QUESTION:
                return self._next_question()
            case Kind.MORE if self._reading_questions:
                return self._next_question()
            case Kind.DETAIL if current is not None:
                return explained(current)
            case Kind.CHOOSE:
                return self._choose(command.number or 0)
            case Kind.NUMBER if current is not None and not self._choosing:
                return self._choose(command.number or 0)
            case Kind.OWN_WORDS:
                if current is None:
                    return _NO_QUESTION
                if command.text is None:
                    self._dictating = True
                    return "Go ahead. Say your answer, or cancel."
                return self._drafted(Draft(current, quote=command.text))
            case Kind.CONFIRM | Kind.CANCEL:
                return "There is no answer waiting."
            case _:
                return None

    def _read_current(self) -> str:
        return spoken(self._questions[self._at], self._at + 1, len(self._questions))

    def _next_question(self) -> str:
        if not self._questions:
            return _NO_QUESTION
        self._reading_questions = True
        if self._at + 1 >= len(self._questions):
            self._at = len(self._questions)
            return "That is the last question."
        self._at += 1
        return self._read_current()

    def _choose(self, number: int) -> str:
        current = self.current_question
        if current is None:
            return _NO_QUESTION
        if not 1 <= number <= len(current.options):
            return f"There is no option {number}."
        quote = self._draft.quote if self._draft is not None else None
        return self._drafted(Draft(current, current.options[number - 1], quote))

    def _drafted(self, draft: Draft) -> str:
        self._draft = draft
        return read_back(draft)

    def _dictated(self, command: Command, words: str) -> Reply:
        self._dictating = False
        option = self._draft.option if self._draft is not None else None
        if command.kind is Kind.CANCEL:
            self._draft = None
            return self._say("Cancelled. Nothing was sent.")
        current = self.current_question
        assert current is not None, "dictation only starts on a question"
        quote = command.text if command.kind is Kind.OWN_WORDS and command.text else words
        return self._say(self._drafted(Draft(current, option, quote)))

    def _confirming(self, draft: Draft, command: Command) -> Reply:
        """An answer is waiting: only confirming sends it."""
        match command.kind:
            case Kind.CONFIRM:
                self._draft = None
                return Reply("", send=draft)
            case Kind.CANCEL:
                self._draft = None
                return self._say("Cancelled. Nothing was sent.")
            case Kind.CHOOSE | Kind.NUMBER:
                return self._say(self._choose(command.number or 0))
            case Kind.OWN_WORDS:
                if command.text is None:
                    self._dictating = True
                    return self._say("Go ahead. Say your answer, or cancel.")
                return self._say(self._drafted(Draft(draft.question, draft.option, command.text)))
            case _:
                return Reply(_WAITING)

    def _answer(self, command: Command, snapshot: Snapshot) -> str:
        match command.kind:
            case Kind.STATUS:
                return speech.status(snapshot, self.focus)
            case Kind.DETAIL:
                return speech.detail(snapshot, self.focus)
            case Kind.LIST_PROJECTS:
                return self._start_list(snapshot)
            case Kind.MORE:
                return self._next_page()
            case Kind.SET_NUMBER:
                return self._set_number(command.number or 0)
            case Kind.NUMBER if self._choosing:
                return self._set_number(command.number or 0)
            case Kind.SET_NAME:
                return self._set_name(command.name or "", snapshot)
            case Kind.WHERE:
                if self.focus:
                    return f"Focus: project {self.focus}."
                return "No focus. Showing everything."
            case Kind.UNSET:
                self.focus = None
                self._choosing = False
                return "Focus cleared. Now showing everything."
            case Kind.HELP:
                return _HELP
            case _:
                return _NOT_UNDERSTOOD

    def _start_list(self, snapshot: Snapshot) -> str:
        if not snapshot.projects:
            self._listed = None
            return "There are no projects."
        self._listed, self._heard, self._choosing = alphabetical(snapshot.projects), 0, False
        total = speech.count(len(self._listed), "project", "projects")
        return f"{total}. {self._next_page()}"

    def _next_page(self) -> str:
        if self._listed is None:
            return _NO_LIST
        start = self._heard
        page = self._listed[start : start + PAGE_SIZE]
        if not page:
            return "That is the end of the list."
        self._heard += len(page)
        text = " ".join(f"{start + i}, {name}." for i, name in enumerate(page, start=1))
        more = self._heard < len(self._listed)
        if self._choosing:
            return f"{text} Say more, or which number?" if more else f"{text} Which number?"
        if more:
            return f"{text} Say more, or set and a number or name."
        return f"{text} That is the end of the list."

    def _set_number(self, number: int) -> str:
        if self._listed is None:
            return _NO_LIST
        if not 1 <= number <= self._heard:
            return f"I haven't read a number {number}. Say more, or pick a number you heard."
        return self._set(self._listed[number - 1])

    def _set_name(self, spoken: str, snapshot: Snapshot) -> str:
        matches = match_names(spoken, alphabetical(snapshot.projects))
        if not matches:
            return f"I couldn't find a project matching {spoken}. Say list projects."
        if len(matches) == 1:
            return self._set(matches[0])
        self._listed, self._heard, self._choosing = matches, 0, True
        return f"I found {len(matches)} matches. {self._next_page()}"

    def _set(self, project: str) -> str:
        self.focus = project
        self._choosing = False
        return f"Focus: project {project}."
