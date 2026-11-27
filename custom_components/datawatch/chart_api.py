"""What the dashboard cards ask Home Assistant for, over its own signed-in connection.

Both only read. Any signed-in Home Assistant user can ask, as with any card's data.
"""

from __future__ import annotations

import logging
from collections import Counter
from typing import Any

import probatio
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.util import dt as dt_util
from homeassistant.util.hass_dict import HassKey

from . import charts
from .api import DatawatchClient, DatawatchError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
_REGISTERED: HassKey[bool] = HassKey(f"{DOMAIN}_chart_api")
_DEFAULT_DAYS = 30


def _client(hass: HomeAssistant) -> DatawatchClient | None:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    return entries[0].runtime_data if entries else None


async def read_gantt(client: DatawatchClient, project: str | None, days: int) -> dict[str, Any]:
    """The Gantt of a registered project. Without one, the project with the most automations."""
    names = sorted(await client.project_names(), key=str.casefold)
    if not names:
        return {"projects": [], "project": None}
    automations = await client.automation_records()
    if project not in names:
        held = Counter(str(row.get("project") or "") for row in automations)
        project = max(names, key=lambda name: held[name])
    timeline = await client.project_timeline(project)
    chart = charts.gantt(timeline, automations, dt_util.utcnow(), days)
    return {"projects": names, "project": project, **chart}


@websocket_api.websocket_command(
    {
        probatio.Required("type"): f"{DOMAIN}/gantt",
        probatio.Optional("project"): str,
        probatio.Optional("days", default=_DEFAULT_DAYS): probatio.In(charts.RANGES),
    }
)
@websocket_api.async_response
async def _gantt(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    client = _client(hass)
    if client is None:
        connection.send_error(msg["id"], "not_loaded", "datawatch is not set up")
        return
    try:
        result = await read_gantt(client, msg.get("project"), msg["days"])
    except DatawatchError:
        _LOGGER.warning("The Gantt could not be read from datawatch", exc_info=True)
        connection.send_error(msg["id"], "unreachable", "datawatch cannot be read")
        return
    connection.send_result(msg["id"], result)


@websocket_api.websocket_command({probatio.Required("type"): f"{DOMAIN}/lanes"})
@websocket_api.async_response
async def _lanes(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    client = _client(hass)
    if client is None:
        connection.send_error(msg["id"], "not_loaded", "datawatch is not set up")
        return
    try:
        result = charts.lanes(await client.lane_activity(), dt_util.utcnow())
    except DatawatchError:
        _LOGGER.warning("Lane activity could not be read from datawatch", exc_info=True)
        connection.send_error(msg["id"], "unreachable", "datawatch cannot be read")
        return
    connection.send_result(msg["id"], result)


@callback
def async_register_chart_api(hass: HomeAssistant) -> None:
    """Offer the two commands. They stay until Home Assistant restarts."""
    if _REGISTERED in hass.data:
        return
    websocket_api.async_register_command(hass, _gantt)
    websocket_api.async_register_command(hass, _lanes)
    hass.data[_REGISTERED] = True
