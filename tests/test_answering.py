"""Reading questions and answering them. Nothing is sent without "confirm answer"."""

from __future__ import annotations

import pytest

from custom_components.datawatch.voice.conversation import Conversation, Needs, Reply
from custom_components.datawatch.voice.model import Snapshot
from custom_components.datawatch.voice.phrases import Kind, parse
from custom_components.datawatch.voice.questions import (
    Option,
    Question,
    explained,
    ordered,
    read_back,
    spoken,
)

OPTIONS = (Option("go", "Go ahead", "It starts now"), Option("wait", "Wait"))
FIRST = Question("q1", "May the made-up job start?", OPTIONS, "supervisor", False, "wait", "Safer")
SECOND = Question("q2", "Keep the made-up branch", OPTIONS, "system")
NOT_SENT = "Your answer was not sent. Closing datawatch."
WAITING = "Not sent yet. Say confirm answer, or cancel."


def reading(*questions: Question, assistant: bool = False) -> Conversation:
    conversation = Conversation(assistant=assistant)
    conversation.enter()
    conversation.hear("questions", None, list(questions or (FIRST, SECOND)))
    return conversation


def say(conversation: Conversation, words: str) -> Reply:
    return conversation.hear(words, None)


def test_the_supervisor_comes_first_and_blocking_first_in_each_group() -> None:
    a = Question("a", "a", asker_kind="system")
    b = Question("b", "b", asker_kind="supervisor")
    c = Question("c", "c", asker_kind="system", blocking=True)
    d = Question("d", "d", asker_kind="supervisor", blocking=True)
    e = Question("e", "e", asker_kind="supervisor")
    assert [q.id for q in ordered([a, b, c, d, e])] == ["d", "b", "e", "c", "a"]


def test_a_question_is_read_in_full_with_its_options() -> None:
    conversation = Conversation()
    conversation.enter()
    reply = conversation.hear("what is the first question", None, [SECOND, FIRST])
    assert (
        reply.text
        == spoken(FIRST, 1, 2)
        == (
            "Question 1 of 2, from the supervisor. May the made-up job start? "
            "Option 1: Go ahead. Option 2: Wait. The asker recommends option 2. "
            "Say option and a number, my answer, more detail, or next question."
        )
    )
    assert conversation.current_question == FIRST


def test_a_blocking_question_says_so() -> None:
    blocking = Question("b", "Stop", (), "system", True)
    assert spoken(blocking, 1, 1).startswith(
        "Question 1 of 1, from datawatch. It is blocking work. Stop."
    )


@pytest.mark.parametrize("words", ["next question", "next", "more", "skip"])
def test_moving_through_the_questions(words: str) -> None:
    conversation = reading()
    assert say(conversation, words).text == spoken(SECOND, 2, 2)
    assert say(conversation, words).text == "That is the last question."
    assert conversation.current_question is None


def test_more_detail_gives_the_tradeoffs_without_reading_datawatch() -> None:
    conversation = reading()
    assert conversation.needs("more detail") is Needs.NOTHING
    assert (
        say(conversation, "more detail").text
        == explained(FIRST)
        == ("Option 1: It starts now. Why the asker recommends it: Safer.")
    )
    assert explained(Question("x", "x")) == "This question has no more detail."


def test_status_leaves_the_questions() -> None:
    conversation = reading()
    conversation.hear("status", Snapshot())
    assert conversation.current_question is None
    assert conversation.needs("more detail") is Needs.SNAPSHOT


def test_no_questions_and_unreachable() -> None:
    conversation = Conversation()
    conversation.enter()
    assert conversation.needs("questions") is Needs.QUESTIONS
    assert conversation.hear("questions", None, []).text == "There are no open questions."
    assert conversation.hear("questions", None, None).text.startswith("I can't reach")


@pytest.mark.parametrize("words", ["next question", "option 1", "my answer", "my answer is fine"])
def test_answering_needs_a_question_first(words: str) -> None:
    conversation = Conversation()
    conversation.enter()
    reply = conversation.hear(words, None)
    assert reply.text == "I haven't read a question yet. Say questions."
    assert reply.send is None


@pytest.mark.parametrize(
    "words", ["option one", "Option 1.", "answer one", "answer option one", "choose 1", "one"]
)
def test_choosing_reads_back_and_sends_nothing(words: str) -> None:
    conversation = reading()
    reply = say(conversation, words)
    assert reply.send is None
    assert reply.text == (
        "Not sent yet. The question begins: May the made-up job start? "
        "Your choice: option 1, Go ahead. Say confirm answer to send it, or cancel."
    )


def test_only_confirm_answer_sends() -> None:
    conversation = reading()
    say(conversation, "option two")
    reply = say(conversation, "Confirm answer.")
    assert reply.send is not None
    assert (reply.send.question, reply.send.option, reply.send.quote) == (FIRST, OPTIONS[1], None)
    assert say(conversation, "confirm answer") == Reply("There is no answer waiting.")


@pytest.mark.parametrize(
    "words",
    ["yes", "confirm", "ok", "send it", "yes confirm answer now", "status", "questions", "next"],
)
def test_nothing_else_sends(words: str) -> None:
    conversation = reading()
    say(conversation, "option one")
    reply = say(conversation, words)
    assert reply.send is None
    assert reply.text == WAITING
    assert conversation.needs(words) is Needs.NOTHING


def test_cancel_drops_the_answer() -> None:
    conversation = reading()
    say(conversation, "option one")
    assert say(conversation, "cancel").text == "Cancelled. Nothing was sent."
    assert say(conversation, "confirm answer").send is None


def test_my_own_words_are_kept_exactly_as_heard() -> None:
    conversation = reading()
    reply = say(conversation, "My answer is: wait until Friday, please.")
    assert "Your words: wait until Friday, please." in reply.text
    sent = say(conversation, "confirm answer").send
    assert sent is not None
    assert (sent.option, sent.quote) == (None, "wait until Friday, please.")


def test_dictating_takes_the_whole_next_turn() -> None:
    conversation = reading()
    assert say(conversation, "my answer").text == "Go ahead. Say your answer, or cancel."
    assert conversation.needs("status") is Needs.NOTHING
    assert (
        "Your words: Status can stay as it is."
        in say(conversation, "Status can stay as it is.").text
    )
    sent = say(conversation, "confirm answer").send
    assert sent is not None and sent.quote == "Status can stay as it is."


def test_confirm_said_while_dictating_is_words_not_a_send() -> None:
    conversation = reading()
    say(conversation, "my answer")
    assert say(conversation, "confirm answer").send is None


def test_cancel_while_dictating() -> None:
    conversation = reading()
    say(conversation, "my answer")
    assert say(conversation, "cancel").text == "Cancelled. Nothing was sent."
    assert say(conversation, "confirm answer").send is None


def test_a_choice_and_words_can_be_sent_together_and_changed() -> None:
    conversation = reading()
    say(conversation, "option one")
    say(conversation, "my answer is but only tonight")
    say(conversation, "option two")
    say(conversation, "my answer")
    say(conversation, "tomorrow instead")
    sent = say(conversation, "confirm answer").send
    assert sent is not None
    assert (sent.option, sent.quote) == (OPTIONS[1], "tomorrow instead")


def test_an_option_that_does_not_exist() -> None:
    conversation = reading()
    assert say(conversation, "option five").text == "There is no option 5."
    assert say(conversation, "confirm answer").send is None


def test_repeat_reads_the_pending_answer_again() -> None:
    conversation = reading()
    first = say(conversation, "option one").text
    assert say(conversation, "repeat").text == first


@pytest.mark.parametrize("leave", [["stop"], [None, None], ["um", "uh", "hm"]])
def test_leaving_with_an_answer_waiting_says_it_was_not_sent(leave: list[str | None]) -> None:
    conversation = reading()
    say(conversation, "option one")
    for words in leave:
        reply = conversation.silence() if words is None else say(conversation, words)
    assert reply.ends and reply.send is None
    assert reply.text.startswith("Your answer was not sent.")


def test_a_new_visit_forgets_a_pending_answer() -> None:
    conversation = reading()
    say(conversation, "option one")
    conversation.enter()
    assert say(conversation, "confirm answer").send is None


def test_with_an_assistant_other_talk_is_passed_on() -> None:
    conversation = reading(assistant=True)
    reply = say(conversation, "What do you think about this one?")
    assert reply == Reply("", forward="What do you think about this one?")
    assert conversation.said("It seems fine.") == Reply("It seems fine.")
    assert say(conversation, "repeat").text == "It seems fine."


def test_the_assistant_never_hears_commands_or_a_pending_answer() -> None:
    conversation = reading(assistant=True)
    say(conversation, "option one")
    assert say(conversation, "tell the assistant to send it").forward is None
    assert say(conversation, "confirm answer").send is not None


def test_a_long_question_is_shortened_only_in_the_read_back() -> None:
    long = Question("l", "word " * 100, OPTIONS)
    conversation = reading(long)
    assert long.text.strip() in say(conversation, "repeat").text
    reply = say(conversation, "option one").text
    assert len(reply) < 320


def test_outcomes_can_be_repeated() -> None:
    conversation = reading()
    assert conversation.sent("Answer sent.") == Reply("Answer sent.")
    assert say(conversation, "repeat").text == "Answer sent."


@pytest.mark.parametrize(
    ("heard", "kind"),
    [
        ("What's the first question?", Kind.QUESTIONS),
        ("Any questions?", Kind.QUESTIONS),
        ("Option to", Kind.CHOOSE),
        ("answer for", Kind.CHOOSE),
        ("My answer.", Kind.OWN_WORDS),
        ("confirm my answer", Kind.CONFIRM),
        ("choose wisely", Kind.UNKNOWN),
    ],
)
def test_what_speech_to_text_might_write(heard: str, kind: Kind) -> None:
    assert parse(heard).kind is kind


def test_read_back_without_an_option() -> None:
    from custom_components.datawatch.voice.questions import Draft

    assert "Your choice" not in read_back(Draft(FIRST, quote="no"))
