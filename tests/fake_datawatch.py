"""A fake datawatch with a throwaway certificate. Everything here is made up."""

from __future__ import annotations

import asyncio
import ssl
import subprocess
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import aiohttp
from aiohttp import web


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
        if request.path == "/api/autonomous/triage":
            states = ["blocked", "failed", "merge_pending", "merge_blocked"]
            return web.json_response({"records": [{"status": x} for x in states]})
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
