"""The read-only datawatch client, against a fake server with a throwaway certificate.

Everything here is made up. Nothing talks to a real datawatch.
"""

from __future__ import annotations

import asyncio
import ssl
import subprocess
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import aiohttp
import pytest
from aiohttp import web

from custom_components.datawatch.api import (
    DatawatchAuthError,
    DatawatchCertificateError,
    DatawatchClient,
    DatawatchError,
    fetch_fingerprint,
    parse_fingerprint,
    parse_server_url,
)
from custom_components.datawatch.voice.model import Snapshot, Tally


def make_certificate(folder: Path, name: str) -> tuple[Path, Path, str]:
    cert, key = folder / f"{name}.crt", folder / f"{name}.pem-key"
    subprocess.run(
        ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "2",
         "-subj", "/CN=fake-datawatch", "-keyout", str(key), "-out", str(cert)],
        check=True, capture_output=True,
    )  # fmt: skip
    printed = subprocess.run(
        ["openssl", "x509", "-in", str(cert), "-noout", "-fingerprint", "-sha256"],
        check=True, capture_output=True, text=True,
    ).stdout  # fmt: skip
    return cert, key, printed.strip().split("=", 1)[1]


@pytest.fixture(scope="module")
def certificate(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path, str]:
    return make_certificate(tmp_path_factory.mktemp("tls"), "server")


class Fake:
    """Answers like datawatch for the reads the client makes, and records them."""

    def __init__(self) -> None:
        self.seen: list[tuple[str, str, dict[str, str], str | None]] = []
        self.override: dict[str, web.Response | Callable[[], web.Response]] = {}
        self.questions = 4
        self.totals = {"waiting_input": (3, 1), "running": (2, 0), "failed": (5, 4)}

    async def handle(self, request: web.Request) -> web.StreamResponse:
        query = dict(request.query)
        self.seen.append(
            (request.method, request.path, query, request.headers.get("Authorization"))
        )
        if request.path in self.override:
            answer = self.override[request.path]
            return answer() if callable(answer) else answer
        if request.path == "/api/projects":
            return web.json_response([{"name": "oak", "dir": "x"}, {"name": "elm"}])
        if request.path == "/api/pause":
            return web.json_response({"paused": True, "global": {}})
        if request.path == "/api/questions":
            rows = [{"id": str(n)} for n in range(self.questions)]
            return web.json_response({"count": len(rows), "questions": rows})
        if request.path == "/api/autonomous/held":
            return web.json_response({"held": [], "total": 7, "expired": 0})
        if request.path == "/api/sessions":
            everything, inside = self.totals[query["status"]]
            total = inside if "project" in query else everything
            return web.json_response({"sessions": [], "total": total})
        return web.Response(status=404)


Body = Callable[[str, aiohttp.ClientSession, Fake], Awaitable[Any]]


def serve(certificate: tuple[Path, Path, str], body: Body, fake: Fake | None = None) -> Any:
    fake = fake or Fake()

    async def run() -> Any:
        app = web.Application()
        app.router.add_route("*", "/{tail:.*}", fake.handle)
        runner = web.AppRunner(app)
        await runner.setup()
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certificate[0], certificate[1])
        site = web.TCPSite(runner, "127.0.0.1", 0, ssl_context=context)
        await site.start()
        port = runner.addresses[0][1]
        try:
            async with aiohttp.ClientSession() as session:
                return await body(f"https://127.0.0.1:{port}", session, fake)
        finally:
            await runner.cleanup()

    return asyncio.run(run())


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("https://datawatch.example.com:8443", "https://datawatch.example.com:8443"),
        (" https://datawatch.example.com/ ", "https://datawatch.example.com"),
    ],
)
def test_server_url_is_normalised(given: str, expected: str) -> None:
    assert parse_server_url(given) == expected


@pytest.mark.parametrize(
    "bad",
    [
        "http://datawatch.example.com",
        "datawatch.example.com",
        "https://",
        "https://user:pw@example.com",
        "https://datawatch.example.com/api",
        "https://datawatch.example.com?x=1",
        "https://datawatch.example.com:notaport",
    ],
)
def test_unsafe_or_unclear_server_urls_are_refused(bad: str) -> None:
    with pytest.raises(ValueError):
        parse_server_url(bad)


def test_fingerprint_text_forms() -> None:
    text = ":".join(["AB"] * 32)
    assert parse_fingerprint(text) == bytes([0xAB]) * 32
    assert parse_fingerprint("ab" * 32) == bytes([0xAB]) * 32
    for bad in ("", "AB:CD", "zz" * 32, "ab" * 20):
        with pytest.raises(ValueError):
            parse_fingerprint(bad)


def test_the_fetched_fingerprint_is_the_certificate_s(certificate: tuple[Path, Path, str]) -> None:
    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        assert await fetch_fingerprint(url) == certificate[2]
        assert fake.seen == []

    serve(certificate, body)


def test_fetching_a_fingerprint_from_nothing_fails() -> None:
    with pytest.raises(DatawatchError):
        asyncio.run(fetch_fingerprint("https://127.0.0.1:1"))


def test_snapshot_without_a_focus(certificate: tuple[Path, Path, str]) -> None:
    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        client = DatawatchClient(session, url, certificate[2])
        assert await client.snapshot(None) == Snapshot(
            paused=True,
            projects=("oak", "elm"),
            focus=None,
            questions=Tally(4),
            waiting=Tally(3),
            running=Tally(2),
            failed=Tally(5),
            held=Tally(7),
        )
        assert {method for method, *_ in fake.seen} == {"GET"}
        assert all("project" not in query for _, _, query, _ in fake.seen)

    serve(certificate, body)


def test_snapshot_with_a_focus_uses_datawatch_s_own_filter(
    certificate: tuple[Path, Path, str],
) -> None:
    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        result = await DatawatchClient(session, url, certificate[2]).snapshot("oak")
        assert result.focus == "oak"
        assert (result.waiting, result.running, result.failed) == (
            Tally(3, 1),
            Tally(2, 0),
            Tally(5, 4),
        )
        assert result.questions == Tally(4), "datawatch cannot filter questions yet"
        assert result.held == Tally(7), "datawatch cannot filter held items yet"
        filtered = [query for _, path, query, _ in fake.seen if "project" in query]
        assert len(filtered) == 3
        assert all(q == {**q, "view": "summary", "limit": "1", "project": "oak"} for q in filtered)

    serve(certificate, body)


def test_a_focus_that_no_longer_exists_is_not_sent_as_a_filter(
    certificate: tuple[Path, Path, str],
) -> None:
    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        result = await DatawatchClient(session, url, certificate[2]).snapshot("gone")
        assert result.focus is None
        assert all("project" not in query for _, _, query, _ in fake.seen)

    serve(certificate, body)


def test_a_full_page_of_questions_is_reported_as_at_least(
    certificate: tuple[Path, Path, str],
) -> None:
    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        result = await DatawatchClient(session, url, certificate[2]).snapshot(None)
        assert result.questions == Tally(1000, capped=True)

    fake = Fake()
    fake.questions = 1000
    serve(certificate, body, fake)


def test_a_different_certificate_is_refused_before_anything_is_sent(
    certificate: tuple[Path, Path, str],
) -> None:
    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        client = DatawatchClient(session, url, "00" * 32, token="fake-token-value")
        with pytest.raises(DatawatchCertificateError):
            await client.project_names()
        assert fake.seen == []

    serve(certificate, body)


def test_a_token_is_sent_only_when_set(certificate: tuple[Path, Path, str]) -> None:
    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        await DatawatchClient(session, url, certificate[2]).project_names()
        await DatawatchClient(session, url, certificate[2], "fake-token-value").project_names()
        assert [seen[3] for seen in fake.seen] == [None, "Bearer fake-token-value"]

    serve(certificate, body)


@pytest.mark.parametrize(
    ("response", "error"),
    [
        (lambda: web.Response(status=401), DatawatchAuthError),
        (lambda: web.Response(status=403), DatawatchAuthError),
        (lambda: web.Response(status=400), DatawatchError),
        (lambda: web.Response(status=500), DatawatchError),
        (lambda: web.Response(text="<html>not json"), DatawatchError),
        (lambda: web.json_response({"projects": "nope"}), DatawatchError),
        (lambda: web.json_response([{"dir": "x"}]), DatawatchError),
    ],
)
def test_failures_raise_and_never_look_like_an_empty_list(
    certificate: tuple[Path, Path, str],
    response: Callable[[], web.Response],
    error: type[Exception],
) -> None:
    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        with pytest.raises(error):
            await DatawatchClient(session, url, certificate[2]).project_names()

    fake = Fake()
    fake.override["/api/projects"] = response
    serve(certificate, body, fake)


@pytest.mark.parametrize(
    ("path", "reply"),
    [
        ("/api/pause", {"paused": "yes"}),
        ("/api/questions", {"count": 1}),
        ("/api/sessions", {"sessions": []}),
        ("/api/sessions", {"sessions": [], "total": True}),
        ("/api/autonomous/held", {"held": []}),
    ],
)
def test_unexpected_shapes_raise(
    certificate: tuple[Path, Path, str], path: str, reply: dict[str, Any]
) -> None:
    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        with pytest.raises(DatawatchError):
            await DatawatchClient(session, url, certificate[2]).snapshot(None)

    fake = Fake()
    fake.override[path] = lambda: web.json_response(reply)
    serve(certificate, body, fake)


def test_redirects_are_not_followed(certificate: tuple[Path, Path, str]) -> None:
    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        with pytest.raises(DatawatchError):
            await DatawatchClient(session, url, certificate[2], "fake-token-value").project_names()
        assert [seen[1] for seen in fake.seen] == ["/api/projects"]

    fake = Fake()
    fake.override["/api/projects"] = lambda: web.Response(
        status=302, headers={"Location": "https://elsewhere.example.com/"}
    )
    serve(certificate, body, fake)


def test_a_slow_server_times_out(certificate: tuple[Path, Path, str]) -> None:
    class Slow(Fake):
        async def handle(self, request: web.Request) -> web.StreamResponse:
            await asyncio.sleep(1)
            return web.json_response([])

    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        with pytest.raises(DatawatchError):
            await DatawatchClient(session, url, certificate[2], timeout=0.2).project_names()

    serve(certificate, body, Slow())
