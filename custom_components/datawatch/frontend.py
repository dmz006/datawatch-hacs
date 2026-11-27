"""Offer datawatch's own dashboard cards to Home Assistant's pages."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration
from homeassistant.util.hass_dict import HassKey

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
CARD_PATH = "/datawatch_static/datawatch-cards.js"
_FILE = Path(__file__).parent / "frontend" / "datawatch-cards.js"
# The address given to Home Assistant's pages, while it is offered.
_OFFERED: HassKey[str] = HassKey(f"{DOMAIN}_card_url")
# A file can be served from an address only once until Home Assistant restarts.
_SERVED: HassKey[bool] = HassKey(f"{DOMAIN}_card_served")


async def async_offer_cards(hass: HomeAssistant) -> None:
    """Add the cards to Home Assistant's pages. Does nothing where there are no pages."""
    if _OFFERED in hass.data or "frontend" not in hass.config.components:
        return
    # Imported here: Home Assistant without pages does not have these.
    from homeassistant.components.frontend import add_extra_js_url
    from homeassistant.components.http import StaticPathConfig

    try:
        # The version in the address makes browsers fetch a new release's cards.
        version = (await async_get_integration(hass, DOMAIN)).version
        url = f"{CARD_PATH}?v={version}"
        if _SERVED not in hass.data:
            await hass.http.async_register_static_paths(
                [StaticPathConfig(CARD_PATH, str(_FILE), False)]
            )
            hass.data[_SERVED] = True
        add_extra_js_url(hass, url)
    except Exception:
        # The cards are an extra: voice and sensors must work without them.
        _LOGGER.exception("Could not add the datawatch dashboard cards")
        return
    hass.data[_OFFERED] = url


def withdraw_cards(hass: HomeAssistant) -> None:
    """Stop adding the cards to pages loaded from now on."""
    url = hass.data.pop(_OFFERED, None)
    if url is None:
        return
    from homeassistant.components.frontend import remove_extra_js_url

    remove_extra_js_url(hass, url)
