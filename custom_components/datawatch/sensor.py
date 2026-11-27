"""datawatch counts and dashboard data, for dashboards and automations."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, override

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COUNTS, DASHBOARD
from .coordinator import Counts
from .dashboard import (
    DATA_SENSORS,
    LANES,
    NUMBERS,
    DashboardCoordinator,
    Number,
    details,
    lane_busy,
    lane_names,
)
from .entity import DatawatchEntity, device


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
    """Add the count sensors, and the dashboard sensors, which start disabled."""
    coordinator = hass.data[COUNTS]
    async_add_entities(
        DatawatchSensor(coordinator, entry.entry_id, description) for description in SENSORS
    )
    dashboard = hass.data[DASHBOARD]
    async_add_entities(
        DashboardDataSensor(dashboard, entry.entry_id, number) for number in DATA_SENSORS
    )
    async_add_entities(DashboardSensor(dashboard, entry.entry_id, number) for number in NUMBERS)

    # Lanes are only known from datawatch. Ones seen before come back from the registry.
    prefix = f"{entry.entry_id}_lane_busy_"
    known: set[str] = set()

    @callback
    def add_lanes(lanes: list[str]) -> None:
        new = [lane for lane in dict.fromkeys(lanes) if lane not in known]
        known.update(new)
        if new:
            async_add_entities(LaneSensor(dashboard, entry.entry_id, lane) for lane in new)

    registered = er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    add_lanes(
        [
            item.unique_id.removeprefix(prefix)
            for item in registered
            if item.unique_id.startswith(prefix)
        ]
    )

    @callback
    def look_for_lanes() -> None:
        add_lanes(lane_names((dashboard.data or {}).get(LANES)))

    entry.async_on_unload(dashboard.async_add_listener(look_for_lanes))


class DatawatchSensor(DatawatchEntity, SensorEntity):
    """A count."""

    entity_description: DatawatchSensorDescription

    @property
    @override
    def native_value(self) -> int | None:
        data = self.coordinator.data
        return None if data is None else self.entity_description.value(data)


class DashboardSensor(CoordinatorEntity[DashboardCoordinator], SensorEntity):
    """A number from datawatch's dashboard data. Off until the user enables it."""

    _attr_has_entity_name = True
    _attr_entity_registry_enabled_default = False
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: DashboardCoordinator,
        entry_id: str,
        number: Number,
        key: str | None = None,
    ) -> None:
        # The context tells the coordinator to read this data set.
        super().__init__(coordinator, context=number.dataset)
        self._number = number
        self._attr_translation_key = number.key
        self._attr_unique_id = f"{entry_id}_{key or number.key}"
        self._attr_native_unit_of_measurement = number.unit
        self._attr_device_info = device(entry_id)

    @property
    def _dataset(self) -> dict[str, Any] | None:
        return (self.coordinator.data or {}).get(self._number.dataset)

    @property
    @override
    def available(self) -> bool:
        return super().available and self._dataset is not None

    @property
    @override
    def native_value(self) -> float | None:
        data = self._dataset
        return None if data is None else self._number.value(data)


class DashboardDataSensor(DashboardSensor):
    """A headline number, with the data set behind it for cards to draw."""

    # Large and changing: never saved in history.
    _unrecorded_attributes = frozenset({"data"})

    @property
    @override
    def extra_state_attributes(self) -> dict[str, Any] | None:
        data = self._dataset
        return None if data is None else {"data": details(data)}


class LaneSensor(DashboardSensor):
    """How busy one lane was in the last full hour."""

    def __init__(self, coordinator: DashboardCoordinator, entry_id: str, lane: str) -> None:
        number = Number("lane_busy", LANES, lane_busy(lane), "%")
        super().__init__(coordinator, entry_id, number, f"lane_busy_{lane}")
        self._attr_translation_placeholders = {"lane": lane}
