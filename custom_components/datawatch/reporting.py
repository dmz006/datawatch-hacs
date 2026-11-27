"""Read what a report needs and word it. Used by voice commands and by the AI tools."""

from __future__ import annotations

import asyncio
from dataclasses import replace

from homeassistant.util import dt as dt_util

from .api import DatawatchClient
from .voice import automata, custom, reports, speech, work
from .voice.automata import Automaton
from .voice.conversation import Topic
from .voice.custom import CustomReport
from .voice.items import Item
from .voice.names import match_names
from .voice.order import Order
from .voice.reports import Overview, Report


async def _overviews(client: DatawatchClient, projects: tuple[str, ...]) -> list[Overview]:
    ordered = sorted(projects, key=str.casefold)
    return list(await asyncio.gather(*(client.overview(name) for name in ordered)))


# The session states, waiting first.
_STATES = ("waiting_input", "running", "failed")
_ONE_STATE = {
    Topic.WAITING: "waiting_input",
    Topic.RUNNING_SESSIONS: "running",
    Topic.FAILED_SESSIONS: "failed",
}


async def _sessions(
    client: DatawatchClient,
    topic: Topic,
    project: str | None,
    inside: Item | None,
    order: Order,
) -> Report:
    """One state's sessions, or counts of all states and then the waiting ones."""
    states = (_ONE_STATE[topic],) if topic in _ONE_STATE else _STATES
    within = (inside.kind, inside.id) if inside is not None else None
    found = await asyncio.gather(
        *(client.sessions(state, None if inside else project, within) for state in states)
    )
    totals = [(state, total) for state, (_, total) in zip(states, found, strict=True)]
    return work.sessions(totals, found[0][0], project, dt_util.now(), inside, order)


async def build(
    client: DatawatchClient,
    topic: Topic,
    project: str | None,
    inside: Item | None = None,
    order: Order = Order.NAME,
) -> Report:
    """A report on topic, for one project or for all. project must be a registered one.

    inside: a focused automaton or automation, which only sessions can be filtered to, or
    for alerts a focused session. order: how sessions, automations and running work are listed.
    """
    match topic:
        case Topic.ALERTS:
            found, unread = await client.alerts()
            return work.alerts(found, unread, inside, dt_util.now())
        case Topic.ATTENTION:
            return reports.attention(await client.attention())
        case Topic.RUNNING:
            rows, total = await client.running(project)
            return reports.running(rows, total, project, order)
        case Topic.SESSIONS | Topic.WAITING | Topic.RUNNING_SESSIONS | Topic.FAILED_SESSIONS:
            return await _sessions(client, topic, project, inside, order)
        case Topic.FINISHED:
            done, how_many = await client.finished(project)
            return work.finished(done, how_many, project)
        case Topic.HELD:
            held, total = await client.held_items()
            return reports.held(held, total)
        case Topic.AUTOMATIONS:
            return reports.automations(await client.automations(project), project, order)
        case Topic.PLANS if project is not None:
            overview, plans = await asyncio.gather(client.overview(project), client.plans(project))
            return reports.plans_of(project, plans, overview.plans, overview.archived)
        case Topic.PLANS:
            return reports.plans_everywhere(await _overviews(client, await client.project_names()))
        case Topic.OVERVIEW if project is not None:
            return reports.overview(await client.overview(project))
        case Topic.OVERVIEW:
            return Report("Set a project first: say list projects, or set and a project name.")
        case Topic.NEXT if project is not None:
            return reports.next_in(await client.overview(project))
        case Topic.NEXT:
            return reports.next_everywhere(await _overviews(client, await client.project_names()))


async def read_automaton(client: DatawatchClient, automaton_id: str) -> Automaton:
    """One automaton, with why it is on hold if it is."""
    (held, _), delivered = await asyncio.gather(client.held_items(), client.delivery(automaton_id))
    reason = next((item.reason for item in held if item.id == automaton_id), "")
    return replace(await client.automaton(automaton_id, reason), delivered=delivered)


def _matching(spoken: str, titles: dict[str, str]) -> list[tuple[str, str]]:
    names = set(match_names(spoken, list(titles.values())))
    return [(ident, title) for ident, title in titles.items() if title in names]


async def find(client: DatawatchClient, spoken: str) -> tuple[Automaton | None, Report]:
    """Search by name among automata needing attention, running or on hold, then among the
    most recently completed ones.

    datawatch has no title search, and listing every automaton is too slow for voice.
    Returns the automaton when exactly one fits, and a report to say otherwise.
    """
    attention, (running, _), (held, _) = await asyncio.gather(
        client.attention(), client.running(), client.held_items()
    )
    pairs = [(a.id, a.title) for a in attention]
    pairs += [(r.id, r.title) for r in running]
    pairs += [(h.id, h.title) for h in held]
    titles: dict[str, str] = {}
    for ident, title in pairs:
        titles.setdefault(ident, title)
    found = _matching(spoken, titles)
    if not found:
        done, _ = await client.finished()
        found = _matching(spoken, {row.id: row.title for row in done})
    if len(found) == 1:
        return await read_automaton(client, found[0][0]), Report("")
    if not found:
        return None, Report(
            f"I couldn't find {spoken} among the automata that need attention, are running, "
            "are on hold or finished recently."
        )
    return None, automata.choices(spoken, found)


# Report contents that are one of datawatch mode's own reports.
_ITEM_TOPICS = {
    "attention": Topic.ATTENTION,
    "next": Topic.NEXT,
    "plans": Topic.PLANS,
    "running": Topic.RUNNING,
    "held": Topic.HELD,
    "sessions": Topic.SESSIONS,
    "automations": Topic.AUTOMATIONS,
}
# Items whose lines are short enough, and needed, to read in a combined report.
_WITH_LINES = ("next",)


async def run(client: DatawatchClient, report: CustomReport, project: str | None) -> str:
    """One of the user's reports: a short sentence or two for each thing in it."""
    parts: dict[str, str] = {}
    if {"status", "detail", "questions"} & set(report.items):
        snapshot = await client.snapshot(project)
        project = snapshot.focus
        if "status" in report.items:
            parts["status"] = speech.status(snapshot, project).removesuffix(
                " Say more detail for more."
            )
        if "detail" in report.items:
            parts["detail"] = speech.detail(snapshot, project)
        if "questions" in report.items:
            total = speech.count(snapshot.questions.total, "open question", "open questions")
            parts["questions"] = f"{total}, across all projects."
    wanted = [item for item in report.items if item in _ITEM_TOPICS]
    built = await asyncio.gather(*(build(client, _ITEM_TOPICS[i], project) for i in wanted))
    for item, result in zip(wanted, built, strict=True):
        # The hint about numbers only makes sense when the list follows.
        text = result.summary.replace(" For a full reason say why and its number.", "")
        if item in _WITH_LINES:
            text = " ".join((text, *result.items[:3]))
        parts[item] = text
    return custom.compose(report.name, parts, report.items)
