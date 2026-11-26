"""Constants for the datawatch integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.util.hass_dict import HassKey

if TYPE_CHECKING:
    from .coordinator import CountsCoordinator
    from .mode import SharedFocus

DOMAIN = "datawatch"
CONF_FINGERPRINT = "fingerprint"
# The AI assistant that may use datawatch. Not set means AI is off.
CONF_ASSISTANT = "assistant"
# The id of the question being discussed in datawatch mode, if any.
DISCUSSING: HassKey[str | None] = HassKey(f"{DOMAIN}_discussing")
# The project focus, shared by voice devices and the AI tools.
FOCUS: HassKey[SharedFocus] = HassKey(f"{DOMAIN}_focus")
# What the dashboard sensors read.
COUNTS: HassKey[CountsCoordinator] = HassKey(f"{DOMAIN}_counts")
# Reports the user defines: the kind of config subentry, and its list of contents.
SUBENTRY_REPORT = "report"
CONF_ITEMS = "items"
