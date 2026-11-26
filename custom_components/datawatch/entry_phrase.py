"""Hear "open datawatch".

This is the only place the integration relies on Home Assistant code that is not a public
interface: the function Home Assistant's own sentence automations use to register a spoken
phrase. If a Home Assistant upgrade changes it, the change belongs here.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from homeassistant.core import CALLBACK_TYPE, HomeAssistant

# Speech-to-text may write the name as two words.
SENTENCES = ["(open|use) (datawatch|data watch)", "(datawatch|data watch)"]


def async_listen(
    hass: HomeAssistant, heard: Callable[[str | None], Awaitable[str]]
) -> CALLBACK_TYPE:
    """Call heard(voice device entity id, or None) when an entry phrase is said."""
    # Imported here so that a change in Home Assistant is a caught error, not a failed load.
    from homeassistant.components.conversation.agent_manager import get_agent_manager

    async def on_match(user_input: Any, result: Any) -> str:
        return await heard(user_input.satellite_id)

    return get_agent_manager(hass).register_trigger(SENTENCES, on_match)
