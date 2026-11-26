"""Datawatch mode: what is said back, and what is remembered between turns.

Read only: nothing here can change anything in datawatch. The only state that changes is
the focus, the list being read and the silence count.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import speech
from .model import Snapshot
from .names import match_names
from .phrases import Command, Kind, parse

PAGE_SIZE = 3
_NO_LIST = "There is no list yet. Say list projects."
_NOT_UNDERSTOOD = "Sorry, I didn't get that. Say help."
_CLOSING = "Closing datawatch."
_UNREACHABLE = "I can't reach datawatch. Try again, or say stop."
_NEEDS_DATA = frozenset({Kind.STATUS, Kind.DETAIL, Kind.LIST_PROJECTS, Kind.SET_NAME})
_HELP = (
    "You can say: status, more detail, list projects, more, set and a number or name, "
    "where am I, unset, repeat, or stop."
)


@dataclass(frozen=True)
class Reply:
    """What to say, and whether datawatch mode ends."""

    text: str
    ends: bool = False


def needs_data(words: str) -> bool:
    """Whether answering words means reading datawatch first."""
    return parse(words).kind in _NEEDS_DATA


def alphabetical(names: tuple[str, ...]) -> list[str]:
    """The default list order."""
    return sorted(names, key=lambda name: (name.casefold(), name))


class Conversation:
    """One user's datawatch mode. The focus outlives each visit to the mode."""

    def __init__(self, focus: str | None = None, silences_before_closing: int | None = 2) -> None:
        """silences_before_closing=None keeps the mode open until the user leaves."""
        self.focus = focus
        self._silence_limit = silences_before_closing
        self._reset()

    def _reset(self) -> None:
        self._silences = 0
        self._listed: list[str] | None = None
        self._heard = 0
        self._choosing = False
        self._last = ""

    def enter(self) -> Reply:
        """Start a visit: say the focus, forget the previous list."""
        self._reset()
        self._last = "Datawatch."
        if self.focus:
            self._last += f" Focus: project {self.focus}."
        return Reply(self._last)

    def silence(self) -> Reply:
        """Nothing was heard."""
        self._silences += 1
        if self._silence_limit is not None and self._silences >= self._silence_limit:
            return Reply(_CLOSING, ends=True)
        return Reply("Still there?")

    def hear(self, words: str, snapshot: Snapshot | None) -> Reply:
        """Answer one thing the user said.

        snapshot is None when datawatch was not read, either because the command does not
        need it or because it could not be.
        """
        self._silences = 0
        command = parse(words)
        if command.kind is Kind.EXIT:
            return Reply(_CLOSING, ends=True)
        if command.kind is Kind.REPEAT:
            return Reply(self._last)

        if snapshot is None and command.kind in _NEEDS_DATA:
            self._last = _UNREACHABLE
            return Reply(self._last)

        notice = ""
        if snapshot is not None and self.focus and self.focus not in snapshot.projects:
            notice = f"Project {self.focus} no longer exists, so the focus is cleared. "
            self.focus = None
        self._last = notice + self._answer(command, snapshot or Snapshot())
        return Reply(self._last)

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
