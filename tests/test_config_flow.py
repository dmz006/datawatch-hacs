"""Setting up datawatch in a real (throwaway) Home Assistant against a fake datawatch."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import aiohttp
import pytest
from aiohttp import web
from fake_datawatch import Fake, serve
from ha_harness import running_hass
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.datawatch import config_flow
from custom_components.datawatch.api import DatawatchClient, DatawatchError
from custom_components.datawatch.const import DOMAIN

INTEGRATION = Path(__file__).resolve().parents[1] / "custom_components" / "datawatch"
TEXT = json.loads((INTEGRATION / "translations" / "en.json").read_text())["config"]
TOKEN = "fake-token-value"
REPLACEMENT = "fake-second-value"

Certificate = tuple[Path, Path, str]
Result = Any
Body = Callable[[HomeAssistant, str, Fake], Awaitable[None]]


def in_hass(certificate: Certificate, tmp_path: Path, body: Body, fake: Fake | None = None) -> None:
    async def inner(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        async with running_hass(tmp_path) as hass:
            await body(hass, url, fake)

    serve(certificate, inner, fake)


def translated(result: Result) -> Result:
    """Every screen, error and reason the user can see has English text."""
    if result["type"] is FlowResultType.FORM:
        step = TEXT["step"][result["step_id"]]
        for key in (result.get("errors") or {}).values():
            assert key in TEXT["error"], key
        for name in result.get("description_placeholders") or {}:
            assert "{" + name + "}" in step["description"], name
        for field in result["data_schema"].schema if result["data_schema"] else ():
            assert str(field) in step["data"], str(field)
    if result["type"] is FlowResultType.ABORT:
        assert result["reason"] in TEXT["abort"], result["reason"]
    return result


async def start(hass: HomeAssistant, **context: str) -> Result:
    context.setdefault("source", "user")
    return translated(await hass.config_entries.flow.async_init(DOMAIN, context=dict(context)))


async def submit(hass: HomeAssistant, result: Result, data: dict[str, str]) -> Result:
    done = await hass.config_entries.flow.async_configure(result["flow_id"], data)
    await hass.async_block_till_done()
    return translated(done)


async def add(hass: HomeAssistant, url: str, **extra: str) -> Result:
    certificate_step = await submit(hass, await start(hass), {"url": url, **extra})
    return await submit(hass, certificate_step, {})


def test_nothing_is_sent_until_the_certificate_is_approved(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, url: str, fake: Fake) -> None:
        result = await start(hass)
        assert (result["type"], result["step_id"]) == (FlowResultType.FORM, "user")
        result = await submit(hass, result, {"url": url + "/", "token": TOKEN})
        assert result["step_id"] == "certificate"
        assert result["description_placeholders"] == {"url": url, "fingerprint": certificate[2]}
        assert fake.seen == [], "nothing, least of all the token, before approval"
        assert hass.config_entries.async_entries(DOMAIN) == []

        result = await submit(hass, result, {})
        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["title"] == "datawatch"
        assert result["data"] == {"url": url, "fingerprint": certificate[2], "token": TOKEN}
        assert [(m, p, auth) for m, p, _, auth in fake.seen] == [
            ("GET", "/api/projects", f"Bearer {TOKEN}")
        ]

    in_hass(certificate, tmp_path, body)


def test_without_a_token_the_entry_loads_a_working_client_and_unloads(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, url: str, fake: Fake) -> None:
        result = await add(hass, url, token="  ")
        assert result["data"] == {"url": url, "fingerprint": certificate[2]}
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        assert entry.state is ConfigEntryState.LOADED
        assert isinstance(entry.runtime_data, DatawatchClient)
        assert await entry.runtime_data.project_names() == ("oak", "elm")
        assert {auth for *_, auth in fake.seen} == {None}

        assert await hass.config_entries.async_unload(entry.entry_id)
        assert entry.state.value == ConfigEntryState.NOT_LOADED.value

    in_hass(certificate, tmp_path, body)


def test_setup_does_not_need_datawatch_to_be_up(certificate: Certificate, tmp_path: Path) -> None:
    """So that voice can say it cannot reach datawatch, rather than not respond."""

    async def body(hass: HomeAssistant, url: str, fake: Fake) -> None:
        await add(hass, url)
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        fake.seen.clear()
        assert await hass.config_entries.async_reload(entry.entry_id)
        assert entry.state is ConfigEntryState.LOADED
        assert fake.seen == []

    in_hass(certificate, tmp_path, body)


def test_a_bad_address_is_explained(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, url: str, fake: Fake) -> None:
        result = await submit(hass, await start(hass), {"url": "http://datawatch.example.com"})
        assert (result["step_id"], result["errors"]) == ("user", {"base": "invalid_url"})

    in_hass(certificate, tmp_path, body)


def test_an_unreachable_server_is_explained(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, url: str, fake: Fake) -> None:
        result = await submit(hass, await start(hass), {"url": "https://127.0.0.1:1"})
        assert (result["step_id"], result["errors"]) == ("user", {"base": "cannot_connect"})

    in_hass(certificate, tmp_path, body)


@pytest.mark.parametrize(("status", "error"), [(401, "invalid_auth"), (500, "cannot_connect")])
def test_a_refused_or_failing_server_adds_nothing(
    certificate: Certificate, tmp_path: Path, status: int, error: str
) -> None:
    async def body(hass: HomeAssistant, url: str, fake: Fake) -> None:
        result = await add(hass, url, token=TOKEN)
        assert (result["step_id"], result["errors"]) == ("user", {"base": error})
        assert hass.config_entries.async_entries(DOMAIN) == []

    fake = Fake()
    fake.override["/api/projects"] = lambda: web.Response(status=status)
    in_hass(certificate, tmp_path, body, fake)


def test_a_certificate_that_changes_before_approval_is_not_accepted(
    certificate: Certificate, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def other(url: str) -> str:
        return ":".join(["00"] * 32)

    async def body(hass: HomeAssistant, url: str, fake: Fake) -> None:
        monkeypatch.setattr(config_flow, "fetch_fingerprint", other)
        result = await add(hass, url, token=TOKEN)
        assert (result["step_id"], result["errors"]) == ("user", {"base": "certificate_changed"})
        assert fake.seen == []

    in_hass(certificate, tmp_path, body)


def test_only_one_datawatch_server_for_now(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, url: str, fake: Fake) -> None:
        await add(hass, url)
        result = await start(hass)
        assert (result["type"], result["reason"]) == (
            FlowResultType.ABORT,
            "single_instance_allowed",
        )

    in_hass(certificate, tmp_path, body)


async def reconfigure(hass: HomeAssistant, data: dict[str, str]) -> Result:
    (entry,) = hass.config_entries.async_entries(DOMAIN)
    result = await start(hass, source="reconfigure", entry_id=entry.entry_id)
    assert result["step_id"] == "reconfigure"
    result = await submit(hass, result, data)
    assert result["step_id"] == "certificate", "a change is approved again"
    return await submit(hass, result, {})


def test_reconfiguring_the_same_server_keeps_the_saved_token(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, url: str, fake: Fake) -> None:
        await add(hass, url, token=TOKEN)
        result = await reconfigure(hass, {"url": url})
        assert (result["type"], result["reason"]) == (
            FlowResultType.ABORT,
            "reconfigure_successful",
        )
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        assert entry.data["token"] == TOKEN
        assert entry.state is ConfigEntryState.LOADED

    in_hass(certificate, tmp_path, body)


def test_a_saved_token_is_never_sent_to_a_different_address(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, url: str, fake: Fake) -> None:
        await add(hass, url, token=TOKEN)
        fake.seen.clear()
        moved = url.replace("127.0.0.1", "localhost")
        await reconfigure(hass, {"url": moved})
        await hass.async_block_till_done(wait_background_tasks=True)
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        assert entry.data == {"url": moved, "fingerprint": certificate[2]}
        new_address = [auth for host, auth in fake.addressed if host.startswith("localhost:")]
        assert new_address, "the new address was read"
        assert set(new_address) == {None}, "the saved token never went to the new address"

    in_hass(certificate, tmp_path, body)


def test_a_new_token_replaces_the_old_one(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, url: str, fake: Fake) -> None:
        await add(hass, url, token=TOKEN)
        await reconfigure(hass, {"url": url, "token": REPLACEMENT})
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        assert entry.data["token"] == REPLACEMENT

    in_hass(certificate, tmp_path, body)


def test_the_harness_notices_a_dead_server(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, url: str, fake: Fake) -> None:
        await add(hass, url)
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        fake.override["/api/projects"] = lambda: web.Response(status=500)
        with pytest.raises(DatawatchError):
            await entry.runtime_data.project_names()

    in_hass(certificate, tmp_path, body)
