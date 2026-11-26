"""Focus on any item, its questions and details, and going back. Data is made up."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from fake_datawatch import Fake, made_up_question
from homeassistant.core import HomeAssistant
from test_assistant import call, choose, posts
from test_voice import Certificate, FakeSatellite, visit, voice_test

from custom_components.datawatch.const import FOCUS
from custom_components.datawatch.voice import items, reports, work
from custom_components.datawatch.voice.automata import Automaton, Task
from custom_components.datawatch.voice.conversation import Conversation, Needs
from custom_components.datawatch.voice.items import GONE, Card, Decision, Item
from custom_components.datawatch.voice.model import Snapshot
from custom_components.datawatch.voice.phrases import Command, Kind, parse
from custom_components.datawatch.voice.questions import Option, Question
from custom_components.datawatch.voice.reports import Child, Report

FENCE = Automaton(
    "a2",
    "Paint the fence",
    "blocked",
    "oak",
    tasks=(Task("Buy paint", "completed", id="t1"), Task("Paint it", "blocked", id="t2")),
)
ROOTS = Item("plan", "p1", "Roots", "oak")
ERRAND = Item("automaton", "a9", "Run the errand")


def card(text: str = "Its status.", **more: object) -> Card:
    return Card(text, f"{text} In detail.", "Its history.", **more)  # type: ignore[arg-type]


def listing(*found: Item) -> Report:
    lines = tuple(f"{n}, {item.title}." for n, item in enumerate(found, start=1))
    return Report(f"{len(found)} things.", lines, found)


def chosen_fence() -> Conversation:
    """Heard the attention list, then chose the fence."""
    conversation = Conversation()
    conversation.enter()
    conversation.hear("attention", None, report=listing(Item("automaton", "a2", "Paint the fence")))
    conversation.hear("one", None, automaton=FENCE)
    return conversation


def asked(text: str, **links: object) -> Question:
    return Question(text, text, (Option("y", "Yes"),), **links)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("heard", "command"),
    [
        ("Set it.", Command(Kind.SET_THIS)),
        ("Go back", Command(Kind.GO_BACK)),
        ("go up", Command(Kind.GO_BACK)),
        ("its questions", Command(Kind.ITS_QUESTIONS)),
        ("Questions for two", Command(Kind.ITS_QUESTIONS, number=2)),
        ("all questions", Command(Kind.ALL_QUESTIONS)),
        ("history", Command(Kind.HISTORY)),
        ("automata", Command(Kind.AUTOMATA)),
        ("set plan two", Command(Kind.SET_NUMBER, number=2, item="plan")),
        (
            "set the automaton roof repair",
            Command(Kind.SET_NAME, name="roof repair", item="automaton"),
        ),
        ("set number two", Command(Kind.SET_NUMBER, number=2)),
        ("set oak", Command(Kind.SET_NAME, name="oak")),
    ],
)
def test_ways_of_asking(heard: str, command: Command) -> None:
    assert parse(heard) == command


def test_choosing_then_setting_an_automaton_focuses_it_and_its_project() -> None:
    conversation = chosen_fence()
    assert conversation.needs("set it") is Needs.CARD
    assert conversation.wanted_card("set it") == Item("automaton", "a2", "Paint the fence")
    reply = conversation.hear("set it", None, card=card(project="oak"))
    assert reply.text == "Focus: project oak, automaton Paint the fence."
    assert conversation.focus == "oak"
    assert [item.id for item in conversation.path] == ["a2"]
    assert conversation.hear("where am i", Snapshot(projects=("oak",))).text == reply.text
    conversation.enter()
    assert conversation.hear("repeat", None).text == f"Datawatch activated. {reply.text}"


def test_a_line_can_be_set_by_number_or_by_name_without_choosing_it_first() -> None:
    for words in ("set two", "set automaton two", "set errand"):
        conversation = Conversation()
        other = Item("automaton", "a1", "Mend the gate")
        conversation.hear("attention", None, report=listing(other, ERRAND))
        assert conversation.wanted_card(words) == ERRAND, words
        conversation.hear(words, None, card=card())
        assert conversation.path == (ERRAND,)


def test_a_number_not_heard_or_of_another_kind_is_not_set() -> None:
    conversation = Conversation()
    conversation.hear("attention", None, report=listing(ERRAND))
    assert conversation.wanted_card("set four") is None
    assert conversation.hear("set four", None).text.startswith("I haven't read a number 4.")
    assert conversation.wanted_card("set plan one") is None
    wrong = conversation.hear("set plan one", None).text
    assert wrong == "Number 1 is the automaton Run the errand. Say set 1."
    assert conversation.path == ()
    assert conversation.hear("set it", None).text.startswith("Choose something first")


def test_several_names_that_fit_are_offered_as_a_numbered_choice() -> None:
    conversation = Conversation()
    gates = (Item("automaton", "g1", "Mend gate"), Item("automaton", "g2", "Paint gate"))
    conversation.hear("attention", None, report=listing(*gates))
    assert conversation.needs("set gate") is Needs.NOTHING
    text = conversation.hear("set gate", None).text
    assert text.startswith("I found 2 matches. Say set and a number. 1, automaton Mend gate.")
    conversation.hear("set two", None, card=card())
    assert conversation.path == (gates[1],)


def test_status_detail_and_history_follow_the_focus() -> None:
    conversation = Conversation("oak", path=(ROOTS,))
    for words in ("status", "more detail", "history", "why"):
        assert conversation.needs(words) is Needs.CARD, words
        assert conversation.wanted_card(words) == ROOTS
    status = conversation.hear("status", None, card=card()).text
    assert status == "Its status. Say more detail for more."
    assert conversation.hear("more detail", None, card=card()).text == "Its status. In detail."
    assert conversation.hear("history", None, card=card()).text == "Its history."
    assert conversation.hear("status", None).text.startswith("I can't reach datawatch")


def test_a_focused_automaton_needs_no_number() -> None:
    conversation = Conversation(path=(Item("automaton", "a2", "Paint the fence"),))
    for words in ("why", "tasks", "progress", "results"):
        assert conversation.needs(words) is Needs.AUTOMATON, words
        assert conversation.wanted_automaton(words) == "a2"


def test_tasks_can_be_chosen_set_and_left() -> None:
    from custom_components.datawatch.voice import automata

    conversation = chosen_fence()
    conversation.hear("tasks", None, automaton=FENCE)
    detail = conversation.hear("two", None).text
    assert detail == "Task Paint it: blocked. In the automaton Paint the fence."
    reply = conversation.hear("set it", None, card=card(project="oak"))
    assert reply.text == "Focus: project oak, automaton Paint the fence, task Paint it."
    assert [item.kind for item in conversation.path] == ["automaton", "task"]
    assert conversation.path[1].parent == "a2"
    back = conversation.hear("go back", None).text
    assert back == f"Back. No focus. Showing everything. {detail}"
    assert conversation.path == ()
    assert automata.tasks(FENCE).under == Item("automaton", "a2", "Paint the fence")


def test_tasks_without_ids_still_leave_the_automaton_chosen() -> None:
    bare = Automaton("a2", "Paint the fence", "blocked", tasks=(Task("Buy paint"),))
    conversation = chosen_fence()
    conversation.hear("tasks", None, automaton=bare)
    assert conversation.wanted_automaton("progress") == "a2"


def test_go_back_returns_to_the_previous_question() -> None:
    conversation = Conversation()
    first = conversation.hear("questions", None, [asked("First?"), asked("Second?")]).text
    second = conversation.hear("next question", None).text
    assert "Second?" in second
    assert conversation.hear("go back", None).text == f"Back. {first}"
    assert conversation.current_question is not None
    assert conversation.current_question.text == "First?"


def test_go_back_from_the_end_returns_to_the_last_question() -> None:
    conversation = Conversation()
    only = conversation.hear("questions", None, [asked("Only?")]).text
    assert conversation.hear("next question", None).text == "That is the last question."
    assert conversation.hear("back", None).text == f"Back. {only}"


def test_go_back_goes_back_up_out_of_a_project() -> None:
    conversation = Conversation()
    projects = Snapshot(projects=("elm", "oak"))
    listed = conversation.hear("list projects", projects).text
    assert conversation.hear("set oak", projects).text == "Focus: project oak."
    back = conversation.hear("go back", None).text
    assert back == f"Back. No focus. Showing everything. {listed}"
    assert conversation.focus is None
    assert conversation.hear("go back", None).text.startswith("Back.")


def test_with_no_earlier_step_go_back_moves_the_focus_up_one_level() -> None:
    task = Item("task", "t1", "Buy paint", "a2")
    conversation = Conversation("oak", path=(ROOTS, task))
    conversation.enter()
    assert conversation.hear("go back", None).text == "Back. Focus: project oak, plan Roots."
    assert conversation.hear("go back", None).text == "Back. Focus: project oak."
    assert conversation.hear("go back", None).text == "Back. No focus. Showing everything."
    assert conversation.hear("go back", None).text == "There is nothing to go back to."


def test_hearing_more_of_a_list_is_not_a_step() -> None:
    conversation = Conversation()
    found = tuple(Item("automaton", str(n), f"Thing {n}") for n in range(5))
    conversation.enter()
    conversation.hear("attention", None, report=listing(*found))
    page_two = conversation.hear("more", None).text
    conversation.hear("two", None, automaton=FENCE)
    assert conversation.hear("go back", None).text == f"Back. {page_two}"
    assert conversation.wanted_automaton("five") == "4"


def test_going_back_never_sends_and_drops_a_waiting_answer() -> None:
    conversation = Conversation()
    conversation.hear("questions", None, [asked("First?")])
    conversation.hear("option one", None)
    reply = conversation.hear("go back", None)
    assert reply.text == "Cancelled. Nothing was sent." and reply.send is None
    assert conversation.hear("confirm answer", None).send is None
    conversation.hear("my answer", None)
    assert conversation.hear("go back", None).text == "Cancelled. Nothing was sent."


def test_a_focus_narrows_questions_to_what_datawatch_links_to_it() -> None:
    conversation = Conversation(path=(Item("automaton", "a2", "Paint the fence"),))
    everything = [
        asked("Other?"),
        asked("Mine?", automaton_id="a2"),
        asked("Tagged?", tags=("automaton:a2",)),
    ]
    assert conversation.needs("questions") is Needs.QUESTIONS
    assert conversation.wanted_card("questions") is None
    text = conversation.hear("questions", None, everything).text
    assert text.startswith("For the automaton Paint the fence. Question 1 of 2")
    assert "Mine?" in text and "Other?" not in text
    assert "Question 1 of 3" in conversation.hear("all questions", None, everything).text


def test_no_linked_questions_says_how_many_there_are_in_all() -> None:
    conversation = Conversation(path=(Item("task", "t1", "Buy paint", "a2"),))
    text = conversation.hear("questions", None, [asked("Other?")]).text
    assert text == (
        "datawatch links no open questions to the task Buy paint. There is 1 open question "
        "in all. Say all questions."
    )
    assert conversation.current_question is None


@pytest.mark.parametrize(
    ("item", "links"),
    [
        (Item("task", "t1", "T", "a2"), {"task_id": "t1"}),
        (Item("session", "s1", "S"), {"asked_by": "s1"}),
        (ROOTS, {"automaton_id": "a7"}),
        (Item("automation", "m1", "M"), {"tags": ("automaton:a7",)}),
    ],
)
def test_how_questions_are_linked(item: Item, links: dict[str, object]) -> None:
    conversation = Conversation(path=(item,))
    holder = card(automata=frozenset({"a7"})) if item.kind in ("plan", "automation") else None
    assert conversation.wanted_card("questions") == (item if holder else None)
    text = conversation.hear(
        "questions", None, [asked("Other?"), asked("Mine?", **links)], card=holder
    ).text
    assert "Question 1 of 1" in text and "Mine?" in text


def test_a_chosen_item_does_not_narrow_plain_questions() -> None:
    conversation = chosen_fence()
    everything = [asked("Other?"), asked("Mine?", automaton_id="a2")]
    assert "Question 1 of 2" in conversation.hear("questions", None, everything).text
    conversation = chosen_fence()
    its = conversation.hear("its questions", None, everything).text
    assert "Question 1 of 1" in its and "Mine?" in its


def test_its_questions_with_nothing_chosen_does_not_read_them_all() -> None:
    text = Conversation().hear("its questions", None, [asked("Other?")]).text
    assert text == "Choose something first, then say its questions. Or say questions."


def test_a_focused_item_datawatch_no_longer_has_is_dropped_with_what_is_inside_it() -> None:
    task = Item("task", "t1", "Buy paint", "a2")
    conversation = Conversation("oak", path=(ROOTS, task))
    text = conversation.hear("status", None, card=GONE).text
    assert text == (
        "datawatch no longer has the task Buy paint, so I moved your focus up. "
        "Focus: project oak, plan Roots."
    )


def test_listing_inside_a_plan_then_setting_one_keeps_the_plan_above_it() -> None:
    conversation = Conversation("oak", path=(ROOTS,))
    assert conversation.needs("automata") is Needs.CHILDREN
    assert conversation.wanted_children("automata") == (ROOTS, "automaton")
    assert conversation.wanted_children("tasks") == (ROOTS, "task")
    inside = reports.children(ROOTS, "automaton", [Child("a7", "Dig", "draft")], 4)
    assert inside.summary == "The plan Roots has 4 automata. I can read the first 1."
    conversation.hear("automata", None, report=inside)
    conversation.hear("set one", None, card=card(project="oak"))
    assert [item.id for item in conversation.path] == ["p1", "a7"]


def test_things_with_nothing_inside_say_what_to_do() -> None:
    conversation = Conversation()
    assert conversation.hear("automata", None).text.startswith("Say plans or automations")
    assert conversation.hear("history", None).text.startswith("Choose something first")
    task = Conversation(path=(Item("task", "t1", "Buy paint", "a2"),))
    assert task.hear("tasks", None).text == "Tasks are listed for a plan or an automaton."


def test_a_name_not_in_the_list_is_searched_for() -> None:
    conversation = Conversation("oak")
    assert conversation.needs("set plan roots") is Needs.FIND_ITEM
    assert conversation.wanted_item_search("set plan roots") == ("plan", "roots")
    found = listing(ROOTS)
    conversation.hear("set plan roots", None, report=found, card=card(project="oak"))
    assert conversation.path == (ROOTS,)
    nothing = conversation.hear("set plan trunk", None, report=found).text
    assert nothing == "I couldn't find a plan matching trunk."
    why = conversation.hear("set task x", None, report=Report("Set a plan first.")).text
    assert why == "Set a plan first."


def test_setting_a_project_or_unsetting_clears_the_items() -> None:
    conversation = Conversation("oak", path=(ROOTS,))
    projects = Snapshot(projects=("elm", "oak"))
    assert conversation.hear("set project elm", projects).text == "Focus: project elm."
    assert conversation.path == ()
    conversation = Conversation("oak", path=(ROOTS,))
    assert conversation.hear("unset", None).text.startswith("Focus cleared.")
    assert (conversation.focus, conversation.path) == (None, ())


def test_saved_focus_that_is_not_one_is_ignored() -> None:
    path = (ROOTS, Item("task", "t1", "Buy paint", "a2"))
    assert items.restored(items.stored(path)) == path
    for junk in (None, "x", [1], [{"kind": "castle"}], [{"kind": "plan", "id": 3}]):
        assert items.restored(junk) == ()


def test_history_is_newest_first_and_members_without_status_are_only_counted() -> None:
    text = items.history(
        "Fence", [Decision("made", "me"), Decision("stage_failed", note="n " * 300)]
    )
    assert text.startswith("Fence has 2 entries. The latest: 1, stage failed: n n")
    assert "2, made, by me." in text and len(text) < 320
    assert items.history("Fence", []) == "datawatch has no history for Fence."
    assert items.member_summary(["", "completed"]) == "2 members"
    assert items.member_summary(["completed", "running", "completed"]) == (
        "3 members: 2 completed and 1 running"
    )


def test_sessions_in_a_focused_automaton_are_named_as_such() -> None:
    report = work.sessions([("running", 0)], [], "oak", datetime.now(UTC), ERRAND)
    assert report.summary == "The automaton Run the errand: sessions, 0 running."


def test_the_focus_is_saved_between_visits(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await visit(hass, satellite, "what needs my attention", "one", "set it", "stop")
        assert [item.id for item in hass.data[FOCUS].path] == ["a2"]
        assert hass.data[FOCUS].project == "oak"
        satellite.asked.clear()
        await visit(hass, satellite, "status", "why", "stop")
        assert satellite.asked[0] == (
            "Datawatch activated. Focus: project oak, automaton Paint the made-up fence."
        )
        assert satellite.asked[1].startswith("Automaton Paint the made-up fence: blocked.")
        assert "the made-up paint ran out" in satellite.asked[2]
        assert posts(fake) == []

    voice_test(certificate, tmp_path, body)


def _said(satellite: FakeSatellite) -> list[str]:
    return satellite.asked[1:]


def test_voice_through_a_plan_to_its_questions_and_back(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        fake.records = [
            made_up_question("q1", "A made-up other question?"),
            made_up_question("q2", "A made-up fence question?") | {"prd_id": "a2"},
        ]
        await visit(
            hass, satellite,
            "set oak", "plans", "set one", "status", "more detail", "history", "questions",
            "automata", "one", "go back", "tasks", "one", "set it", "status", "history",
            "go back", "where am i", "stop",
        )  # fmt: skip
        said = _said(satellite)
        assert said[1].startswith("Project oak has 2 current plans.")
        assert said[2] == "Focus: project oak, plan Roots."
        assert said[3] == "Plan Roots: in progress. 2 of 5 automata done. Say more detail for more."
        assert "Its goal: Made-up goal for Roots." in said[4]
        assert said[4].endswith("Next: Paint the made-up fence.")
        assert said[5] == "datawatch gives no history for a plan."
        assert said[6].startswith("For the plan Roots. Question 1 of 1")
        assert "fence question" in said[6] and "other question" not in said[6]
        assert said[7].startswith(
            "The plan Roots has 1 automaton. 1, Paint the made-up fence: blocked."
        )
        assert said[8].startswith("Paint the made-up fence: blocked.")
        assert said[9] == f"Back. {said[7]}"
        assert said[10].startswith("The plan Roots has 1 task. 1, Paint it: blocked.")
        task = "Task Paint it: blocked. In the automaton Paint the made-up fence."
        assert said[11] == task
        assert said[12] == "Focus: project oak, plan Roots, task Paint it."
        assert said[13] == task, "no offer of more detail when there is none"
        assert said[14].startswith("datawatch records history for an automaton")
        assert said[15] == f"Back. Focus: project oak, plan Roots. {task}"
        assert said[16] == "Focus: project oak, plan Roots."
        assert posts(fake) == []

    voice_test(certificate, tmp_path, body)


def test_voice_through_an_automation_and_its_sessions(
    certificate: Certificate, tmp_path: Path
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        fake.automations = [fake.automation_records["m1"]]
        await visit(
            hass, satellite,
            "automations", "set one", "history", "automata", "go back", "sessions",
            "set session helper", "status", "history", "stop",
        )  # fmt: skip
        said = _said(satellite)
        assert said[1] == "Focus: automation Gamma."
        assert said[2].startswith(
            "Gamma has 2 entries. The latest: 1, member blocked: The made-up paint ran out."
        )
        assert said[3].startswith(
            "The automation Gamma has 2 automata. 1, Paint the made-up fence: blocked. "
            "2, Build the made-up shed: completed."
        )
        assert said[5].startswith("The automation Gamma: sessions,")
        filtered = [
            q for _, path, q, _ in fake.seen if path == "/api/sessions" and "automation" in q
        ]
        assert filtered and all(q["automation"] == "m1" and "project" not in q for q in filtered)
        assert said[6] == "Focus: project oak, automation Gamma, session Made-up helper."
        assert said[7].startswith("Session named Made-up helper: waiting for input.")
        assert "raw terminal text" not in " ".join(said)
        assert said[8].startswith("I can't read a session's history")
        assert posts(fake) == []

    voice_test(certificate, tmp_path, body)


def test_voice_says_when_a_focused_item_has_gone(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await hass.data[FOCUS].async_set("oak", (Item("automation", "gone1", "Lost"),))
        await visit(hass, satellite, "automata", "status", "stop")
        said = _said(satellite)
        assert said[0].startswith("datawatch no longer has the automation Lost.")
        assert said[1].startswith("datawatch no longer has the automation Lost, so I moved")
        assert hass.data[FOCUS].path == ()

    voice_test(certificate, tmp_path, body)


def test_the_assistant_is_told_what_is_focused(certificate: Certificate, tmp_path: Path) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        await hass.data[FOCUS].async_set("oak", (ROOTS,))
        await choose(hass, "conversation.home_assistant")
        result, _ = await call(hass, "projects")
        assert result["focus"] == "oak"
        assert result["focused_on"] == "project oak, plan Roots"

    voice_test(certificate, tmp_path, body)


def test_asking_about_the_focused_item_is_not_a_step() -> None:
    conversation = Conversation(path=(Item("automaton", "a2", "Paint the fence"),))
    conversation.enter()
    for words in ("why", "progress", "why"):
        conversation.hear(words, None, automaton=FENCE)
    conversation.hear("history", None, card=card())
    assert conversation.hear("go back", None).text == "Back. No focus. Showing everything."


@pytest.mark.parametrize(
    ("before", "words", "reply"),
    [
        (("set oak",), "set plan leaves", "Focus: project oak, plan Leaves."),
        ((), "set plan leaves", "Set a project first: say list projects"),
        ((), "set automation gamma", "Focus: automation Gamma."),
        ((), "set automation trumpet", "I couldn't find an automation matching trumpet."),
        ((), "set automaton made up tree", "Focus: project elm, automaton Plant the made-up tree."),
        ((), "set automaton submarine", "I couldn't find submarine among"),
        ((), "set session runner", "Focus: project elm, session Made-up runner."),
        ((), "set task roof", "Set a plan or an automaton first, then set the task."),
        (
            ("set automaton made up fence",),
            "set task tidy",
            "Focus: project oak, automaton Paint the made-up fence, task Tidy up.",
        ),
        (
            ("set oak", "set plan roots"),
            "set task paint",
            "Focus: project oak, plan Roots, task Paint it.",
        ),
    ],
)
def test_voice_setting_something_by_name_alone(
    certificate: Certificate,
    tmp_path: Path,
    before: tuple[str, ...],
    words: str,
    reply: str,
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        fake.automations = [fake.automation_records["m1"]]
        fake.automata["f1"]["project"] = "oak"
        fake.automata["h1"]["project"] = "elm"
        await visit(hass, satellite, *before, words, "stop")
        assert _said(satellite)[len(before)].startswith(reply)
        assert posts(fake) == []

    voice_test(certificate, tmp_path, body)


def test_voice_titles_the_plan_list_leaves_blank_are_read_from_the_automaton(
    certificate: Certificate, tmp_path: Path
) -> None:
    """datawatch's plan list leaves some titles empty that the automaton itself has."""

    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        fake.plan_automata = [
            {"id": "a2", "title": "", "state": "blocked"},
            {"id": "h1", "state": "draft"},
            {"id": "n1", "title": "", "state": "draft"},
        ]
        fake.automata["n1"] = {"id": "n1", "status": "draft"}
        await visit(hass, satellite, "set oak", "plans", "set one", "automata", "stop")
        said = _said(satellite)[3]
        assert (
            "1, Paint the made-up fence: blocked. 2, Plant the made-up tree: draft. "
            "3, untitled: draft."
        ) in said

    voice_test(certificate, tmp_path, body)


def test_go_back_does_not_say_the_focus_twice() -> None:
    conversation = Conversation()
    projects = Snapshot(projects=("oak",))
    conversation.enter()
    conversation.hear("set oak", projects)
    conversation.hear("unset", None)
    text = conversation.hear("go back", None).text
    assert text == "Back. Focus: project oak."


@pytest.mark.parametrize("status", ["completed", "archived", "blocked"])
def test_only_unfinished_work_is_asked_why_it_is_not_moving(
    certificate: Certificate, tmp_path: Path, status: str
) -> None:
    async def body(hass: HomeAssistant, satellite: FakeSatellite, fake: Fake) -> None:
        fake.automata["a2"]["status"] = status
        fake.automata["a2"]["blocked_reason"] = ""
        fake.automata["a2"]["stories"] = []
        await visit(hass, satellite, "attention", "one", "set it", "more detail", "stop")
        assert ("gives no reason" in _said(satellite)[3]) is (status == "blocked")

    voice_test(certificate, tmp_path, body)
