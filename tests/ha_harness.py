"""A throwaway Home Assistant: the real code, with an empty temporary configuration."""

from __future__ import annotations

import contextlib
from collections.abc import AsyncIterator
from pathlib import Path

from homeassistant import bootstrap, config_entries, loader
from homeassistant.auth import auth_manager_from_config
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component


@contextlib.asynccontextmanager
async def running_hass(config_dir: Path) -> AsyncIterator[HomeAssistant]:
    hass = HomeAssistant(str(config_dir))
    loader.async_setup(hass)
    hass.config.skip_pip = True
    hass.config_entries = config_entries.ConfigEntries(hass, {})
    await bootstrap.async_load_base_functionality(hass)
    # The voice components need these, as in a running Home Assistant.
    hass.auth = await auth_manager_from_config(hass, [], [])
    # A running Home Assistant always has this; its shared web session depends on it.
    assert await async_setup_component(hass, "network", {})
    try:
        yield hass
    finally:
        await hass.async_stop(force=True)


async def add_datawatch(hass: HomeAssistant, url: str) -> None:
    """Go through the setup screens, approving the certificate."""
    flow = hass.config_entries.flow
    result = await flow.async_init("datawatch", context={"source": "user"})
    result = await flow.async_configure(result["flow_id"], {"url": url})
    await flow.async_configure(result["flow_id"], {})
    await hass.async_block_till_done()
