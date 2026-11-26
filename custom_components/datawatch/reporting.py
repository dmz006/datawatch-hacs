"""Read what a report needs and word it. Used by voice commands and by the AI tools."""

from __future__ import annotations

import asyncio

from .api import DatawatchClient
from .voice import reports
from .voice.conversation import Topic
from .voice.reports import Overview, Report


async def _overviews(client: DatawatchClient, projects: tuple[str, ...]) -> list[Overview]:
    ordered = sorted(projects, key=str.casefold)
    return list(await asyncio.gather(*(client.overview(name) for name in ordered)))


async def build(client: DatawatchClient, topic: Topic, project: str | None) -> Report:
    """A report on topic, for one project or for all. project must be a registered one."""
    match topic:
        case Topic.ATTENTION:
            return reports.attention(await client.attention())
        case Topic.AUTOMATIONS:
            return reports.automations(await client.automations(project), project)
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
