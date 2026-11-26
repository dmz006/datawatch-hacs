"""The datawatch integration: hands-free datawatch by voice."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN, CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DatawatchClient
from .const import CONF_FINGERPRINT, DISCUSSING, DOMAIN, FOCUS
from .entry_phrase import async_listen
from .mode import DatawatchMode, SharedFocus

_LOGGER = logging.getLogger(__name__)
_PHRASE_ISSUE = "voice_phrase_unavailable"

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
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DatawatchConfigEntry) -> bool:
    """Home Assistant removes the phrase and stops any visit in progress."""
    return True


async def async_remove_entry(hass: HomeAssistant, entry: DatawatchConfigEntry) -> None:
    """Leave nothing behind."""
    ir.async_delete_issue(hass, DOMAIN, _PHRASE_ISSUE)
    await SharedFocus(hass).async_remove()
