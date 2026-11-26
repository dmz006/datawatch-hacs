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


def made_up_plan(title: str, state: str, done: int = 0, total: int = 0) -> dict[str, Any]:
    return {"title": title, "state": state, "progress": {"done": done, "total": total}}


def made_up_automation(name: str, status: str, members: int = 1) -> dict[str, Any]:
    return {"name": name, "status": status, "members": [{}] * members}


def made_up_attention(ident: str, title: str, status: str, **more: Any) -> dict[str, Any]:
    return {"id": ident, "title": title, "status": status, **more}


def made_up_question(
    ident: str,
    text: str = "Should the made-up thing happen?",
    *,
    asker_kind: str = "system",
    blocking: bool = False,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": ident,
        "text": text,
        "asker_kind": asker_kind,
        "options": [
            {"id": "yes", "label": "Yes, do it", "tradeoffs": "It happens"},
            {"id": "no", "label": "No, leave it"},
        ],
        "recommendation": {"option_id": "no", "rationale": "It is safer"},
        "state": "open",
    }
    if blocking:
        row["blocking"] = True
    return row


class Fake:
    """Answers like datawatch for the reads the client makes, and records them."""

    def __init__(self) -> None:
        self.seen: list[tuple[str, str, dict[str, str], str | None]] = []
        self.override: dict[str, web.Response | Callable[[], web.Response]] = {}
        self.questions = 4
        self.totals = {"waiting_input": (3, 1), "running": (2, 0), "failed": (5, 4)}
        # Full question records; when None, self.questions made-up ones are served.
        self.records: list[dict[str, Any]] | None = None
        # The JSON bodies of answers received, as (question id, body).
        self.answers: list[tuple[str, dict[str, Any]]] = []
        self.answer_status = 201
        self.closed: set[str] = set()
        # Per project: current plans in order, and what is next.
        self.plans: dict[str, list[dict[str, Any]]] = {
            "oak": [made_up_plan("Roots", "in_progress", 2, 5), made_up_plan("Leaves", "planned")],
            "elm": [],
        }
        self.automations = [
            made_up_automation("Zeta", "draft"),
            made_up_automation("Alpha", "completed"),
            made_up_automation("Gamma", "blocked", members=2),
            made_up_automation("Beta", "draft"),
        ]
        self.attention: list[dict[str, Any]] = [
            made_up_attention("a1", "Mend the made-up gate", "needs_review"),
            made_up_attention("a2", "Paint the made-up fence.", "blocked"),
            made_up_attention("a3", "Old made-up work", "cancelled", review_needed=[{"t": 1}]),
        ]

    def rows(self) -> list[dict[str, Any]]:
        if self.records is not None:
            return self.records
        return [made_up_question(str(n)) for n in range(self.questions)]

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
            rows = self.rows()
            return web.json_response({"count": len(rows), "questions": rows})
        if request.path.startswith("/api/questions/"):
            parts = request.path.removeprefix("/api/questions/").split("/")
            if parts[1:] == ["answer"] and request.method == "POST":
                self.answers.append((parts[0], await request.json()))
                return web.json_response({}, status=self.answer_status)
            state = "answered" if parts[0] in self.closed else "open"
            return web.json_response({"question": {"id": parts[0], "state": state}})
        if request.path == "/api/autonomous/attention":
            return web.json_response(
                {"statuses": ["blocked", "needs_review", "paused"], "items": self.attention}
            )
        if request.path == "/api/automations":
            wanted = query.get("project")
            return web.json_response(self.automations if wanted in (None, "oak") else [])
        if request.path.startswith("/api/projects/"):
            name, what = request.path.removeprefix("/api/projects/").split("/")
            plans = self.plans[name]
            if what == "plans":
                return web.json_response({"project": name, "plans": plans, "page": {}})
            states: dict[str, int] = {}
            for plan in plans:
                states[plan["state"]] = states.get(plan["state"], 0) + 1
            following = (
                {"automaton_title": "Dig the made-up hole", "plan_title": plans[0]["title"]}
                if plans
                else None
            )
            return web.json_response(
                {
                    "counts": {"plans": {"total": len(plans), "by_state": states, "archived": 3}},
                    "progress": {"automata": {"done": 2, "total": 7, "percent": 28}},
                    "next": following,
                }
            )
        if request.path == "/api/docs/search":
            hit = {"path": "howto/x.md", "anchor": "a", "heading": "H", "excerpt": "E", "score": 1}
            return web.json_response({"hits": [hit]})
        if request.path == "/api/docs/read":
            return web.json_response({"content": "words " * 2000})
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
