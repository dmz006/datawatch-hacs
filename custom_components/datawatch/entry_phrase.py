"""Hear "open datawatch".

This is the only place the integration relies on Home Assistant code that is not a public
interface: the function Home Assistant's own sentence automations use to register a spoken
phrase. If a Home Assistant upgrade changes it, the change belongs here.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from homeassistant.core import CALLBACK_TYPE, HomeAssistant

from .voice.language import LANGUAGES

# Every language's ways of opening datawatch mode, so that any of them works.
SENTENCES = list(
    dict.fromkeys(
        sentence for found in LANGUAGES.values() for sentence in found.grammar.entry_sentences
    )
)


def async_listen(
    hass: HomeAssistant, heard: Callable[[str | None, str | None], Awaitable[str]]
) -> CALLBACK_TYPE:
    """Call heard(voice device entity id or None, the language it was heard in) when an
    entry phrase is said.
    """
    # Imported here so that a change in Home Assistant is a caught error, not a failed load.
    from homeassistant.components.conversation.agent_manager import get_agent_manager

    async def on_match(user_input: Any, result: Any) -> str:
        return await heard(user_input.satellite_id, user_input.language)

    return get_agent_manager(hass).register_trigger(SENTENCES, on_match)
