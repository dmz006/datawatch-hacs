"""The datawatch integration. In development: voice is not connected yet."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN, CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DatawatchClient
from .const import CONF_FINGERPRINT

type DatawatchConfigEntry = ConfigEntry[DatawatchClient]


async def async_setup_entry(hass: HomeAssistant, entry: DatawatchConfigEntry) -> bool:
    """Prepare the client. datawatch does not need to be reachable at this point."""
    entry.runtime_data = DatawatchClient(
        async_get_clientsession(hass),
        entry.data[CONF_URL],
        entry.data[CONF_FINGERPRINT],
        entry.data.get(CONF_TOKEN),
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DatawatchConfigEntry) -> bool:
    """Nothing is running yet, so there is nothing to stop."""
    return True
