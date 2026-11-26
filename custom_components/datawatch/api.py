"""A client for datawatch's REST API. It reads, and sends only answers to questions.

The server, its certificate fingerprint and any token are all settings: nothing about a
particular installation is built in. The certificate is pinned: a connection is made only
to a server presenting exactly the certificate the user approved.
"""

from __future__ import annotations

import asyncio
import hashlib
import re
import ssl
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlsplit

import aiohttp

from .voice.model import Snapshot, Tally
from .voice.questions import Option, Question

QUESTION_LIMIT = 1000
# datawatch's question ids. Anything else could change which address is requested.
_QUESTION_ID = re.compile(r"[A-Za-z0-9_-]+")
# How an answer is marked in datawatch.
ANSWER_SURFACE = "comm:voice"
DEFAULT_TIMEOUT = 10.0
_SESSION_STATES = ("waiting_input", "running", "failed")


class DatawatchError(Exception):
    """datawatch could not be read."""


class DatawatchAuthError(DatawatchError):
    """datawatch refused the token, or wants one."""


class DatawatchCertificateError(DatawatchError):
    """The server's certificate is not the approved one."""


class DatawatchClosedError(DatawatchError):
    """The question was already answered or withdrawn. Nothing was stored."""


class DatawatchSecretError(DatawatchError):
    """datawatch refused an answer that looks like it holds a secret."""


class DatawatchRefusedError(DatawatchError):
    """datawatch refused an answer. Nothing was stored."""


def _question_path(question_id: str) -> str:
    if not _QUESTION_ID.fullmatch(question_id):
        raise DatawatchError("unexpected question id")
    return f"questions/{question_id}"


def _question(row: Any) -> Question:
    """One question as datawatch describes it."""
    if not isinstance(row, dict) or not all(
        isinstance(row.get(key), str) for key in ("id", "text")
    ):
        raise DatawatchError("unexpected question")
    options = row.get("options") or []
    if not isinstance(options, list) or not all(
        isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and isinstance(item.get("label"), str)
        for item in options
    ):
        raise DatawatchError("unexpected question options")
    recommendation = row.get("recommendation")
    if not isinstance(recommendation, dict):
        recommendation = {}
    return Question(
        id=row["id"],
        text=row["text"],
        options=tuple(
            Option(item["id"], item["label"], str(item.get("tradeoffs") or "")) for item in options
        ),
        asker_kind=str(row.get("asker_kind") or ""),
        blocking=row.get("blocking") is True,
        recommended=recommendation.get("option_id"),
        rationale=str(recommendation.get("rationale") or ""),
    )


def parse_server_url(url: str) -> str:
    """Return https://host[:port], refusing anything else."""
    parts = urlsplit(url.strip())
    if parts.scheme != "https" or not parts.hostname:
        raise ValueError("enter an https:// address")
    if parts.username or parts.password:
        raise ValueError("do not put a user name or password in the address")
    if parts.path not in ("", "/") or parts.query or parts.fragment:
        raise ValueError("enter only the server address, without a path")
    _ = parts.port  # raises ValueError for a bad port
    return f"https://{parts.netloc}"


def parse_fingerprint(text: str) -> bytes:
    """A SHA-256 fingerprint as hex, with or without colons or spaces."""
    digest = bytes.fromhex(text.replace(":", "").replace(" ", ""))
    if len(digest) != hashlib.sha256().digest_size:
        raise ValueError("a SHA-256 fingerprint has 32 bytes")
    return digest


async def fetch_fingerprint(url: str, timeout: float = DEFAULT_TIMEOUT) -> str:
    """Fetch the server certificate's fingerprint, for the user to check and approve.

    Nothing is trusted or sent here: only the TLS handshake takes place.
    """
    parts = urlsplit(parse_server_url(url))
    # No certificate files are loaded: Home Assistant flags that inside its event loop,
    # and nothing is verified here anyway.
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    try:
        async with asyncio.timeout(timeout):
            _, writer = await asyncio.open_connection(
                parts.hostname, parts.port or 443, ssl=context
            )
    except (OSError, TimeoutError) as error:
        raise DatawatchError("could not connect to the server") from error
    certificate = writer.get_extra_info("ssl_object").getpeercert(binary_form=True)
    writer.close()
    return hashlib.sha256(certificate).digest().hex(":").upper()


class DatawatchClient:
    """Reads with GET. The one thing it can change is answering a question."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        url: str,
        fingerprint: str,
        token: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._session = session
        self._url = parse_server_url(url)
        self._pin = aiohttp.Fingerprint(parse_fingerprint(fingerprint))
        self._headers = {"Authorization": f"Bearer {token}"} if token else {}
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    async def _get(self, path: str, params: Mapping[str, str] | None = None) -> Any:
        try:
            async with self._session.get(
                f"{self._url}/api/{path}",
                params=params,
                headers=self._headers,
                ssl=self._pin,
                timeout=self._timeout,
                allow_redirects=False,
            ) as response:
                if response.status in (401, 403):
                    raise DatawatchAuthError(f"datawatch refused access ({response.status})")
                if response.status != 200:
                    raise DatawatchError(f"datawatch answered {response.status} for {path}")
                return await response.json(content_type=None)
        except aiohttp.ServerFingerprintMismatch as error:
            raise DatawatchCertificateError("the server certificate has changed") from error
        except (aiohttp.ClientError, TimeoutError, ValueError) as error:
            raise DatawatchError(f"could not read {path}") from error

    async def questions(self) -> tuple[Question, ...]:
        """The open questions, as datawatch orders them."""
        reply = await self._get("questions", {"state": "open", "limit": str(QUESTION_LIMIT)})
        if not isinstance(reply, dict) or not isinstance(reply.get("questions"), list):
            raise DatawatchError("unexpected question list")
        return tuple(_question(row) for row in reply["questions"])

    async def question_is_open(self, question_id: str) -> bool:
        """Whether a question is still waiting for an answer."""
        reply = await self._get(_question_path(question_id))
        record = reply.get("question") if isinstance(reply, dict) else None
        if not isinstance(record, dict) or not isinstance(record.get("state"), str):
            raise DatawatchError("unexpected question")
        return bool(record["state"] == "open")

    async def answer(self, question_id: str, option_id: str | None, words: str | None) -> None:
        """Record the user's confirmed answer. Never replaces an earlier answer.

        Tried once. If the connection fails, whether it was stored is not known.
        """
        body = {"surface": ANSWER_SURFACE}
        if option_id is not None:
            body["chosen_option_id"] = option_id
        if words is not None:
            body["quote"] = words
        address = f"{self._url}/api/{_question_path(question_id)}/answer"
        try:
            async with self._session.post(
                address,
                json=body,
                headers=self._headers,
                ssl=self._pin,
                timeout=self._timeout,
                allow_redirects=False,
            ) as response:
                status = response.status
        except aiohttp.ServerFingerprintMismatch as error:
            raise DatawatchCertificateError("the server certificate has changed") from error
        except (aiohttp.ClientError, TimeoutError) as error:
            raise DatawatchError("the answer may not have been sent") from error
        if status == 201:
            return
        if status in (401, 403):
            raise DatawatchAuthError(f"datawatch refused access ({status})")
        if status == 409:
            raise DatawatchClosedError("the question is not open")
        if status == 422:
            raise DatawatchSecretError("the answer looks like a secret")
        if 400 <= status < 500:
            raise DatawatchRefusedError(f"datawatch refused the answer ({status})")
        raise DatawatchError(f"datawatch answered {status}")

    async def search_docs(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Search datawatch's own documentation and how-tos."""
        reply = await self._get("docs/search", {"q": query, "limit": str(limit)})
        hits = reply.get("hits") if isinstance(reply, dict) else None
        if not isinstance(hits, list) or not all(isinstance(hit, dict) for hit in hits):
            raise DatawatchError("unexpected search reply")
        return [
            {key: hit.get(key) for key in ("path", "anchor", "heading", "excerpt")} for hit in hits
        ]

    async def read_doc(self, path: str, anchor: str = "") -> str:
        """Read one page, or one section of a page, of datawatch's documentation."""
        params = {"path": path}
        if anchor:
            params["anchor"] = anchor
        reply = await self._get("docs/read", params)
        content = reply.get("content") if isinstance(reply, dict) else None
        if not isinstance(content, str):
            raise DatawatchError("unexpected document")
        return content

    async def project_names(self) -> tuple[str, ...]:
        """The registered projects."""
        rows = await self._get("projects")
        if not isinstance(rows, list) or not all(
            isinstance(row, dict) and isinstance(row.get("name"), str) for row in rows
        ):
            raise DatawatchError("unexpected project list")
        return tuple(row["name"] for row in rows)

    async def paused(self) -> bool:
        """Whether new work is paused."""
        reply = await self._get("pause")
        if not isinstance(reply, dict) or not isinstance(reply.get("paused"), bool):
            raise DatawatchError("unexpected pause reply")
        return bool(reply["paused"])

    async def open_questions(self) -> Tally:
        """Open questions across all projects: datawatch cannot filter them by project."""
        reply = await self._get("questions", {"state": "open", "limit": str(QUESTION_LIMIT)})
        if not isinstance(reply, dict) or not isinstance(reply.get("questions"), list):
            raise DatawatchError("unexpected question list")
        total = len(reply["questions"])
        return Tally(total, capped=total >= QUESTION_LIMIT)

    async def held_total(self) -> Tally:
        """Held items across all projects: datawatch cannot filter them by project yet."""
        reply = await self._get("autonomous/held")
        total = reply.get("total") if isinstance(reply, dict) else None
        if not isinstance(total, int) or isinstance(total, bool):
            raise DatawatchError("unexpected held list")
        return Tally(total)

    async def stuck_total(self) -> Tally:
        """Failed or blocked automata, as datawatch's main view counts them.

        Across all projects: datawatch cannot filter these records by project yet.
        """
        reply = await self._get("autonomous/triage")
        records = reply.get("records") if isinstance(reply, dict) else None
        if not isinstance(records, list) or not all(
            isinstance(row, dict) and isinstance(row.get("status"), str) for row in records
        ):
            raise DatawatchError("unexpected triage list")
        return Tally(sum(row["status"] in ("failed", "blocked") for row in records))

    async def session_total(self, state: str, project: str | None = None) -> int:
        """How many sessions are in a state, using datawatch's own project filter."""
        params = {"view": "summary", "status": state, "limit": "1"}
        if project is not None:
            params["project"] = project
        reply = await self._get("sessions", params)
        total = reply.get("total") if isinstance(reply, dict) else None
        if not isinstance(total, int) or isinstance(total, bool):
            raise DatawatchError("unexpected session list")
        return total

    async def snapshot(self, focus: str | None) -> Snapshot:
        """Everything the conversation needs. focus is dropped if it no longer exists."""
        projects, paused, questions, held, stuck = await asyncio.gather(
            self.project_names(),
            self.paused(),
            self.open_questions(),
            self.held_total(),
            self.stuck_total(),
        )
        if focus not in projects:
            focus = None
        totals = await asyncio.gather(*(self.session_total(s) for s in _SESSION_STATES))
        inside: list[int | None] = [None] * len(_SESSION_STATES)
        if focus is not None:
            inside = list(
                await asyncio.gather(*(self.session_total(s, focus) for s in _SESSION_STATES))
            )
        waiting, running, failed = (Tally(t, i) for t, i in zip(totals, inside, strict=True))
        return Snapshot(
            paused=paused,
            projects=projects,
            focus=focus,
            questions=questions,
            waiting=waiting,
            running=running,
            failed=failed,
            held=held,
            stuck=stuck,
        )
