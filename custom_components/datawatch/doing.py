"""Carry out one action the user has just confirmed, and say what happened.

Each change is sent once and never repeated here: after a lost connection it is not known
whether datawatch has it, and the user is told so.
"""

from __future__ import annotations

import logging
import secrets

from homeassistant.util import dt as dt_util

from .api import (
    DatawatchAuthError,
    DatawatchBugsOffError,
    DatawatchCertificateError,
    DatawatchClient,
    DatawatchError,
    DatawatchRefusedError,
)
from .voice.actions import SESSION_SEND_OFF, Act, Action, title_of
from .voice.language import N_, t
from .voice.reports import words

_LOGGER = logging.getLogger(__name__)

NOT_CHECKED = N_("I can't reach datawatch, so nothing was sent. Say it again.")
UNSURE = N_("I don't know whether it was sent. Check datawatch before saying it again.")
REFUSED = N_("datawatch did not accept it. Nothing was sent.")
_SESSION_REFUSED = N_(
    "datawatch did not accept it, so nothing was sent. The session may be showing a prompt "
    "to answer in datawatch."
)
_BUG_ROUTES = {
    "tiny_fix": N_("datawatch made a one-task draft for it."),
    "open_batch": N_("datawatch added it to an open draft bug group."),
    "new_batch": N_("datawatch made a new draft bug group for it."),
}


class _Stopped(Exception):
    """Nothing was sent, and this says why."""


async def _directory(client: DatawatchClient, project: str) -> str:
    try:
        directories = await client.project_directories()
    except DatawatchCertificateError, DatawatchAuthError:
        raise
    except DatawatchError as error:
        raise _Stopped(t(NOT_CHECKED)) from error
    if project not in directories:
        raise _Stopped(
            t("datawatch no longer has the project {project}. Nothing was sent.", project=project)
        )
    return directories[project]


async def _automaton(client: DatawatchClient, action: Action) -> str:
    project = action.target.project
    directory = await _directory(client, project)
    if not directory:
        raise _Stopped(
            t("datawatch gives no folder for project {project}. Nothing was sent.", project=project)
        )
    made = await client.create_automaton(action.words, directory)
    title = title_of(action.words)
    try:
        await client.name_automaton(made, title)
    except DatawatchError:
        _LOGGER.warning("A new automaton could not be named", exc_info=True)
        return t(
            "Added a draft automaton to project {project}, but I could not name it, so it "
            "may show as untitled. Do not add it again.",
            project=project,
        )
    return t(
        "Added a draft automaton to project {project}, named {title}. I did not ask "
        "datawatch to plan or start it.",
        project=project,
        title=title,
    )


async def _bug(client: DatawatchClient, action: Action) -> str:
    project = action.target.project
    await _directory(client, project)
    ident = f"voice-{dt_util.utcnow():%Y%m%d-%H%M%S}-{secrets.token_hex(2)}"
    try:
        route = await client.report_bug(ident, title_of(action.words), action.words, project)
    except DatawatchBugsOffError:
        return t(
            "datawatch's bug intake is turned off for project {project}. Nothing was sent.",
            project=project,
        )
    reported = t("Bug reported for project {project}.", project=project)
    became = _BUG_ROUTES.get(route)
    return f"{reported} {t(became)}" if became else reported


async def _session(client: DatawatchClient, action: Action) -> str:
    target = action.target.session
    assert target is not None, "a session action has a session"
    try:
        found = await client.session(target.id)
    except DatawatchCertificateError, DatawatchAuthError:
        raise
    except DatawatchError as error:
        raise _Stopped(t(NOT_CHECKED)) from error
    if found is None:
        raise _Stopped(t("datawatch no longer has that session. Nothing was sent."))
    if found.state != "waiting_input":
        raise _Stopped(
            t(
                "That session is {state} now, not waiting for input. Nothing was sent.",
                state=words(found.state),
            )
        )
    try:
        await client.send_to_session(target.id, action.words)
    except DatawatchRefusedError:
        return t(_SESSION_REFUSED)
    return t("Sent to the {item}.", item=target.spoken())


async def perform(client: DatawatchClient, action: Action, session_send: bool) -> str:
    """What to say after trying. Certificate and access problems are raised."""
    try:
        match action.target.act:
            case Act.AUTOMATON:
                return await _automaton(client, action)
            case Act.BUG:
                return await _bug(client, action)
            case Act.SESSION:
                # Checked here as well as in the conversation.
                if not session_send:
                    return t(SESSION_SEND_OFF)
                return await _session(client, action)
    except _Stopped as stopped:
        return str(stopped)
    except DatawatchCertificateError, DatawatchAuthError:
        raise
    except DatawatchRefusedError:
        _LOGGER.warning("datawatch refused an action", exc_info=True)
        return t(REFUSED)
    except DatawatchError:
        _LOGGER.warning("An action may not have reached datawatch", exc_info=True)
        return t(UNSURE)
