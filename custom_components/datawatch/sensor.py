"""datawatch counts, for dashboards and automations."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import override

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import COUNTS
from .coordinator import Counts
from .entity import DatawatchEntity


@dataclass(frozen=True, kw_only=True)
class DatawatchSensorDescription(SensorEntityDescription):
    """A count and where it comes from."""

    value: Callable[[Counts], int]


def _count(key: str, value: Callable[[Counts], int]) -> DatawatchSensorDescription:
    return DatawatchSensorDescription(
        key=key, translation_key=key, state_class=SensorStateClass.MEASUREMENT, value=value
    )


SENSORS = (
    _count("open_questions", lambda c: c.snapshot.questions.total),
    _count("needs_attention", lambda c: c.attention),
    _count("sessions_waiting", lambda c: c.snapshot.waiting.total),
    _count("sessions_running", lambda c: c.snapshot.running.total),
    _count("sessions_failed", lambda c: c.snapshot.failed.total),
    _count("automata_stuck", lambda c: c.snapshot.stuck.total),
    _count("held_items", lambda c: c.snapshot.held.total),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    """Add the count sensors."""
    coordinator = hass.data[COUNTS]
    async_add_entities(
        DatawatchSensor(coordinator, entry.entry_id, description) for description in SENSORS
    )


class DatawatchSensor(DatawatchEntity, SensorEntity):
    """A count."""

    entity_description: DatawatchSensorDescription

    @property
    @override
    def native_value(self) -> int | None:
        data = self.coordinator.data
        return None if data is None else self.entity_description.value(data)
