"""Datawatch mode: what is said back, and what is remembered between turns.

Nothing here reads or changes datawatch. An answer leaves as Reply.send, and only after the
user, heard directly, says "confirm answer". Any other action leaves as Reply.act, only
after its own confirming words.

The focus is a project and then a path of items. Commands about "it" apply to the item the
user last chose, or else to the end of that path.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum, auto

from . import actions, automata, custom, items, speech
from . import order as order_words
from .actions import Act, Action, Target
from .automata import Automaton
from .custom import CustomReport
from .items import GONE, KINDS, Card, Item
from .model import Snapshot
from .names import match_names
from .order import Order
from .phrases import Command, Kind, parse
from .questions import Draft, Question, explained, ordered, read_back, spoken
from .reports import Report

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
    "cancel, status, more detail, attention, running, held items, tell me about a number "
    "or name, why, tasks, progress, results, what finished, sessions, waiting sessions, "
    "running sessions, failed sessions, plans, overview, what's next, automations, "
    "reports or a report's name, "
    "list projects, more, set and a number or name, set it, its questions, all questions, "
    "automata, history, add automation, add bug, send to session, go back, where am I, "
    "alerts, list order, sort by name, most recent first, unset, repeat, or stop."
)
_ORDERS = {Kind.ORDER_NAME: Order.NAME, Kind.ORDER_RECENT: Order.RECENT}
_NO_AUTOMATON = "Say attention, running or held items, then a number."
_ABOUT_AUTOMATON = (Kind.WHY, Kind.TASKS, Kind.PROGRESS, Kind.RESULTS)
_SESSIONS_ONLY = "That is a session. I can only say what is in the list and its details."
_NOTHING_CHOSEN = "Choose something first: say its number, then set it."
_NO_HISTORY_TARGET = "Choose something first, then say history."
_NO_QUESTION_TARGET = "Choose something first, then say its questions. Or say questions."
_NO_PARENT = "Say plans or automations, choose one, then say automata."
_NO_TASKS = "Tasks are listed for a plan or an automaton."
_NOTHING_BEHIND = "There is nothing to go back to."
_CLEARED = "Focus cleared. Now showing everything."
# Things that hold automata.
_HOLDERS = ("plan", "automation")
# How many steps "go back" remembers.
_TRAIL = 50
_ACT_OF = {
    Kind.ADD_AUTOMATON: Act.AUTOMATON,
    Kind.ADD_BUG: Act.BUG,
    Kind.SEND_SESSION: Act.SESSION,
}
_CONFIRMS = {
    Kind.CONFIRM_AUTOMATON: Act.AUTOMATON,
    Kind.CONFIRM_BUG: Act.BUG,
    Kind.CONFIRM_SEND: Act.SESSION,
}
_NOTHING_WAITING = "There is nothing waiting to be sent."
_QUESTION_WORDS = (Kind.QUESTIONS, Kind.ALL_QUESTIONS, Kind.ITS_QUESTIONS)


class Topic(Enum):
    """What a report is about."""

    ATTENTION = auto()
    PLANS = auto()
    OVERVIEW = auto()
    NEXT = auto()
    AUTOMATIONS = auto()
    RUNNING = auto()
    HELD = auto()
    SESSIONS = auto()
    WAITING = auto()
    RUNNING_SESSIONS = auto()
    FAILED_SESSIONS = auto()
    FINISHED = auto()
    ALERTS = auto()


_TOPICS = {
    Kind.ALERTS: Topic.ALERTS,
    Kind.ATTENTION: Topic.ATTENTION,
    Kind.PLANS: Topic.PLANS,
    Kind.OVERVIEW: Topic.OVERVIEW,
    Kind.WHATS_NEXT: Topic.NEXT,
    Kind.AUTOMATIONS: Topic.AUTOMATIONS,
    Kind.RUNNING: Topic.RUNNING,
    Kind.HELD: Topic.HELD,
    Kind.SESSIONS: Topic.SESSIONS,
    Kind.WAITING: Topic.WAITING,
    Kind.RUNNING_SESSIONS: Topic.RUNNING_SESSIONS,
    Kind.FAILED_SESSIONS: Topic.FAILED_SESSIONS,
    Kind.FINISHED: Topic.FINISHED,
}


def topic_of(words: str) -> Topic | None:
    """The report words ask for, if any."""
    return _TOPICS.get(parse(words).kind)


@dataclass(frozen=True)
class Reply:
    """What to say, and whether datawatch mode ends.

    send is a confirmed answer to send, act a confirmed action, and forward is talk for the
    AI assistant. The caller does it, then reports what happened with sent() or said().
    """

    text: str
    ends: bool = False
    send: Draft | None = None
    forward: str | None = None
    act: Action | None = None
    # A list order the user has just chosen, to be saved.
    order: Order | None = None


class Needs(Enum):
    """What has to be read from datawatch before replying."""

    NOTHING = auto()
    SNAPSHOT = auto()
    QUESTIONS = auto()
    REPORT = auto()
    AUTOMATON = auto()
    SEARCH = auto()
    CUSTOM = auto()
    CARD = auto()
    CHILDREN = auto()
    FIND_ITEM = auto()


@dataclass(frozen=True)
class _State:
    """Where the user is: what "go back" restores. A waiting answer is never part of it."""

    focus: str | None
    path: tuple[Item, ...]
    projects: list[str] | None
    projects_heard: int
    choosing: bool
    questions: list[Question]
    at: int
    reading_questions: bool
    lines: tuple[str, ...] | None
    lines_read: int
    refs: tuple[Item, ...]
    details: tuple[str, ...]
    under: Item | None
    selected: Item | None

    def place(self) -> tuple[object, ...]:
        """What makes this a different place. Hearing more of one list does not."""
        return (
            self.focus,
            self.path,
            id(self.projects),
            self.choosing,
            id(self.questions),
            self.at,
            self.reading_questions,
            id(self.lines),
            self.selected,
        )


def _same(one: Item, other: Item) -> bool:
    return (one.kind, one.id) == (other.kind, other.id)


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
        reports: tuple[CustomReport, ...] = (),
        path: tuple[Item, ...] = (),
        session_send: bool = False,
        order: Order = Order.NAME,
    ) -> None:
        """silences_before_closing=None keeps the mode open until the user leaves.

        assistant: whether talk that is not a command goes to an AI assistant.
        """
        self.focus = focus
        self.path = path
        self._silence_limit = silences_before_closing
        self._assistant = assistant
        self._reports = reports
        self._session_send = session_send
        self.order = order
        self._reset()

    def _reset(self) -> None:
        self._silences = 0
        # Phrases not understood in a row. Silence does not restart this count.
        self._misses = 0
        self._listed: list[str] | None = None
        self._heard_count = 0
        self._choosing = False
        self._last = ""
        self._questions: list[Question] = []
        self._at = 0
        # What "more" and "more detail" are about.
        self._reading_questions = False
        self._draft: Draft | None = None
        self._dictating = False
        # An action whose words are awaited, and one waiting to be confirmed.
        self._wording: Target | None = None
        self._pending: Action | None = None
        # A report's lines, and how many have been read.
        self._lines: tuple[str, ...] | None = None
        self._lines_read = 0
        # The automaton ids behind numbered lines, and the one being discussed.
        self._refs: tuple[Item, ...] = ()
        self._details: tuple[str, ...] = ()
        self._under: Item | None = None
        self._selected: Item | None = None
        # Earlier places with what was said there, and what was said here.
        self._trail: list[tuple[_State, str]] = []
        self._here = ""

    @property
    def current_question(self) -> Question | None:
        """The question being discussed, if any."""
        if self._reading_questions and self._at < len(self._questions):
            return self._questions[self._at]
        return None

    def needs(self, words: str) -> Needs:
        """What to read from datawatch before calling hear(words, ...).

        For questions about a plan or an automation, wanted_card() is needed as well.
        """
        if self._holding:
            return Needs.NOTHING
        command = parse(words)
        kind = command.kind
        if kind is Kind.GO_BACK:
            return Needs.NOTHING
        if kind in _QUESTION_WORDS:
            return Needs.QUESTIONS
        found = self._to_set(command)
        if found:
            return Needs.CARD if len(found) == 1 else Needs.NOTHING
        if self.wanted_item_search(words) is not None:
            return Needs.FIND_ITEM
        if self.wanted_children(words) is not None:
            return Needs.CHILDREN
        if kind in _TOPICS:
            return Needs.REPORT
        if kind is Kind.UNKNOWN and self.wanted_report(words) is not None:
            return Needs.CUSTOM
        if kind is Kind.ABOUT:
            return Needs.SEARCH
        if self.wanted_automaton(words) is not None:
            return Needs.AUTOMATON
        if self.wanted_card(words) is not None:
            return Needs.CARD
        if kind is Kind.DETAIL and self.current_question is not None:
            return Needs.NOTHING
        return Needs.SNAPSHOT if kind in _NEEDS_DATA else Needs.NOTHING

    @property
    def _holding(self) -> bool:
        """Whether something is being dictated or waits to be confirmed."""
        return (
            self._dictating
            or self._draft is not None
            or self._wording is not None
            or self._pending is not None
        )

    def wanted_report(self, words: str) -> CustomReport | None:
        """The user's own report that words name, if any."""
        return custom.match(words, self._reports)

    @property
    def target(self) -> Item | None:
        """What "it" means: the item last chosen, or else the focused one."""
        if self._selected is not None:
            return self._selected
        return self.path[-1] if self.path else None

    @property
    def session_scope(self) -> Item | None:
        """The focused automaton or automation that sessions are limited to, if any."""
        return next((i for i in reversed(self.path) if i.kind in ("automaton", "automation")), None)

    def report_scope(self, topic: Topic) -> Item | None:
        """The focused item a report is limited to, beyond the project."""
        if topic is Topic.ALERTS:
            # datawatch links an alert only to a session.
            last = self.path[-1] if self.path else None
            return last if last is not None and last.kind == "session" else None
        return self.session_scope

    def _line(self, number: int) -> Item | None:
        """The item behind a numbered line the user has heard."""
        read = min(self._lines_read, len(self._refs))
        return self._refs[number - 1] if 1 <= number <= read else None

    def _picks(self, command: Command) -> bool:
        """Whether command chooses a numbered line."""
        if command.kind is Kind.PICK:
            return True
        return command.kind is Kind.NUMBER and self.current_question is None and not self._choosing

    @staticmethod
    def matching(found: tuple[Item, ...], kind: str | None, name: str) -> list[Item]:
        """The items of that kind, or of any kind, whose title fits a spoken name."""
        wanted = [item for item in found if kind is None or item.kind == kind]
        titles = set(match_names(name, [item.title for item in wanted]))
        return [item for item in wanted if item.title in titles]

    def _to_set(self, command: Command) -> list[Item]:
        """The items a set command could mean among what the user has been hearing."""
        if command.item == "project":
            return []
        if command.kind is Kind.SET_THIS:
            return [self._selected] if self._selected is not None else []
        if command.kind is Kind.SET_NUMBER:
            found = self._line(command.number or 0)
            if found is None or command.item not in (None, found.kind):
                return []
            return [found]
        if command.kind is Kind.SET_NAME:
            return self.matching(self._refs, command.item, command.name or "")
        return []

    def wanted_item_search(self, words: str) -> tuple[str, str] | None:
        """The (kind, name) to look for, for 'set plan roof' when no such line was read."""
        command = parse(words)
        if command.kind is not Kind.SET_NAME or command.item not in KINDS:
            return None
        if self._to_set(command):
            return None
        return command.item, command.name or ""

    def wanted_children(self, words: str) -> tuple[Item, str] | None:
        """The item to list the inside of, and whether its automata or its tasks."""
        command = parse(words)
        if command.kind is Kind.AUTOMATA:
            chain = [self._selected, *reversed(self.path)]
            holder = next((i for i in chain if i is not None and i.kind in _HOLDERS), None)
            return (holder, "automaton") if holder is not None else None
        if command.kind is Kind.TASKS:
            item = self.target if command.number is None else self._line(command.number)
            if item is not None and item.kind == "plan":
                return item, "task"
        return None

    def wanted_automaton(self, words: str) -> str | None:
        """The id of the automaton to read before replying to words, if one is meant."""
        command = parse(words)
        if self._picks(command) or (
            command.kind in _ABOUT_AUTOMATON and command.number is not None
        ):
            item = self._line(command.number or 0)
        elif command.kind in _ABOUT_AUTOMATON:
            item = self.target
        else:
            return None
        return item.id if item is not None and item.kind == "automaton" else None

    def _question_scope(self, command: Command) -> Item | None:
        """The item that a request for questions is limited to, if any.

        Only the focus narrows plain "questions": hearing about an item must not hide the
        others. "Its questions" and a line number ask about one item.
        """
        match command.kind:
            case Kind.QUESTIONS:
                return self.path[-1] if self.path else None
            case Kind.ITS_QUESTIONS if command.number is None:
                return self.target
            case Kind.ITS_QUESTIONS:
                return self._line(command.number or 0)
            case _:
                return None

    def wanted_card(self, words: str) -> Item | None:
        """The item to read before replying to words, if one is meant."""
        if self._holding:
            return None
        command = parse(words)
        found = self._to_set(command)
        if found:
            return found[0] if len(found) == 1 else None
        match command.kind:
            case Kind.QUESTIONS | Kind.ITS_QUESTIONS:
                scope = self._question_scope(command)
                return scope if scope is not None and scope.kind in _HOLDERS else None
            case Kind.STATUS:
                return self.path[-1] if self.path else None
            case Kind.DETAIL:
                return None if self.current_question is not None else self.target
            case Kind.HISTORY:
                return self.target if command.number is None else self._line(command.number)
            case Kind.WHY | Kind.PROGRESS | Kind.RESULTS:
                item = self.target if command.number is None else self._line(command.number)
                # Automata have their own wording, and a session has only its details.
                if item is None or item.kind in ("automaton", "session"):
                    return None
                return item
            case _:
                return None

    def enter(self) -> Reply:
        """Start a visit: say the focus, forget the previous list."""
        self._reset()
        self._last = "Datawatch activated."
        if self.focus or self.path:
            self._last += f" {self._where()}"
        return Reply(self._last)

    def _where(self) -> str:
        described = items.describe(self.focus, self.path)
        return f"Focus: {described}." if described else "No focus. Showing everything."

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
        report: Report | None = None,
        automaton: Automaton | None = None,
        composed: str | None = None,
        card: Card | None = None,
    ) -> Reply:
        """Answer one thing the user said.

        snapshot, questions, report, automaton and card are None when they were not read,
        either because the command does not need them or because they could not be. For a
        search by name, give the automaton if one matched, otherwise a report. card is the
        reading of wanted_card(), or of the one item a search matched.
        """
        self._silences = 0
        command = parse(words)
        before = self._state()
        held = self._holding
        reply = self._heard(command, words, snapshot, questions, report, automaton, composed, card)
        if command.kind not in (Kind.GO_BACK, Kind.REPEAT):
            if self._state().place() != before.place():
                self._trail = [*self._trail, (before, self._here)][-_TRAIL:]
                self._here = reply.text
            elif command.kind is Kind.MORE and not held:
                self._here = reply.text
        unmoved = (_NOT_UNDERSTOOD, _WAITING, *(actions.waiting(act) for act in Act))
        if reply.text.endswith(unmoved) and command.kind is not Kind.REPEAT:
            self._misses += 1
            if self._misses >= MISSES_BEFORE_CLOSING:
                return self._close(_GAVE_UP)
        else:
            self._misses = 0
        return reply

    def _heard(
        self,
        command: Command,
        words: str,
        snapshot: Snapshot | None,
        questions: list[Question] | None,
        report: Report | None,
        automaton: Automaton | None,
        composed: str | None,
        card: Card | None,
    ) -> Reply:
        if self._holding:
            return self._reply_to(command, words, snapshot, questions, report)
        if command.kind in _ACT_OF:
            return self._say(self._begin(_ACT_OF[command.kind], command.text))
        if command.kind in _CONFIRMS:
            return self._say(_NOTHING_WAITING)
        if command.kind is Kind.GO_BACK:
            return self._back()
        if command.kind in _QUESTION_WORDS:
            return self._say(self._open_questions(command, questions, card))
        if self._to_set(command) or self.wanted_item_search(words) is not None:
            return self._say(self._set_item(command, words, report, card))
        if command.kind is Kind.SET_THIS:
            return self._say(_NOTHING_CHOSEN)
        if command.kind is Kind.SET_NUMBER and command.item != "project" and self._refs:
            number = command.number or 0
            found = self._line(number)
            if found is None:
                return self._say(
                    f"I haven't read a number {number}. Say more, or pick one you heard."
                )
            return self._say(f"Number {number} is the {found.spoken()}. Say set {number}.")
        children = self.wanted_children(words)
        if children is not None:
            return self._say(self._start_report(report))
        if self.wanted_automaton(words) is not None or command.kind is Kind.ABOUT:
            return self._about_automaton(command, report, automaton)
        wanted = self.wanted_card(words)
        if wanted is not None:
            return self._say(self._from_card(command, wanted, card))
        if self._runs_report(command, words):
            return self._say(composed if composed is not None else _UNREACHABLE)
        if self._chooses_detail(command):
            return self._detail(command)
        if command.kind is Kind.AUTOMATA:
            return self._say(_NO_PARENT)
        if command.kind is Kind.HISTORY:
            return self._say(_NO_HISTORY_TARGET)
        if command.kind in _ABOUT_AUTOMATON:
            item = self.target if command.number is None else self._line(command.number)
            if item is not None and item.kind == "session":
                return self._say(_SESSIONS_ONLY)
            if item is not None and command.kind is Kind.TASKS:
                return self._say(_NO_TASKS)
        return self._reply_to(command, words, snapshot, questions, report)

    def _state(self) -> _State:
        return _State(
            self.focus,
            self.path,
            self._listed,
            self._heard_count,
            self._choosing,
            self._questions,
            self._at,
            self._reading_questions,
            self._lines,
            self._lines_read,
            self._refs,
            self._details,
            self._under,
            self._selected,
        )

    def _restore(self, state: _State) -> None:
        self.focus, self.path = state.focus, state.path
        self._listed, self._heard_count = state.projects, state.projects_heard
        self._choosing = state.choosing
        self._questions, self._at = state.questions, state.at
        self._reading_questions = state.reading_questions
        self._lines, self._lines_read = state.lines, state.lines_read
        self._refs, self._details = state.refs, state.details
        self._under, self._selected = state.under, state.selected

    def _back(self) -> Reply:
        """Undo the last step. With none left, move the focus up one level."""
        focused = (self.focus, self.path)
        if self._trail:
            state, said = self._trail.pop()
            self._restore(state)
            self._here = said
            # "Focus cleared" is news only when it happens; the focus is said instead.
            said = "" if said == _CLEARED else said
            parts = ["Back."]
            if (self.focus, self.path) != focused and not said.startswith(self._where()):
                parts.append(self._where())
            if said:
                parts.append(said.removeprefix("Back. "))
            elif len(parts) == 1:
                parts.append(self._where())
            return self._say(" ".join(parts))
        if not self.path and self.focus is None:
            return self._say(_NOTHING_BEHIND)
        if self.path:
            self.path = self.path[:-1]
        else:
            self.focus = None
        self._selected = None
        return self._say(f"Back. {self._where()}")

    def _choose_item(self, item: Item) -> None:
        """Make item what "it" means. Asking again about the same one is not a step."""
        if self._selected is not None and _same(self._selected, item):
            return
        focused = bool(self.path) and _same(self.path[-1], item)
        self._selected = None if focused else item

    def _gone(self, item: Item) -> str:
        """Forget an item datawatch no longer has, and anything focused inside it."""
        if self._selected is not None and _same(self._selected, item):
            self._selected = None
        for index, focused in enumerate(self.path):
            if _same(focused, item):
                self.path = self.path[:index]
                return (
                    f"datawatch no longer has the {item.spoken()}, so I moved your focus "
                    f"up. {self._where()}"
                )
        return f"datawatch no longer has the {item.spoken()}."

    def _from_card(self, command: Command, item: Item, card: Card | None) -> str:
        if card is None:
            return _UNREACHABLE
        if card is GONE:
            return self._gone(item)
        self._reading_questions = False
        if command.kind is Kind.STATUS:
            more = "" if card.status == card.detail else " Say more detail for more."
            return f"{card.status}{more}"
        self._choose_item(item)
        return card.history if command.kind is Kind.HISTORY else card.detail

    def _set_item(
        self, command: Command, words: str, report: Report | None, card: Card | None
    ) -> str:
        found = self._to_set(command)
        source, under = self._refs, self._under
        search = self.wanted_item_search(words)
        if search is not None:
            if report is None:
                return _UNREACHABLE
            kind, name = search
            found = self.matching(report.refs, kind, name)
            source, under = report.refs, report.under
            if not found:
                return (
                    f"I couldn't find {'an' if kind[0] == 'a' else 'a'} {kind} matching {name}."
                    if report.refs
                    else report.summary
                )
        if len(found) > 1:
            return self._start_report(
                Report(
                    f"I found {len(found)} matches. Say set and a number.",
                    tuple(f"{n}, {i.spoken()}." for n, i in enumerate(found, start=1)),
                    tuple(found),
                    under=under,
                )
            )
        item = found[0]
        if card is None:
            return _UNREACHABLE
        if card is GONE:
            return self._gone(item)
        base: tuple[Item, ...] = ()
        if under is not None and any(_same(item, ref) for ref in source):
            above = next((n for n, i in enumerate(self.path) if _same(i, under)), None)
            base = (under,) if above is None else self.path[: above + 1]
        else:
            # Chosen again, or from outside a list: keep what is above it, if focused.
            above = next((n for n, i in enumerate(self.path) if _same(i, item)), None)
            base = self.path[:above] if above is not None else ()
        self.path = (*base, item)
        # An automation can span projects, so it leaves the project focus alone.
        if item.kind != "automation":
            self.focus = card.project or None
        self._selected, self._choosing, self._reading_questions = None, False, False
        return self._where()

    def _open_questions(
        self, command: Command, questions: list[Question] | None, card: Card | None
    ) -> str:
        if command.number is not None and self._line(command.number) is None:
            return f"I haven't read a number {command.number}. Say more, or pick one you heard."
        if questions is None:
            return _UNREACHABLE
        scope = self._question_scope(command)
        if scope is None and command.kind is Kind.ITS_QUESTIONS:
            return _NO_QUESTION_TARGET
        found, prefix = list(questions), ""
        if scope is not None:
            automata_in_it: frozenset[str] = frozenset()
            if scope.kind in _HOLDERS:
                if card is None:
                    return _UNREACHABLE
                if card is GONE:
                    return self._gone(scope)
                automata_in_it = card.automata
            found = [
                q
                for q in questions
                if items.linked(
                    scope, automata_in_it, q.automaton_id, q.task_id, q.asked_by, q.tags
                )
            ]
            if not found:
                everywhere = speech.count(len(questions), "open question", "open questions")
                return (
                    f"datawatch links no open questions to the {scope.spoken()}. There "
                    f"{'is' if len(questions) == 1 else 'are'} {everywhere} in all. "
                    "Say all questions."
                )
            prefix = f"For the {scope.spoken()}. "
        self._lines, self._refs, self._details, self._under = None, (), (), None
        self._questions, self._at = ordered(found), 0
        self._reading_questions = bool(self._questions)
        if not self._questions:
            return "There are no open questions."
        return prefix + self._read_current()

    def _close(self, text: str) -> Reply:
        if self._draft is not None:
            self._draft = None
            text = f"{_NOT_SENT} {text}"
        if self._pending is not None:
            text = f"{actions.not_sent(self._pending.target.act)} {text}"
            self._pending = None
        self._wording = None
        return Reply(text, ends=True)

    def _reply_to(
        self,
        command: Command,
        words: str,
        snapshot: Snapshot | None,
        questions: list[Question] | None,
        report: Report | None,
    ) -> Reply:
        if command.kind is Kind.EXIT:
            return self._close(_CLOSING)
        if command.kind is Kind.REPEAT:
            return Reply(self._last)
        if self._dictating:
            return self._dictated(command, words)
        if self._draft is not None:
            return self._confirming(self._draft, command)
        if self._wording is not None:
            return self._worded(self._wording, command, words)
        if self._pending is not None:
            return self._confirming_action(self._pending, command)
        if command.kind is Kind.REPORTS:
            return self._say(custom.listing(self._reports))
        if command.kind is Kind.ORDER:
            return self._say(order_words.current(self.order))
        if command.kind in _ORDERS:
            self.order = _ORDERS[command.kind]
            return replace(self._say(order_words.changed(self.order)), order=self.order)
        if command.kind is Kind.UNKNOWN and self._assistant:
            return Reply("", forward=words)
        if command.kind in _TOPICS:
            return self._say(self._start_report(report))
        if command.kind in _ABOUT_AUTOMATON or command.kind is Kind.PICK:
            return self._say(_NO_AUTOMATON)
        if command.kind is Kind.MORE and self._lines is not None and not self._reading_questions:
            return self._say(self._next_lines())
        asked = self._about_questions(command)
        if asked is not None:
            return self._say(asked)

        if snapshot is None and command.kind in _NEEDS_DATA:
            return self._say(_UNREACHABLE)

        notice = ""
        if snapshot is not None and self.focus and self.focus not in snapshot.projects:
            notice = f"Project {self.focus} no longer exists, so the focus is cleared. "
            self.focus, self.path = None, ()
        if command.kind in (Kind.STATUS, Kind.LIST_PROJECTS, Kind.SET_NAME):
            self._reading_questions = False
            self._lines, self._refs, self._details, self._under = None, (), (), None
            self._selected = None
        return self._say(notice + self._answer(command, snapshot or Snapshot()))

    def _say(self, text: str) -> Reply:
        self._last = text
        return Reply(text)

    def _runs_report(self, command: Command, words: str) -> bool:
        """Whether words name one of the user's reports. Never while an answer waits."""
        if self._holding or command.kind is not Kind.UNKNOWN:
            return False
        return self.wanted_report(words) is not None

    def _chooses_detail(self, command: Command) -> bool:
        """Whether command picks a line that carries its own details, such as a session."""
        if not self._details:
            return False
        return self._picks(command) or (
            command.kind in _ABOUT_AUTOMATON and command.number is not None
        )

    def _detail(self, command: Command) -> Reply:
        number = command.number or 0
        if not 1 <= number <= min(self._lines_read, len(self._details)):
            return self._say(f"I haven't read a number {number}. Say more, or pick one you heard.")
        item = self._line(number)
        if command.kind in _ABOUT_AUTOMATON:
            return self._say(_SESSIONS_ONLY)
        self._selected = item
        return self._say(self._details[number - 1])

    def _about_automaton(
        self, command: Command, report: Report | None, automaton: Automaton | None
    ) -> Reply:
        if automaton is None:
            if command.kind is Kind.ABOUT and report is not None:
                return self._say(self._start_report(report))
            return self._say(_UNREACHABLE)
        self._choose_item(Item("automaton", automaton.id, automaton.title))
        self._reading_questions = False
        if command.kind is Kind.WHY:
            return self._say(automata.why(automaton))
        if command.kind is Kind.PROGRESS:
            return self._say(automata.progress(automaton))
        if command.kind is Kind.RESULTS:
            return self._say(automata.results(automaton))
        if command.kind is Kind.TASKS:
            # The task lines replace the list, so its numbers no longer choose.
            return self._say(self._start_report(automata.tasks(automaton)))
        return self._say(automata.summary(automaton))

    def _start_report(self, report: Report | None) -> str:
        if report is None:
            return _UNREACHABLE
        self._reading_questions = False
        self._lines, self._lines_read = report.items or None, 0
        self._refs, self._details = report.refs, report.details
        # A list from inside an item leaves that item chosen.
        self._under = self._selected = report.under
        if not report.items:
            return report.summary
        return f"{report.summary} {self._next_lines()}"

    def _next_lines(self) -> str:
        assert self._lines is not None
        page = self._lines[self._lines_read : self._lines_read + PAGE_SIZE]
        if not page:
            return "That is the end of the list."
        self._lines_read += len(page)
        more = " Say more." if self._lines_read < len(self._lines) else " That is all."
        return " ".join(page) + more

    def _about_questions(self, command: Command) -> str | None:
        """The reply to a command about the question being read, or None for any other."""
        current = self.current_question
        match command.kind:
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
        if command.kind in (Kind.CANCEL, Kind.GO_BACK):
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
            case Kind.CANCEL | Kind.GO_BACK:
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

    def _begin(self, act: Act, words: str | None) -> str:
        """Start an action. Where it goes is settled before any words are asked for."""
        session = self.target if self.target and self.target.kind == "session" else None
        problem = None
        if act is Act.SESSION and not self._session_send:
            problem = actions.SESSION_SEND_OFF
        elif act is Act.SESSION and session is None:
            problem = actions.NEEDS_SESSION
        elif act is not Act.SESSION and self.focus is None:
            problem = actions.NEEDS_PROJECT
        if problem is not None:
            return f"{problem} I did not keep your words." if words else problem
        target = (
            Target(act, session=session)
            if act is Act.SESSION
            else Target(act, project=self.focus or "")
        )
        if words is None:
            self._wording = target
            return actions.ask(act)
        return self._pend(Action(target, words))

    def _pend(self, action: Action) -> str:
        self._wording, self._pending = None, action
        return actions.read_back(action)

    def _worded(self, target: Target, command: Command, words: str) -> Reply:
        """The whole turn is the words for the action, unless it cancels."""
        if command.kind in (Kind.CANCEL, Kind.GO_BACK):
            self._wording = None
            return self._say(actions.CANCELLED)
        return self._say(self._pend(Action(target, words.strip())))

    def _confirming_action(self, action: Action, command: Command) -> Reply:
        """An action is waiting: only its own confirming words send it."""
        act = action.target.act
        if _CONFIRMS.get(command.kind) is act:
            self._pending = None
            return Reply("", act=action)
        if command.kind in (Kind.CANCEL, Kind.GO_BACK):
            self._pending = None
            return self._say(actions.CANCELLED)
        if _ACT_OF.get(command.kind) is act:
            # Saying it again replaces the words, for the same place.
            if command.text is None:
                self._pending, self._wording = None, action.target
                return self._say(actions.ask(act))
            return self._say(self._pend(Action(action.target, command.text)))
        return Reply(actions.waiting(act))

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
                return self._where()
            case Kind.UNSET:
                self.focus, self.path, self._selected = None, (), None
                self._choosing = False
                return _CLEARED
            case Kind.HELP:
                return _HELP
            case _:
                return _NOT_UNDERSTOOD

    def _start_list(self, snapshot: Snapshot) -> str:
        if not snapshot.projects:
            self._listed = None
            return "There are no projects."
        self._listed, self._heard_count, self._choosing = alphabetical(snapshot.projects), 0, False
        total = speech.count(len(self._listed), "project", "projects")
        return f"{total}. {self._next_page()}"

    def _next_page(self) -> str:
        if self._listed is None:
            return _NO_LIST
        start = self._heard_count
        page = self._listed[start : start + PAGE_SIZE]
        if not page:
            return "That is the end of the list."
        self._heard_count += len(page)
        text = " ".join(f"{start + i}, {name}." for i, name in enumerate(page, start=1))
        more = self._heard_count < len(self._listed)
        if self._choosing:
            return f"{text} Say more, or which number?" if more else f"{text} Which number?"
        if more:
            return f"{text} Say more, or set and a number or name."
        return f"{text} That is the end of the list."

    def _set_number(self, number: int) -> str:
        if self._listed is None:
            return _NO_LIST
        if not 1 <= number <= self._heard_count:
            return f"I haven't read a number {number}. Say more, or pick a number you heard."
        return self._set(self._listed[number - 1])

    def _set_name(self, spoken: str, snapshot: Snapshot) -> str:
        matches = match_names(spoken, alphabetical(snapshot.projects))
        if not matches:
            return f"I couldn't find a project matching {spoken}. Say list projects."
        if len(matches) == 1:
            return self._set(matches[0])
        self._listed, self._heard_count, self._choosing = matches, 0, True
        return f"I found {len(matches)} matches. {self._next_page()}"

    def _set(self, project: str) -> str:
        self.focus, self.path, self._selected = project, (), None
        self._choosing = False
        return self._where()
