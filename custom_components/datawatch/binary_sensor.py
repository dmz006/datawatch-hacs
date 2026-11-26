"""Whether datawatch has paused new work."""

from __future__ import annotations

from typing import override

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import COUNTS
from .entity import DatawatchEntity

PAUSED = BinarySensorEntityDescription(key="new_work_paused", translation_key="new_work_paused")


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    """Add the paused sensor."""
    async_add_entities([DatawatchPaused(hass.data[COUNTS], entry.entry_id, PAUSED)])


class DatawatchPaused(DatawatchEntity, BinarySensorEntity):
    """On while new work is paused."""

    @property
    @override
    def is_on(self) -> bool | None:
        data = self.coordinator.data
        return None if data is None else data.snapshot.paused
