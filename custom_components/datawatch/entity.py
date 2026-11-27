"""What datawatch's sensors share."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import CountsCoordinator


def device(entry_id: str) -> DeviceInfo:
    """The one device every datawatch sensor belongs to."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)}, name="datawatch", entry_type=DeviceEntryType.SERVICE
    )


class DatawatchEntity(CoordinatorEntity[CountsCoordinator]):
    """One count from datawatch."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: CountsCoordinator, entry_id: str, description: EntityDescription
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_device_info = device(entry_id)
