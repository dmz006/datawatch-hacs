"""Counts for dashboard sensors, read from datawatch once a minute."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import override

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DatawatchClient, DatawatchError
from .const import DOMAIN
from .voice.model import Snapshot

_LOGGER = logging.getLogger(__name__)
INTERVAL = timedelta(seconds=60)


@dataclass(frozen=True)
class Counts:
    """What the sensors show."""

    snapshot: Snapshot
    attention: int


class CountsCoordinator(DataUpdateCoordinator[Counts]):
    """Reads the counts. A failed read makes the sensors unavailable, never zero."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: DatawatchClient) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=DOMAIN, update_interval=INTERVAL)
        self._client = client

    @override
    async def _async_update_data(self) -> Counts:
        try:
            snapshot, attention = await asyncio.gather(
                self._client.snapshot(None), self._client.attention()
            )
        except DatawatchError as error:
            raise UpdateFailed(str(error)) from error
        return Counts(snapshot, len(attention))
