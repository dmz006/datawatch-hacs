"""Voice actions: a draft automaton, a bug, and input to a session. Data is made up.

Each is read back and sent only after its own confirming words.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from aiohttp import web
from fake_datawatch import Fake, made_up_question
from homeassistant.core import HomeAssistant
from test_voice import Certificate, FakeSatellite, visit, voice_test

from custom_components.datawatch import const, mode
from custom_components.datawatch.voice import actions
from custom_components.datawatch.voice.actions import Act, Action, Target
from custom_components.datawatch.voice.conversation import Conversation, Needs, Reply
from custom_components.datawatch.voice.items import Item
from custom_components.datawatch.voice.phrases import Command, Kind, parse
from custom_components.datawatch.voice.questions import Option, Question

SESSION = Item("session", "host-1111", "Made-up helper")
CONFIRMS = {
    "confirm automation": Act.AUTOMATON,
    "confirm bug": Act.BUG,
    "confirm send": Act.SESSION,
}


def in_project(**more: object) -> Conversation:
    conversation = Conversation("oak", **more)  # type: ignore[arg-type]
    conversation.enter()
    return conversation


def say(conversation: Conversation, words: str) -> Reply:
    return conversation.hear(words, None)


def pending(act: Act) -> Conversation:
    """A conversation with one action read back and waiting."""
    if act is Act.SESSION:
        conversation = in_project(session_send=True, path=(SESSION,))
        say(conversation, "send to session carry on")
    else:
        conversation = in_project()
        say(conversation, "add bug it broke" if act is Act.BUG else "add automation mend it")
    return conversation


@pytest.mark.parametrize(
    ("heard", "kind", "words"),
    [
        ("Add automation.", Kind.ADD_AUTOMATON, None),
        ("add an automation", Kind.ADD_AUTOMATON, None),
        ("New automaton", Kind.ADD_AUTOMATON, None),
        ("Add automation: mend the made-up gate.", Kind.ADD_AUTOMATON, "mend the made-up gate."),
        ("Add a bug", Kind.ADD_BUG, None),
        ("Report bug, the gate sticks", Kind.ADD_BUG, "the gate sticks"),
        ("please add a new bug", Kind.ADD_BUG, None),
        ("Send to session.", Kind.SEND_SESSION, None),
        ("send to the session carry on", Kind.SEND_SESSION, "carry on"),
        ("Tell the session, run the tests", Kind.SEND_SESSION, "run the tests"),
        ("send a command", Kind.SEND_SESSION, None),
        ("confirm automation", Kind.CONFIRM_AUTOMATON, None),
        ("Confirm bug.", Kind.CONFIRM_BUG, None),
        ("confirm send", Kind.CONFIRM_SEND, None),
    ],
)
def test_ways_of_asking(heard: str, kind: Kind, words: str | None) -> None:
    assert parse(heard) == Command(kind, text=words)


@pytest.mark.parametrize(
    "heard",
    ["automations", "list automations", "add bugs", "send it", "confirm", "new automations"],
)
def test_words_that_do_not_start_an_action(heard: str) -> None:
    assert parse(heard).kind not in (
        Kind.ADD_AUTOMATON,
        Kind.ADD_BUG,
        Kind.SEND_SESSION,
        Kind.CONFIRM_AUTOMATON,
        Kind.CONFIRM_BUG,
        Kind.CONFIRM_SEND,
    )


def test_an_automation_is_read_back_and_not_sent_until_confirmed() -> None:
    conversation = in_project()
    assert say(conversation, "add automation").text == (
        "Go ahead. Say what the automation should do, or cancel."
    )
    reply = say(conversation, "Status of the made-up gate should be checked")
    assert reply.act is None
    assert reply.text == (
        "Not sent yet. This is a new draft automaton in project oak. Your words: Status of "
        "the made-up gate should be checked. Say confirm automation to send it, or cancel."
    )
    sent = say(conversation, "confirm automation")
    assert sent.act == Action(
        Target(Act.AUTOMATON, project="oak"), "Status of the made-up gate should be checked"
    )
    assert say(conversation, "confirm automation").act is None


@pytest.mark.parametrize("act", list(Act))
@pytest.mark.parametrize("heard", [*CONFIRMS, "confirm answer", "yes", "send it", "okay"])
def test_only_its_own_words_send_an_action(act: Act, heard: str) -> None:
    reply = say(pending(act), heard)
    if CONFIRMS.get(heard) is act:
        assert reply.act is not None and reply.act.target.act is act
    else:
        assert reply.act is None and reply.send is None
        assert reply.text == actions.waiting(act)


@pytest.mark.parametrize("heard", ["confirm automation", "confirm bug", "confirm send"])
def test_action_words_never_send_an_answer(heard: str) -> None:
    conversation = Conversation()
    conversation.enter()
    question = Question("q", "May it?", (Option("y", "Yes"),))
    conversation.hear("questions", None, [question])
    say(conversation, "option one")
    reply = say(conversation, heard)
    assert reply.send is None and reply.act is None


@pytest.mark.parametrize("heard", ["cancel", "go back"])
def test_cancel_drops_an_action(heard: str) -> None:
    for conversation in (pending(Act.BUG), in_project()):
        if conversation.needs("status") is not Needs.NOTHING:
            say(conversation, "add bug")
        assert say(conversation, heard).text == "Cancelled. Nothing was sent."
        assert say(conversation, "confirm bug").act is None


def test_while_waiting_nothing_is_read_and_the_assistant_hears_nothing() -> None:
    conversation = in_project(assistant=True)
    say(conversation, "add bug")
    for heard in ("status", "questions", "tell me a story", "confirm bug"):
        assert conversation.needs(heard) is Needs.NOTHING
    # The whole turn became the words, even though it sounded like a command.
    assert say(conversation, "repeat").text.startswith("Go ahead.")
    say(conversation, "the gate sticks")
    reply = say(conversation, "what do you think")
    assert reply.forward is None and reply.text == actions.waiting(Act.BUG)
    assert say(conversation, "repeat").text.startswith("Not sent yet. This is a bug")


def test_saying_the_action_again_replaces_the_words() -> None:
    conversation = pending(Act.BUG)
    assert "Your words: the latch is bent." in say(conversation, "add bug the latch is bent").text
    assert say(conversation, "add bug").text.startswith("Go ahead.")
    say(conversation, "the hinge is bent")
    sent = say(conversation, "confirm bug").act
    assert sent is not None and sent.words == "the hinge is bent"


@pytest.mark.parametrize("leave", [["stop"], [None, None], ["huh", "what", "eh"]])
def test_leaving_with_an_action_waiting_says_it_was_not_sent(leave: list[str | None]) -> None:
    conversation = pending(Act.BUG)
    for heard in leave:
        reply = conversation.silence() if heard is None else say(conversation, heard)
    assert reply.ends and reply.act is None
    assert reply.text.startswith("Your bug was not sent.")
    conversation.enter()
    assert say(conversation, "confirm bug").text == "There is nothing waiting to be sent."


def test_a_project_or_session_is_needed_before_any_words_are_asked_for() -> None:
    nowhere = Conversation(session_send=True)
    nowhere.enter()
    assert say(nowhere, "add bug").text == actions.NEEDS_PROJECT
    assert say(nowhere, "send to session").text == actions.NEEDS_SESSION
    assert say(nowhere, "add automation mend it").text == (
        f"{actions.NEEDS_PROJECT} I did not keep your words."
    )
    assert say(nowhere, "confirm automation").act is None


def test_sending_to_a_session_is_off_unless_turned_on() -> None:
    assert const.SESSION_SEND is False
    conversation = in_project(path=(SESSION,))
    assert say(conversation, "send to session").text == actions.SESSION_SEND_OFF
    said = say(conversation, "send to session carry on").text
    assert said == f"{actions.SESSION_SEND_OFF} I did not keep your words."
    assert say(conversation, "confirm send").act is None


@pytest.mark.parametrize(
    ("words", "title"),
    [
        ("mend the gate. it sticks badly", "Mend the gate"),
        ("is it  broken? yes", "Is it broken"),
        ("word " * 40, ("Word " + "word " * 15).strip()),
    ],
)
def test_the_name_is_the_first_sentence_kept_short(words: str, title: str) -> None:
    assert actions.title_of(words) == title
    assert len(actions.title_of(words)) <= actions.TITLE_LIMIT


# From here on: a throwaway Home Assistant and a pretend datawatch.


def run(certificate: Certificate, tmp_path: Path, script: list[str], fake: Fake | None = None):
    seen: dict[str, object] = {}

    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await visit(hass, satellite, *script)
        seen["said"] = [*satellite.asked, *satellite.announced]
        seen["changes"] = list(fake.changes)
        seen["answers"] = list(fake.answers)

    voice_test(certificate, tmp_path, body, fake)
    return seen


def test_voice_adds_a_draft_automaton_and_names_it(
    certificate: Certificate, tmp_path: Path
) -> None:
    words = "Mend the made-up gate. It sticks."
    script = ["set oak", f"add automation {words}", "confirm automation", "stop"]
    seen = run(certificate, tmp_path, script)
    assert seen["changes"] == [
        ("POST", "/api/autonomous/prds", {"spec": words, "project_dir": "x"}),
        (
            "PATCH",
            "/api/autonomous/prds/made1",
            {"title": "Mend the made-up gate", "actor": "comm:voice"},
        ),
    ]
    assert seen["said"][3] == (  # type: ignore[index]
        "Added a draft automaton to project oak, named Mend the made-up gate. I did not ask "
        "datawatch to plan or start it."
    )


@pytest.mark.parametrize(
    ("route", "ending"),
    [
        ("new_batch", " datawatch made a new draft bug group for it."),
        ("open_batch", " datawatch added it to an open draft bug group."),
        ("tiny_fix", " datawatch made a one-task draft for it."),
        ("something_new", ""),
    ],
)
def test_voice_reports_a_bug(
    certificate: Certificate, tmp_path: Path, route: str, ending: str
) -> None:
    fake = Fake()
    fake.bug_route = route
    script = ["set oak", "add bug", "The made-up gate sticks", "confirm bug", "stop"]
    seen = run(certificate, tmp_path, script, fake)
    ((method, path, body),) = seen["changes"]  # type: ignore[misc]
    assert (method, path) == ("POST", "/api/autonomous/defects/intake")
    assert body.pop("id").startswith("voice-")
    assert body == {
        "title": "The made-up gate sticks",
        "description": "The made-up gate sticks",
        "project": "oak",
    }
    assert seen["said"][4] == f"Bug reported for project oak.{ending}"  # type: ignore[index]


@pytest.mark.parametrize(
    ("field", "status", "command", "said", "sent"),
    [
        ("bug_status", 409, "bug", "datawatch's bug intake is turned off for project oak.", 1),
        ("bug_status", 400, "bug", "datawatch did not accept it. Nothing was sent.", 1),
        ("bug_status", 500, "bug", "I don't know whether it was sent.", 1),
        ("create_status", 400, "automation", "datawatch did not accept it.", 1),
        ("create_status", 503, "automation", "I don't know whether it was sent.", 1),
        ("name_status", 400, "automation", "but I could not name it", 2),
        ("name_status", 500, "automation", "Do not add it again.", 2),
    ],
)
def test_voice_says_what_happened_and_never_retries(
    certificate: Certificate,
    tmp_path: Path,
    field: str,
    status: int,
    command: str,
    said: str,
    sent: int,
) -> None:
    fake = Fake()
    setattr(fake, field, status)
    script = ["set oak", f"add {command} mend it", f"confirm {command}", "stop"]
    seen = run(certificate, tmp_path, script, fake)
    assert said in seen["said"][3]  # type: ignore[index]
    assert len(seen["changes"]) == sent  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "status", "ending"),
    [("bug_status", 401, "refused access"), ("create_status", 403, "refused access")],
)
def test_voice_closes_when_access_is_refused(
    certificate: Certificate, tmp_path: Path, field: str, status: int, ending: str
) -> None:
    fake = Fake()
    setattr(fake, field, status)
    command = "bug" if field == "bug_status" else "automation"
    script = ["set oak", f"add {command} mend it", f"confirm {command}", "stop"]
    seen = run(certificate, tmp_path, script, fake)
    assert ending in seen["said"][-1]  # type: ignore[index]


def test_voice_a_project_with_no_folder_gets_no_automaton(
    certificate: Certificate, tmp_path: Path
) -> None:
    script = ["set elm", "add automation mend it", "confirm automation", "stop"]
    seen = run(certificate, tmp_path, script)
    assert seen["changes"] == []
    assert "gives no folder for project elm" in seen["said"][3]  # type: ignore[index]


@pytest.mark.parametrize(
    ("reply", "said"),
    [
        (lambda: web.json_response([{"name": "elm"}]), "no longer has the project oak"),
        (lambda: web.Response(status=500), "I can't reach datawatch, so nothing was sent."),
    ],
)
def test_voice_nothing_is_sent_if_the_project_cannot_be_checked(
    certificate: Certificate, tmp_path: Path, reply: object, said: str
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await visit(hass, satellite, "set oak", "stop")
        fake.override["/api/projects"] = reply  # type: ignore[assignment]
        await visit(hass, satellite, "add bug mend it", "confirm bug", "stop")
        assert fake.changes == []
        assert said in satellite.asked[2]

    voice_test(certificate, tmp_path, body)


def test_voice_does_not_send_to_a_session_while_that_is_off(
    certificate: Certificate, tmp_path: Path
) -> None:
    script = ["sessions", "one", "set it", "send to session carry on", "confirm send", "stop"]
    seen = run(certificate, tmp_path, script)
    assert seen["changes"] == []
    assert seen["said"][4].startswith(actions.SESSION_SEND_OFF)  # type: ignore[index]


@pytest.mark.parametrize(
    ("state", "status", "said", "sent"),
    [
        ("waiting_input", 200, "Sent to the session Made-up helper.", 1),
        ("waiting_input", 400, "The session may be showing a prompt", 1),
        ("waiting_input", 500, "I don't know whether it was sent.", 1),
        ("running", 200, "is running now, not waiting for input. Nothing was sent.", 0),
        (None, 200, "datawatch no longer has that session. Nothing was sent.", 0),
    ],
)
def test_voice_sends_to_a_session_once_turned_on(
    certificate: Certificate,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    state: str | None,
    status: int,
    said: str,
    sent: int,
) -> None:
    monkeypatch.setattr(mode, "SESSION_SEND", True)

    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        fake.input_status = status
        await visit(hass, satellite, "sessions", "one", "set it", "stop")
        rows = [] if state is None else [{"full_id": "host-1111", "name": "Made-up helper"}]
        for row in rows:
            row["state"] = state or ""
        listed = {"sessions": rows, "total": len(rows)}
        fake.override["/api/sessions"] = lambda: web.json_response(listed)
        await visit(hass, satellite, "send to session carry on", "confirm send", "stop")
        assert said in satellite.asked[2], satellite.asked
        expected = {"session_id": "host-1111", "text": "carry on", "source": "comm:voice"}
        assert fake.changes == [("POST", "/api/sessions/send", expected)] * sent

    voice_test(certificate, tmp_path, body)


def test_voice_an_action_leaves_questions_alone(certificate: Certificate, tmp_path: Path) -> None:
    fake = Fake()
    fake.records = [made_up_question("q1")]
    script = ["set oak", "add bug mend it", "confirm answer", "cancel", "stop"]
    seen = run(certificate, tmp_path, script, fake)
    assert seen["changes"] == [] and seen["answers"] == []
