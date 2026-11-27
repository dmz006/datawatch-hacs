"""The datawatch integration: hands-free datawatch by voice."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN, CONF_URL, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DatawatchClient
from .chart_api import async_register_chart_api
from .const import CONF_FINGERPRINT, COUNTS, DASHBOARD, DISCUSSING, DOMAIN, FOCUS
from .coordinator import CountsCoordinator
from .dashboard import DashboardCoordinator
from .entry_phrase import async_listen
from .frontend import async_offer_cards, withdraw_cards
from .mode import DatawatchMode, SharedFocus

_LOGGER = logging.getLogger(__name__)
_PHRASE_ISSUE = "voice_phrase_unavailable"
# 0.10.0's live-work sensor: the cards now ask for their data themselves.
_RETIRED_SENSORS = ("data_live_work",)
_PLATFORMS = (Platform.BINARY_SENSOR, Platform.SENSOR)

type DatawatchConfigEntry = ConfigEntry[DatawatchClient]


async def async_setup_entry(hass: HomeAssistant, entry: DatawatchConfigEntry) -> bool:
    """Prepare the client and listen for the entry phrase.

    datawatch does not need to be reachable now, so that voice can say when it is not.
    """
    entry.runtime_data = DatawatchClient(
        async_get_clientsession(hass),
        entry.data[CONF_URL],
        entry.data[CONF_FINGERPRINT],
        entry.data.get(CONF_TOKEN),
    )
    focus = SharedFocus(hass)
    await focus.async_load()
    hass.data[FOCUS] = focus
    hass.data[DISCUSSING] = None
    mode = DatawatchMode(hass, entry, focus)
    try:
        entry.async_on_unload(async_listen(hass, mode.async_entry_phrase))
    except Exception:
        # Relies on Home Assistant internals: any failure must be visible, not silent.
        _LOGGER.exception("Could not register the datawatch voice phrase")
        ir.async_create_issue(
            hass,
            DOMAIN,
            _PHRASE_ISSUE,
            is_fixable=False,
            severity=ir.IssueSeverity.ERROR,
            translation_key=_PHRASE_ISSUE,
        )
    else:
        ir.async_delete_issue(hass, DOMAIN, _PHRASE_ISSUE)

    async_register_chart_api(hass)
    await async_offer_cards(hass)
    _remove_retired_sensors(hass, entry)
    counts = CountsCoordinator(hass, entry, entry.runtime_data)
    hass.data[COUNTS] = counts
    dashboard = DashboardCoordinator(hass, entry, entry.runtime_data)
    hass.data[DASHBOARD] = dashboard
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)
    # Not awaited: setting up must not wait for datawatch, or fail without it.
    entry.async_create_background_task(hass, counts.async_refresh(), f"{DOMAIN} first read")
    entry.async_create_background_task(
        hass, dashboard.async_refresh(), f"{DOMAIN} first dashboard read"
    )
    return True


@callback
def _remove_retired_sensors(hass: HomeAssistant, entry: DatawatchConfigEntry) -> None:
    """Take away sensors an earlier version made and this one no longer has."""
    registry = er.async_get(hass)
    for key in _RETIRED_SENSORS:
        found = registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_{key}")
        if found:
            registry.async_remove(found)


async def async_unload_entry(hass: HomeAssistant, entry: DatawatchConfigEntry) -> bool:
    """Remove the sensors. Home Assistant removes the phrase and stops any visit."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: DatawatchConfigEntry) -> None:
    """Leave nothing behind."""
    withdraw_cards(hass)
    ir.async_delete_issue(hass, DOMAIN, _PHRASE_ISSUE)
    await SharedFocus(hass).async_remove()
