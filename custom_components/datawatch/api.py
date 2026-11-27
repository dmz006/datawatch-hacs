"""A client for datawatch's REST API.

It reads. The only changes it can make are the ones a user has confirmed: answering a
question, adding a draft automaton, reporting a bug, and sending input to a session.

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
from urllib.parse import quote, urlsplit

import aiohttp

from .gantt import AUTOMATA, HOURS, STATUSES
from .voice.automata import Automaton, Task
from .voice.items import Decision
from .voice.model import Snapshot, Tally
from .voice.questions import Option, Question
from .voice.reports import Attention, Automation, Child, Held, Listed, Overview, Plan
from .voice.work import Alert, Delivery, Finished, Session

QUESTION_LIMIT = 1000
# The most plans datawatch returns in one page.
PLAN_LIMIT = 500
# Running automata and held items read at once.
LIST_LIMIT = 200
# Sessions and finished automata read at once.
RECENT_LIMIT = 50
# datawatch's ids. Anything else could change which address is requested.
_IDENTIFIER = re.compile(r"[A-Za-z0-9_-]+")
# How an answer is marked in datawatch.
ANSWER_SURFACE = "comm:voice"
DEFAULT_TIMEOUT = 10.0
# For a list datawatch is known to take several seconds over.
SLOW_TIMEOUT = 30.0
_SESSION_STATES = ("waiting_input", "running", "failed")
# datawatch's smaller dashboard data sets: quick to read, and numbers, times and titles
# only. Its work map and timeline are far larger and are not here.
DASHBOARDS = {
    "console": "dashboard/console",
    "lane_pulse": "dashboard/lane-pulse",
    "lane_use": "dashboard/series/lane-utilization",
    "defects_per_day": "dashboard/series/defects-per-day",
    "review_backlog": "dashboard/series/review-backlog",
    "throughput_forecast": "dashboard/series/throughput-forecast",
}


class DatawatchError(Exception):
    """datawatch could not be read."""


class DatawatchMissingError(DatawatchError):
    """datawatch has no such thing."""


class DatawatchAuthError(DatawatchError):
    """datawatch refused the token, or wants one."""


class DatawatchCertificateError(DatawatchError):
    """The server's certificate is not the approved one."""


class DatawatchClosedError(DatawatchError):
    """The question was already answered or withdrawn. Nothing was stored."""


class DatawatchSecretError(DatawatchError):
    """datawatch refused an answer that looks like it holds a secret."""


class DatawatchRefusedError(DatawatchError):
    """datawatch refused a change. Nothing was stored."""


class DatawatchBugsOffError(DatawatchRefusedError):
    """datawatch's bug intake is turned off for the project."""


def _question_path(question_id: str) -> str:
    if not _IDENTIFIER.fullmatch(question_id):
        raise DatawatchError("unexpected question id")
    return f"questions/{question_id}"


def _checked(ident: str) -> str:
    if not _IDENTIFIER.fullmatch(ident):
        raise DatawatchError("unexpected id")
    return ident


def _text(row: Mapping[str, Any], key: str) -> str:
    value = row.get(key)
    return value if isinstance(value, str) else ""


def _texts(value: Any) -> tuple[str, ...]:
    return tuple(v for v in value if isinstance(v, str)) if isinstance(value, list) else ()


def _decisions(value: Any) -> tuple[Decision, ...]:
    return tuple(
        Decision(row["kind"], _text(row, "actor"), _text(row, "note"), _text(row, "at"))
        for row in _rows(value or [], "kind")
    )


def _automation(row: Mapping[str, Any]) -> Automation:
    members = row.get("members") or []
    return Automation(
        row["name"],
        row["status"],
        len(members),
        _text(row, "id"),
        _text(row, "description"),
        tuple(m["prd_id"] for m in members if isinstance(m, dict) and _text(m, "prd_id")),
        _decisions(row.get("decisions")),
        _text(row, "updated_at"),
    )


def _session(row: Mapping[str, Any], state: str) -> Session:
    return Session(
        row["full_id"],
        str(row.get("name") or ""),
        state,
        str(row.get("project") or ""),
        str(row.get("llm_ref") or row.get("backend") or ""),
        str(row.get("last_activity") or row.get("updated_at") or ""),
    )


def _project_path(project: str, what: str) -> str:
    if project in ("", ".", ".."):
        raise DatawatchError("unexpected project name")
    return f"projects/{quote(project, safe='')}/{what}"


def _number(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise DatawatchError("expected a number")
    return value


def _table(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DatawatchError("expected a record")
    return value


def _rows(value: Any, *text: str) -> list[dict[str, Any]]:
    """A list of records, each with these text fields."""
    if not isinstance(value, list) or not all(
        isinstance(row, dict) and all(isinstance(row.get(key), str) for key in text)
        for row in value
    ):
        raise DatawatchError("unexpected list")
    return value


def _title(row: Mapping[str, Any]) -> str:
    """A record's title. datawatch can leave one out, which must not fail the whole read."""
    title = row.get("title")
    return title if isinstance(title, str) and title.strip() else "untitled"


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
        automaton_id=_text(row, "prd_id"),
        task_id=_text(row, "task_id"),
        asked_by=_text(row, "asked_by"),
        tags=_texts(row.get("system_tags")),
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
    """Reads with GET. Each change is one request, tried once."""

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

    async def _get(
        self, path: str, params: Mapping[str, str] | None = None, timeout: float | None = None
    ) -> Any:
        try:
            async with self._session.get(
                f"{self._url}/api/{path}",
                params=params,
                headers=self._headers,
                ssl=self._pin,
                timeout=aiohttp.ClientTimeout(total=timeout) if timeout else self._timeout,
                allow_redirects=False,
            ) as response:
                if response.status == 404:
                    raise DatawatchMissingError(f"datawatch has no {path}")
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

    async def _write(self, method: str, path: str, body: Mapping[str, str]) -> tuple[int, Any]:
        """Send one change, once. Returns the status and any JSON reply.

        If the connection fails, or datawatch reports its own fault, whether the change was
        made is not known: that is a plain DatawatchError.
        """
        try:
            async with self._session.request(
                method,
                f"{self._url}/api/{path}",
                json=dict(body),
                headers=self._headers,
                ssl=self._pin,
                timeout=self._timeout,
                allow_redirects=False,
            ) as response:
                status = response.status
                try:
                    reply = await response.json(content_type=None)
                except ValueError:
                    reply = None
        except aiohttp.ServerFingerprintMismatch as error:
            raise DatawatchCertificateError("the server certificate has changed") from error
        except (aiohttp.ClientError, TimeoutError) as error:
            raise DatawatchError("the change may not have been sent") from error
        if status in (401, 403):
            raise DatawatchAuthError(f"datawatch refused access ({status})")
        if status >= 500 or 300 <= status < 400:
            raise DatawatchError(f"datawatch answered {status}")
        return status, reply

    async def answer(self, question_id: str, option_id: str | None, words: str | None) -> None:
        """Record the user's confirmed answer. Never replaces an earlier answer."""
        body = {"surface": ANSWER_SURFACE}
        if option_id is not None:
            body["chosen_option_id"] = option_id
        if words is not None:
            body["quote"] = words
        status, _ = await self._write("POST", f"{_question_path(question_id)}/answer", body)
        if status == 201:
            return
        if status == 409:
            raise DatawatchClosedError("the question is not open")
        if status == 422:
            raise DatawatchSecretError("the answer looks like a secret")
        if 400 <= status < 500:
            raise DatawatchRefusedError(f"datawatch refused the answer ({status})")
        raise DatawatchError(f"datawatch answered {status}")

    async def create_automaton(self, spec: str, directory: str) -> str:
        """Add a draft automaton described by spec. Returns its id."""
        status, reply = await self._write(
            "POST", "autonomous/prds", {"spec": spec, "project_dir": directory}
        )
        if 400 <= status < 500:
            raise DatawatchRefusedError(f"datawatch refused the automaton ({status})")
        made = reply.get("id") if isinstance(reply, dict) else None
        if status not in (200, 201) or not isinstance(made, str):
            raise DatawatchError(f"unexpected reply to a new automaton ({status})")
        return made

    async def name_automaton(self, automaton_id: str, title: str) -> None:
        """Set an automaton's title. Its description is left as it is."""
        status, _ = await self._write(
            "PATCH",
            f"autonomous/prds/{_checked(automaton_id)}",
            {"title": title, "actor": ANSWER_SURFACE},
        )
        if status != 200:
            raise DatawatchError(f"datawatch answered {status}")

    async def report_bug(self, ident: str, title: str, description: str, project: str) -> str:
        """Hand a bug to datawatch's intake. Returns the route datawatch chose."""
        body = {"id": ident, "title": title, "description": description, "project": project}
        status, reply = await self._write("POST", "autonomous/defects/intake", body)
        if status == 409:
            raise DatawatchBugsOffError("bug intake is off for the project")
        if 400 <= status < 500:
            raise DatawatchRefusedError(f"datawatch refused the bug ({status})")
        if status != 200:
            raise DatawatchError(f"datawatch answered {status}")
        route = reply.get("route") if isinstance(reply, dict) else None
        return route if isinstance(route, str) else ""

    async def send_to_session(self, session_id: str, text: str) -> None:
        """Type confirmed words into a session, marked as coming from voice."""
        body = {"session_id": _checked(session_id), "text": text, "source": ANSWER_SURFACE}
        status, reply = await self._write("POST", "sessions/send", body)
        if 400 <= status < 500:
            raise DatawatchRefusedError(f"datawatch refused the input ({status})")
        if status != 200 or not (isinstance(reply, dict) and reply.get("ok") is True):
            raise DatawatchError(f"unexpected reply to session input ({status})")

    async def project_directories(self) -> dict[str, str]:
        """The registered projects and the folder datawatch gives for each."""
        rows = await self._get("projects")
        if not isinstance(rows, list) or not all(
            isinstance(row, dict) and isinstance(row.get("name"), str) for row in rows
        ):
            raise DatawatchError("unexpected project list")
        return {row["name"]: _text(row, "dir") for row in rows}

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

    async def attention(self) -> list[Attention]:
        """The automata datawatch says need the user, chosen as its web app chooses them."""
        reply = _table(await self._get("autonomous/attention"))
        statuses = reply.get("statuses")
        if not isinstance(statuses, list):
            raise DatawatchError("unexpected attention reply")
        wanted = {str(status).lower() for status in statuses}
        found: dict[str, Attention] = {}
        for row in _rows(reply.get("items"), "id", "status"):
            held = row.get("review_needed")
            held_tasks = len(held) if isinstance(held, list) else int(bool(held))
            if row.get("is_template") or not (row["status"] in wanted or held_tasks):
                continue
            found.setdefault(
                row["id"], Attention(_title(row), row["status"], held_tasks, row["id"])
            )
        return list(found.values())

    async def running(self, project: str | None = None) -> tuple[list[Listed], int]:
        """The automata running now, with datawatch's own filters, and how many there are."""
        params = {"status": "running", "limit": str(LIST_LIMIT)}
        if project is not None:
            params["project"] = project
        reply = _table(await self._get("autonomous/prds", params))
        rows = []
        for row in _rows(reply.get("prds"), "id"):
            counts = row.get("task_status_counts")
            counts = counts if isinstance(counts, dict) else {}
            done = counts.get("completed")
            rows.append(
                Listed(
                    row["id"],
                    _title(row),
                    str(row.get("project") or ""),
                    done if isinstance(done, int) else 0,
                    _number(row.get("task_count") or 0),
                    _text(row, "updated_at"),
                )
            )
        return rows, _number(reply.get("total"))

    async def held_items(self) -> tuple[list[Held], int]:
        """What is on hold, across all projects: datawatch cannot filter this list."""
        reply = _table(await self._get("autonomous/held"))
        rows = [
            Held(
                row["id"],
                _title(row),
                str(row.get("reason") or ""),
                str(row.get("next_look_text") or ""),
                str(row.get("project") or ""),
            )
            for row in _rows(reply.get("held"), "id")
        ]
        return rows, _number(reply.get("total"))

    async def automaton(self, automaton_id: str, hold: str = "") -> Automaton:
        """One automaton with its tasks."""
        if not _IDENTIFIER.fullmatch(automaton_id):
            raise DatawatchError("unexpected automaton id")
        reply = _table(await self._get(f"autonomous/prds/{automaton_id}"))
        if not all(isinstance(reply.get(key), str) for key in ("id", "status")):
            raise DatawatchError("unexpected automaton")
        tasks = []
        for story in _rows(reply.get("stories") or []):
            for task in _rows(story.get("tasks") or []):
                reason = task.get("blocked_reason") or task.get("wait_reason") or ""
                # A finished task's old waiting note no longer explains anything.
                if task.get("status") == "completed":
                    reason = ""
                tasks.append(
                    Task(
                        _title(task),
                        str(task.get("status") or ""),
                        str(reason),
                        _text(task, "id"),
                    )
                )
        return Automaton(
            id=reply["id"],
            title=_title(reply),
            status=reply["status"],
            project=str(reply.get("project") or ""),
            reason=str(reply.get("blocked_reason") or ""),
            hold=hold,
            tasks=tuple(tasks),
            goal=_text(reply, "spec"),
            decisions=_decisions(reply.get("decisions")),
        )

    async def automaton_brief(self, automaton_id: str) -> Child:
        """An automaton's title and status, without its tasks."""
        path = f"autonomous/prds/{_checked(automaton_id)}"
        reply = _table(await self._get(path, {"detail": "summary"}))
        if not all(isinstance(reply.get(key), str) for key in ("id", "status")):
            raise DatawatchError("unexpected automaton")
        return Child(reply["id"], _text(reply, "title"), reply["status"])

    async def plan_automata(self, plan_id: str, limit: int) -> tuple[list[Child], int]:
        """A plan's automata in run order, and how many there are."""
        reply = _table(
            await self._get(f"plans/{_checked(plan_id)}/automata", {"limit": str(limit)})
        )
        rows = [
            Child(row["id"], _text(row, "title"), _text(row, "state"))
            for row in _rows(reply.get("automata"), "id")
        ]
        return rows, _number(_table(reply.get("page")).get("total"))

    async def plan_tasks(self, plan_id: str, limit: int) -> tuple[list[Child], int]:
        """A plan's tasks, and how many there are."""
        reply = _table(await self._get(f"plans/{_checked(plan_id)}/tasks", {"limit": str(limit)}))
        rows = [
            Child(
                row["id"],
                _text(row, "title"),
                _text(row, "status"),
                row["automaton_id"],
                _text(row, "automaton_title"),
            )
            for row in _rows(reply.get("tasks"), "id", "automaton_id")
        ]
        return rows, _number(_table(reply.get("page")).get("total"))

    async def automation(self, automation_id: str) -> Automation:
        """One automation with its members and history."""
        reply = _table(await self._get(f"automations/{_checked(automation_id)}"))
        if not all(isinstance(reply.get(key), str) for key in ("name", "status")):
            raise DatawatchError("unexpected automation")
        return _automation(reply)

    async def session(self, session_id: str) -> Session | None:
        """One session, or None if datawatch no longer lists it. Never its output."""
        reply = _table(
            await self._get(
                "sessions", {"view": "summary", "limit": "50", "q": _checked(session_id)}
            )
        )
        for row in _rows(reply.get("sessions"), "full_id", "state"):
            if row["full_id"] == session_id:
                return _session(row, row["state"])
        return None

    async def overview(self, project: str) -> Overview:
        """A project's plans at a glance."""
        reply = _table(await self._get(_project_path(project, "overview-summary")))
        plans = _table(_table(reply.get("counts")).get("plans"))
        done = _table(_table(reply.get("progress")).get("automata"))
        following = reply.get("next")
        following = following if isinstance(following, dict) else {}
        return Overview(
            project=project,
            plan_states=tuple(
                (str(state), _number(number))
                for state, number in _table(plans.get("by_state") or {}).items()
            ),
            plans=_number(plans.get("total")),
            archived=_number(plans.get("archived") or 0),
            done=_number(done.get("done")),
            total=_number(done.get("total")),
            next_automaton=str(following.get("automaton_title") or ""),
            next_plan=str(following.get("plan_title") or ""),
        )

    async def plans(self, project: str) -> list[Plan]:
        """A project's current plans, in datawatch's order."""
        reply = _table(await self._get(_project_path(project, "plans"), {"limit": str(PLAN_LIMIT)}))
        result = []
        for row in _rows(reply.get("plans"), "state"):
            progress = row.get("progress")
            progress = progress if isinstance(progress, dict) else {}
            done, total = progress.get("done"), progress.get("total")
            following = row.get("next")
            following = following if isinstance(following, dict) else {}
            result.append(
                Plan(
                    _title(row),
                    row["state"],
                    done if isinstance(done, int) else 0,
                    total if isinstance(total, int) else 0,
                    _text(row, "uid") or _text(row, "id"),
                    _text(row, "goal"),
                    frozenset(_texts(row.get("automaton_ids"))),
                    _text(following, "automaton_id"),
                )
            )
        return result

    async def automations(self, project: str | None = None) -> list[Automation]:
        """Automations, filtered by datawatch when a project is given."""
        params = {"project": project} if project is not None else None
        return [
            _automation(row)
            for row in _rows(await self._get("automations", params), "name", "status")
        ]

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

    async def sessions(
        self,
        state: str,
        project: str | None = None,
        within: tuple[str, str] | None = None,
    ) -> tuple[list[Session], int]:
        """Sessions in a state, and how many there are. Never their terminal output.

        within: ('automaton' or 'automation', its id), using datawatch's own filter.
        """
        params = {"view": "summary", "status": state, "limit": str(RECENT_LIMIT)}
        if project is not None:
            params["project"] = project
        if within is not None:
            params[within[0]] = _checked(within[1])
        reply = _table(await self._get("sessions", params))
        rows = [_session(row, state) for row in _rows(reply.get("sessions"), "full_id")]
        return rows, _number(reply.get("total"))

    async def finished(self, project: str | None = None) -> tuple[list[Finished], int]:
        """Completed automata, most recently updated first, and how many there are."""
        params = {"status": "completed", "limit": str(RECENT_LIMIT)}
        if project is not None:
            params["project"] = project
        reply = _table(await self._get("autonomous/prds", params, timeout=SLOW_TIMEOUT))
        rows = []
        for row in _rows(reply.get("prds"), "id"):
            shipped = row.get("shipped")
            rows.append(
                Finished(
                    row["id"],
                    _title(row),
                    shipped if isinstance(shipped, bool) else None,
                    str(row.get("merged_in_release") or ""),
                )
            )
        return rows, _number(reply.get("total"))

    async def alerts(self) -> tuple[list[Alert], int]:
        """Unread alerts in datawatch's order, and how many are unread. Never their bodies."""
        reply = _table(await self._get("alerts"))
        rows = [
            Alert(
                row["id"],
                _title(row),
                _text(row, "level"),
                _text(row, "session_id"),
                _text(row, "created_at"),
            )
            for row in _rows(reply.get("alerts"), "id")
            if row.get("read") is not True
        ]
        return rows, _number(reply.get("unread_count"))

    async def dashboard(self, name: str) -> dict[str, Any]:
        """One of datawatch's dashboard data sets, as datawatch gives it."""
        path = DASHBOARDS.get(name)
        if path is None:
            raise DatawatchError("unknown dashboard data set")
        return _table(await self._get(path))

    async def live_work(self) -> tuple[dict[str, Any], dict[str, Any]]:
        """What the lanes ran, and the unfinished automata with their tasks."""
        lanes = _table(await self._get("autonomous/lane-utilization", {"window": f"{HOURS}h"}))
        query = {"status": STATUSES, "full": "true", "limit": str(AUTOMATA)}
        listed = _table(await self._get("autonomous/prds", query))
        rows = listed.get("prds")
        if not isinstance(lanes.get("lanes"), list) or not isinstance(rows, list):
            raise DatawatchError("unexpected live work reply")
        # Tasks that datawatch counts but does not send would look like nothing running.
        for row in rows:
            if isinstance(row, dict) and row.get("task_count") and "stories" not in row:
                raise DatawatchError("datawatch sent automata without their tasks")
        return lanes, listed

    async def delivery(self, automaton_id: str) -> Delivery | None:
        """datawatch's record of what an automaton changed, or None if it has none."""
        if not _IDENTIFIER.fullmatch(automaton_id):
            raise DatawatchError("unexpected automaton id")
        try:
            reply = _table(await self._get(f"autonomous/prds/{automaton_id}/change-record"))
        except DatawatchMissingError:
            return None

        def size(key: str) -> int:
            value = reply.get(key)
            if isinstance(value, (list, dict)):
                return len(value)
            return value if isinstance(value, int) else 0

        return Delivery(size("files"), size("packages"), size("tests_added"))

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
