"""Read one item, or what is inside it, fresh from datawatch."""

from __future__ import annotations

import asyncio
from dataclasses import replace

from homeassistant.util import dt as dt_util

from .api import DatawatchClient, DatawatchMissingError
from .reporting import build, find, read_automaton
from .voice import actions, automata, items, reports, work
from .voice.automata import Automaton
from .voice.conversation import Topic
from .voice.items import GONE, Card, Item
from .voice.language import N_, t, tn
from .voice.reports import Child, Report, words

# The most automata or tasks read from inside a plan or an automation.
CHILD_LIMIT = 50
# The most missing titles looked up for one list.
TITLE_READS = 20
_TASK_HISTORY = N_(
    "datawatch records history for an automaton, not for one task. Choose its automaton to hear it."
)
_NO_PLAN_HISTORY = N_("datawatch gives no history for a plan.")
_NO_SESSION_HISTORY = N_("I can't read a session's history by voice. Open it in datawatch.")


def _goal(label: str, text: str) -> str:
    return f" {t(label)}: {items.shorten(text, 400)}" if text.strip() else ""


def _automaton_card(found: Automaton) -> Card:
    title = items.clean(found.title)
    first = t("Automaton {title}: {state}.", title=title, state=words(found.status))
    status = f"{first} {automata.progress(found)}"
    project = f" {t('Project {project}.', project=found.project)}" if found.project else ""
    ended = found.status in ("completed", "archived")
    lead = status if ended else automata.why(found)
    return Card(
        status,
        f"{lead}{project}{_goal(N_('What it is for'), found.goal)}",
        items.history(found.title, found.decisions),
        found.project,
    )


def _task_card(found: Automaton, item: Item) -> Card:
    task = next((task for task in found.tasks if task.id == item.id), None)
    if task is None:
        return GONE
    text = automata.task_detail(task, found.title)
    return Card(text, text, t(_TASK_HISTORY), found.project)


async def _plan_card(client: DatawatchClient, item: Item) -> Card:
    plan = next((p for p in await client.plans(item.parent) if p.id == item.id), None)
    if plan is None:
        return GONE
    status = t("Plan {line}.", line=f"{items.clean(plan.title)}: {words(plan.state)}")
    if plan.total:
        status += " " + t("{done} of {total} automata done.", done=plan.done, total=plan.total)
    where = t("Project {project}.", project=item.parent)
    detail = f"{status} {where}{_goal(N_('Its goal'), plan.goal)}"
    if plan.next_automaton:
        following = await client.automaton_brief(plan.next_automaton)
        detail += " " + t("Next: {title}.", title=items.clean(following.title))
    return Card(status, detail, t(_NO_PLAN_HISTORY), item.parent, plan.automata)


async def _automation_card(client: DatawatchClient, item: Item) -> Card:
    found = await client.automation(item.id)
    line = f"{items.clean(found.name)}: {words(found.status)}."
    members = tn(found.members, "It has {number} member.", "It has {number} members.")
    status = f"{t('Automation {line}', line=line)} {members}"
    return Card(
        status,
        f"{status}{_goal(N_('Its description'), found.description)}",
        items.history(found.name, found.decisions),
        automata=frozenset(found.member_ids),
    )


async def _session_card(client: DatawatchClient, item: Item) -> Card:
    found = await client.session(item.id)
    if found is None:
        return GONE
    text = work.session_detail(found, dt_util.now())
    return Card(text, text, t(_NO_SESSION_HISTORY), found.project)


async def read_card(client: DatawatchClient, item: Item) -> Card:
    """The item as it is now, or GONE if datawatch no longer has it."""
    try:
        match item.kind:
            case "automaton":
                return _automaton_card(await read_automaton(client, item.id))
            case "task":
                return _task_card(await read_automaton(client, item.parent), item)
            case "plan":
                return await _plan_card(client, item)
            case "automation":
                return await _automation_card(client, item)
            case _:
                return await _session_card(client, item)
    except DatawatchMissingError:
        return GONE


async def _titled(client: DatawatchClient, rows: list[Child]) -> list[Child]:
    """rows with empty titles filled in from the automata themselves, the first few.

    datawatch's plan list leaves some titles empty that the automaton has.
    """
    blank = [row.id for row in rows if not row.title.strip()][:TITLE_READS]
    found = await asyncio.gather(*(client.automaton_brief(ident) for ident in blank))
    titles = {row.id: row.title for row in found if row.title.strip()}
    return [replace(row, title=titles[row.id]) if row.id in titles else row for row in rows]


async def read_children(client: DatawatchClient, under: Item, what: str) -> Report:
    """The automata or tasks inside a plan, or the automata of an automation."""
    if under.kind == "plan" and what == "automaton":
        rows, total = await client.plan_automata(under.id, CHILD_LIMIT)
        rows = await _titled(client, rows)
    elif under.kind == "plan":
        rows, total = await client.plan_tasks(under.id, CHILD_LIMIT)
    else:
        members = (await client.automation(under.id)).member_ids
        total = len(members)
        rows = list(
            await asyncio.gather(*(client.automaton_brief(m) for m in members[:CHILD_LIMIT]))
        )
    return reports.children(under, what, rows, total)


_SESSION_STATES = ("waiting_input", "running", "failed")
_NEEDS_HOLDER = N_("Set a plan or an automaton first, then set the task.")


async def search_items(
    client: DatawatchClient,
    kind: str,
    name: str,
    project: str | None,
    path: tuple[Item, ...],
) -> Report:
    """Where to look for a spoken name: a report whose refs can be matched against it.

    A report without refs says why there is nothing to choose from.
    """
    inside = next((i for i in reversed(path) if i.kind in ("automaton", "automation")), None)
    match kind:
        case "plan":
            if project is None:
                return Report(t(actions.NEEDS_PROJECT))
            return await build(client, Topic.PLANS, project)
        case "automation":
            return await build(client, Topic.AUTOMATIONS, project)
        case "automaton":
            found, report = await find(client, name)
            if found is None:
                return report
            return Report("", refs=(Item("automaton", found.id, found.title),))
        case "task":
            holder = next((i for i in reversed(path) if i.kind in ("plan", "automaton")), None)
            if holder is None:
                return Report(t(_NEEDS_HOLDER))
            if holder.kind == "plan":
                return await read_children(client, holder, "task")
            return automata.tasks(await read_automaton(client, holder.id))
        case _:
            within = (inside.kind, inside.id) if inside is not None else None
            found_states = await asyncio.gather(
                *(
                    client.sessions(state, None if inside else project, within)
                    for state in _SESSION_STATES
                )
            )
            refs = tuple(
                Item("session", row.id, row.name or t("unnamed"))
                for rows, _ in found_states
                for row in rows
            )
            return Report(t("There are no waiting, running or failed sessions."), refs=refs)
