"""Answering by voice, and the AI assistant, in a real (throwaway) Home Assistant."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from aiohttp import web
from fake_datawatch import Fake, made_up_question
from homeassistant.components import conversation
from homeassistant.components.conversation.const import DATA_COMPONENT as CONVERSATION_COMPONENT
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers import intent, llm
from test_voice import CLOSING, Certificate, FakeSatellite, visit, voice_test

from custom_components.datawatch.const import CONF_ASSISTANT, DISCUSSING, DOMAIN

OWN = "You are Pat, a made-up assistant with a dry wit. Never forget the made-up cat."
SENT = "Answer sent. Say next question."
POSTS = "POST"


def posts(fake: Fake) -> list[str]:
    return [path for method, path, *_ in fake.seen if method == POSTS]


def test_a_confirmed_answer_is_sent_once(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await visit(hass, satellite, "questions", "option one", "confirm answer", "stop")
        assert fake.answers == [("0", {"surface": "comm:voice", "chosen_option_id": "yes"})]
        assert posts(fake) == ["/api/questions/0/answer"]
        assert satellite.asked[1].startswith("Question 1 of 4, from datawatch.")
        assert satellite.asked[2].startswith("Not sent yet.")
        assert satellite.asked[3] == SENT

    voice_test(certificate, tmp_path, body)


def test_own_words_are_sent_exactly_and_never_replace_an_answer(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        said = "Not before Friday, and tell nobody-else."
        await visit(hass, satellite, "questions", "my answer", said, "confirm answer", "stop")
        ((_, sent),) = fake.answers
        assert sent == {"surface": "comm:voice", "quote": said}
        assert "supersedes" not in sent

    voice_test(certificate, tmp_path, body)


@pytest.mark.parametrize(
    "script",
    [
        ("questions", "option one", "stop"),
        ("questions", "option one", "cancel", "confirm answer", "stop"),
        ("questions", "option one", None, None),
        ("questions", "option one", "yes", "send it", "go ahead"),
        ("questions", "my answer", "confirm answer", "stop"),
        ("confirm answer", "questions", "confirm answer", "stop"),
    ],
)
def test_without_confirmation_nothing_is_sent(
    certificate: Certificate, tmp_path: Path, script: tuple[str | None, ...]
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await visit(hass, satellite, *script)
        assert posts(fake) == []

    voice_test(certificate, tmp_path, body)


def test_a_question_closed_meanwhile_is_not_answered(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        fake.closed.add("0")
        await visit(hass, satellite, "questions", "option one", "confirm answer", "stop")
        assert posts(fake) == []
        assert satellite.asked[-1].startswith("That question was already answered")

    voice_test(certificate, tmp_path, body)


@pytest.mark.parametrize(
    ("status", "said"),
    [
        (409, "That question was already answered or withdrawn. Nothing was sent."),
        (422, "datawatch refused that answer because it looks like it holds a secret."),
        (400, "datawatch refused that answer. Nothing was sent."),
        (500, "I don't know whether the answer was sent. Say questions to check."),
        (302, "I don't know whether the answer was sent."),
    ],
)
def test_a_failed_send_is_said_and_never_retried(
    certificate: Certificate, tmp_path: Path, status: int, said: str
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        fake.answer_status = status
        await visit(hass, satellite, "questions", "option one", "confirm answer", "stop")
        assert len(posts(fake)) == 1
        assert satellite.asked[-1].startswith(said)

    voice_test(certificate, tmp_path, body)


@pytest.mark.parametrize("status", [401, 403])
def test_refused_access_while_answering_ends_the_mode(
    certificate: Certificate, tmp_path: Path, status: int
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        fake.answer_status = status
        await visit(hass, satellite, "questions", "option one", "confirm answer")
        assert satellite.announced[-1].startswith("datawatch refused access.")

    voice_test(certificate, tmp_path, body)


def test_if_the_question_cannot_be_checked_nothing_is_sent(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        fake.override["/api/questions/0"] = lambda: web.Response(status=500)
        await visit(hass, satellite, "questions", "option one", "confirm answer", "stop")
        assert posts(fake) == []
        assert satellite.asked[-1].startswith("I can't reach datawatch, so nothing was sent.")

    voice_test(certificate, tmp_path, body)


class PromptAssistant(conversation.ConversationEntity):
    """An AI assistant with its own instructions, built the way Home Assistant's are."""

    _attr_supported_features = conversation.ConversationEntityFeature.CONTROL
    entity_id = "conversation.pat"
    _attr_name = "Pat"

    def __init__(self) -> None:
        self.asked: list[str] = []
        self.chats: list[str] = []
        self.prompt = ""
        self.tools: list[str] = []
        self.discussing: list[str | None] = []

    @property
    def supported_languages(self) -> str:
        return "*"

    async def _async_handle_message(
        self,
        user_input: conversation.ConversationInput,
        chat_log: conversation.ChatLog,
    ) -> conversation.ConversationResult:
        await chat_log.async_provide_llm_data(
            user_input.as_llm_context(DOMAIN), llm.LLM_API_ASSIST, OWN, None
        )
        self.asked.append(user_input.text)
        self.chats.append(chat_log.conversation_id)
        self.discussing.append(self.hass.data[DISCUSSING])
        system = chat_log.content[0]
        assert isinstance(system, conversation.SystemContent)
        self.prompt = system.content
        assert chat_log.llm_api
        self.tools = [tool.name for tool in chat_log.llm_api.tools]
        response = intent.IntentResponse(language=user_input.language)
        response.async_set_speech(f"Pat heard {len(self.asked)}.")
        return conversation.ConversationResult(
            response=response, conversation_id=chat_log.conversation_id
        )


async def add_assistant(hass: HomeAssistant) -> PromptAssistant:
    assistant = PromptAssistant()
    await hass.data[CONVERSATION_COMPONENT].async_add_entities([assistant])
    await hass.async_block_till_done()
    return assistant


async def choose(hass: HomeAssistant, agent_id: str | None) -> None:
    """Set the AI assistant through datawatch's options screen."""
    (entry,) = hass.config_entries.async_entries(DOMAIN)
    form = await hass.config_entries.options.async_init(entry.entry_id)
    assert form["step_id"] == "init"
    await hass.config_entries.options.async_configure(
        form["flow_id"], {CONF_ASSISTANT: agent_id} if agent_id else {}
    )
    await hass.async_block_till_done()
    assert dict(entry.options) == ({CONF_ASSISTANT: agent_id} if agent_id else {})


async def ask_typed(hass: HomeAssistant, assistant: PromptAssistant) -> None:
    await conversation.async_converse(
        hass, "tell me about my work", None, Context(), language="en", agent_id=assistant.entity_id
    )


def test_datawatch_adds_to_the_assistant_and_keeps_its_own_instructions(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        assistant = await add_assistant(hass)

        await ask_typed(hass, assistant)
        before, tools_before = assistant.prompt, assistant.tools
        assert before.startswith(OWN)
        assert "datawatch" not in before, "off until an assistant is chosen"
        assert not [name for name in tools_before if name.startswith("datawatch__")]

        await choose(hass, assistant.entity_id)
        await ask_typed(hass, assistant)
        assert assistant.prompt.startswith(OWN), "its own instructions still come first"
        unchanged = [line for line in before.splitlines() if "time is" not in line.lower()]
        assert [line for line in unchanged if line not in assistant.prompt] == []
        assert "What you can do with datawatch now:" in assistant.prompt
        assert "datawatch__search_docs" in assistant.prompt
        assert set(tools_before) < set(assistant.tools), "no tool was taken away"
        assert sorted(set(assistant.tools) - set(tools_before)) == [
            "datawatch__automaton",
            "datawatch__projects",
            "datawatch__questions",
            "datawatch__read_doc",
            "datawatch__report",
            "datawatch__search_docs",
            "datawatch__status",
            "datawatch__work",
        ]

        await choose(hass, None)
        await ask_typed(hass, assistant)
        assert "datawatch" not in assistant.prompt

    voice_test(certificate, tmp_path, body)


def test_in_datawatch_mode_other_talk_is_a_conversation_with_the_assistant(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        assistant = await add_assistant(hass)
        await choose(hass, assistant.entity_id)
        await visit(hass, satellite, "questions", "what do you think", "and why", "repeat", "stop")
        assert assistant.asked == ["what do you think", "and why"]
        assert assistant.chats[0] == assistant.chats[1], "one conversation per visit"
        assert assistant.discussing == ["0", "0"]
        assert assistant.prompt.startswith(OWN)
        assert satellite.asked[2:] == ["Pat heard 1.", "Pat heard 2.", "Pat heard 2."]
        assert satellite.announced == [CLOSING]
        assert hass.data[DISCUSSING] is None
        assert posts(fake) == []

    voice_test(certificate, tmp_path, body)


def test_the_assistant_never_hears_a_confirmation(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        assistant = await add_assistant(hass)
        await choose(hass, assistant.entity_id)
        await visit(
            hass, satellite, "questions", "option two", "please send that", "confirm answer",
            "stop",
        )  # fmt: skip
        assert assistant.asked == []
        assert fake.answers == [("0", {"surface": "comm:voice", "chosen_option_id": "no"})]

    voice_test(certificate, tmp_path, body)


def test_if_the_assistant_fails_it_is_said(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        (entry,) = hass.config_entries.async_entries(DOMAIN)
        hass.config_entries.async_update_entry(entry, options={CONF_ASSISTANT: "conversation.gone"})
        await visit(hass, satellite, "tell me a story", "stop")
        assert satellite.asked[-1] == "Your assistant didn't answer. Try again, or say stop."

    voice_test(certificate, tmp_path, body)


async def call(hass: HomeAssistant, tool: str, **args: Any) -> tuple[dict[str, Any], bool]:
    """Use a tool the way an AI assistant does."""
    context = llm.LLMContext(
        platform="test", context=Context(), language="en", assistant="conversation", device_id=None
    )
    api = await llm.async_get_api(hass, llm.LLM_API_ASSIST, context)
    result: Any = await api.async_call_tool(llm.ToolInput(f"datawatch__{tool}", args))
    if isinstance(result, llm.ToolResult):
        return dict(result.data), result.error
    return dict(result), False


def test_the_tools_read_datawatch_and_only_read(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await choose(hass, "conversation.home_assistant")
        status, _ = await call(hass, "status")
        assert status["new_work_paused"] is True
        assert status["all_projects"]["open_questions"] == 4
        assert "project" not in status
        status, _ = await call(hass, "status", project="oak")
        assert status["project"]["name"] == "oak"
        status, _ = await call(hass, "status", project="nowhere")
        assert status["note"] == "There is no project named nowhere."

        projects, _ = await call(hass, "projects")
        assert projects == {"projects": ["elm", "oak"], "focus": None}

        fake.records = [
            made_up_question(str(n), f"Made-up question {n}. " + "long " * 100) for n in range(12)
        ] + [made_up_question("boss", "From the boss", asker_kind="supervisor")]
        listed, _ = await call(hass, "questions")
        assert listed["open"] == 13
        assert len(listed["first_ones"]) == 10
        assert listed["first_ones"][0]["begins"] == "From the boss"
        assert len(listed["first_ones"][1]["begins"]) == 200
        assert "being_discussed" not in listed
        hass.data[DISCUSSING] = "11"
        listed, _ = await call(hass, "questions")
        assert listed["being_discussed"]["number"] == 13
        one, _ = await call(hass, "questions", number=1)
        assert one["question"]["asker_recommends_option"] == 2
        assert one["question"]["options"][0]["choice"] == "Yes, do it"
        none, _ = await call(hass, "questions", number=99)
        assert none["note"] == "There is no question 99."

        found, _ = await call(hass, "search_docs", query="what is a plan")
        assert found["found"] == [
            {"path": "howto/x.md", "anchor": "a", "heading": "H", "excerpt": "E"}
        ]
        page, _ = await call(hass, "read_doc", path="howto/x.md", anchor="a")
        assert len(page["content"]) == 6000 and page["cut_short"] is True
        page, _ = await call(hass, "read_doc", path="howto/x.md")

        assert posts(fake) == []

    voice_test(certificate, tmp_path, body)


def test_tool_problems_are_reported_to_the_assistant(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await choose(hass, "conversation.home_assistant")
        data, failed = await call(hass, "search_docs")
        assert failed and data["error"].startswith("wrong arguments")
        fake.override["/api/projects"] = web.Response(status=500)
        data, failed = await call(hass, "projects")
        assert failed and data["error"].startswith("datawatch could not be read")

    voice_test(certificate, tmp_path, body)
