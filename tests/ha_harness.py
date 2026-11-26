"""A throwaway Home Assistant: the real code, with an empty temporary configuration."""

from __future__ import annotations

import contextlib
from collections.abc import AsyncIterator
from pathlib import Path

from homeassistant import bootstrap, config_entries, loader
from homeassistant.core import HomeAssistant


@contextlib.asynccontextmanager
async def running_hass(config_dir: Path) -> AsyncIterator[HomeAssistant]:
    hass = HomeAssistant(str(config_dir))
    loader.async_setup(hass)
    hass.config.skip_pip = True
    hass.config_entries = config_entries.ConfigEntries(hass, {})
    await bootstrap.async_load_base_functionality(hass)
    try:
        yield hass
    finally:
        await hass.async_stop(force=True)
