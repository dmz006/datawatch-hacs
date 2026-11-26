"""The datawatch-mode conversation. All data here is made up."""

from __future__ import annotations

from custom_components.datawatch.voice.conversation import Conversation, Reply
from custom_components.datawatch.voice.model import Item, Snapshot

PROJECTS = ("walnut", "maple-syrup", "Birch", "maple-leaf", "oak", "cedar", "elm")


def snapshot(*, paused: bool = False) -> Snapshot:
    return Snapshot(
        paused=paused,
        projects=PROJECTS,
        questions=(Item("oak"), Item("oak"), Item("elm"), Item(None)),
        waiting=(Item("oak"), Item("elm"), Item("elm")),
        running=(Item("oak"),),
        failed=(Item("elm"), Item(None)),
        held=(Item("elm"),),
    )


def start(focus: str | None = None) -> Conversation:
    conversation = Conversation(focus=focus)
    conversation.enter()
    return conversation


def say(conversation: Conversation, words: str, **kwargs: bool) -> Reply:
    return conversation.hear(words, snapshot(**kwargs))


def test_entering_without_a_focus() -> None:
    reply = Conversation().enter()
    assert reply == Reply("Datawatch.", ends=False)


def test_entering_says_the_focus_first() -> None:
    assert Conversation(focus="oak").enter().text == "Datawatch. Focus: project oak."


def test_status_for_everything() -> None:
    text = say(start(), "status").text
    assert text == (
        "4 open questions, 3 sessions waiting for input and 1 running. Say more detail for more."
    )


def test_status_says_when_new_work_is_paused() -> None:
    assert say(start(), "status", paused=True).text.startswith("New work is paused. ")


def test_status_with_a_focus_counts_inside_and_says_what_is_outside_or_unlinked() -> None:
    text = say(start("oak"), "status").text
    assert text == (
        "In project oak: 2 open questions, 1 session waiting for input and 1 running. "
        "Elsewhere: 1 open question, 2 sessions waiting for input and 0 running. "
        "Not linked: 1 open question. Say more detail for more."
    )


def test_more_detail() -> None:
    assert say(start(), "more detail").text == "1 held or blocked item and 2 failed sessions."


def test_more_detail_with_a_focus() -> None:
    assert say(start("elm"), "more detail").text == (
        "In project elm: 1 held or blocked item and 1 failed session. Not linked: 1 failed session."
    )


def test_list_reads_the_count_then_three_in_alphabetical_order() -> None:
    assert say(start(), "list projects").text == (
        "7 projects. 1, Birch. 2, cedar. 3, elm. Say more, or set and a number or name."
    )


def test_more_continues_the_numbers_and_ends_cleanly() -> None:
    conversation = start()
    say(conversation, "list projects")
    assert say(conversation, "more").text.startswith("4, maple-leaf. 5, maple-syrup. 6, oak.")
    assert say(conversation, "more").text == "7, walnut. That is the end of the list."
    assert say(conversation, "more").text == "That is the end of the list."


def test_more_without_a_list() -> None:
    assert say(start(), "more").text == "There is no list yet. Say list projects."


def test_no_projects() -> None:
    reply = start().hear("list projects", Snapshot(projects=()))
    assert reply.text == "There are no projects."


def test_set_by_number_from_any_group_already_heard() -> None:
    conversation = start()
    say(conversation, "list projects")
    say(conversation, "more")
    assert say(conversation, "set two").text == "Focus: project cedar."
    assert conversation.focus == "cedar"


def test_a_number_not_yet_heard_is_refused() -> None:
    conversation = start()
    say(conversation, "list projects")
    assert say(conversation, "set five").text.startswith("I haven't read a number 5.")
    assert conversation.focus is None


def test_set_number_without_a_list() -> None:
    assert say(start(), "set two").text == "There is no list yet. Say list projects."


def test_set_by_full_name_and_by_partial_name() -> None:
    conversation = start()
    assert say(conversation, "set project maple syrup").text == "Focus: project maple-syrup."
    assert say(conversation, "set wal").text == "Focus: project walnut."


def test_several_matches_are_listed_and_the_user_is_asked_which() -> None:
    conversation = start("oak")
    reply = say(conversation, "set maple")
    assert reply.text == "I found 2 matches. 1, maple-leaf. 2, maple-syrup. Which number?"
    assert conversation.focus == "oak"
    assert say(conversation, "two").text == "Focus: project maple-syrup."


def test_a_partial_name_narrows_the_choice() -> None:
    conversation = start()
    say(conversation, "set maple")
    assert say(conversation, "set maple leaf").text == "Focus: project maple-leaf."


def test_unknown_name_changes_nothing() -> None:
    conversation = start("oak")
    assert say(conversation, "set willow").text == (
        "I couldn't find a project matching willow. Say list projects."
    )
    assert conversation.focus == "oak"


def test_a_bare_number_does_nothing_unless_a_choice_was_asked_for() -> None:
    conversation = start()
    say(conversation, "list projects")
    assert say(conversation, "two").text == "Sorry, I didn't get that. Say help."
    assert conversation.focus is None


def test_where_and_unset() -> None:
    conversation = start("oak")
    assert say(conversation, "where am I").text == "Focus: project oak."
    assert say(conversation, "unset").text == "Focus cleared. Now showing everything."
    assert say(conversation, "where am I").text == "No focus. Showing everything."
    assert conversation.focus is None


def test_repeat_says_the_last_reply_again() -> None:
    conversation = start()
    first = say(conversation, "list projects")
    assert say(conversation, "repeat").text == first.text
    assert say(conversation, "repeat").text == first.text


def test_help_names_the_commands() -> None:
    text = say(start(), "help").text
    for word in ("status", "more detail", "list projects", "set", "unset", "repeat", "stop"):
        assert word in text


def test_unclear_speech_changes_nothing() -> None:
    conversation = start("oak")
    reply = say(conversation, "purple monkey")
    assert reply == Reply("Sorry, I didn't get that. Say help.", ends=False)
    assert conversation.focus == "oak"


def test_exit_ends_the_mode_and_keeps_the_focus() -> None:
    conversation = start("oak")
    assert say(conversation, "stop") == Reply("Closing datawatch.", ends=True)
    assert conversation.focus == "oak"


def test_first_silence_asks_once_and_second_ends() -> None:
    conversation = start()
    assert conversation.silence() == Reply("Still there?", ends=False)
    assert conversation.silence() == Reply("Closing datawatch.", ends=True)


def test_speaking_resets_the_silence_count() -> None:
    conversation = start()
    conversation.silence()
    say(conversation, "status")
    assert conversation.silence() == Reply("Still there?", ends=False)


def test_entering_again_resets_silence_and_list() -> None:
    conversation = start()
    say(conversation, "list projects")
    conversation.silence()
    conversation.enter()
    assert conversation.silence().ends is False
    assert say(conversation, "more").text == "There is no list yet. Say list projects."


def test_stay_until_exit_can_be_chosen_later() -> None:
    conversation = Conversation(silences_before_closing=None)
    conversation.enter()
    assert all(not conversation.silence().ends for _ in range(5))


def test_a_focus_on_a_project_that_no_longer_exists_is_said_and_cleared() -> None:
    conversation = start("gone")
    reply = say(conversation, "status")
    assert reply.text.startswith("Project gone no longer exists, so the focus is cleared. ")
    assert conversation.focus is None


def test_paused_with_a_focus_still_says_the_focus_first() -> None:
    text = say(start("oak"), "status", paused=True).text
    assert text.startswith("In project oak: all new work is paused. 2 open questions")
