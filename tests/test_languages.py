"""Voice takes another language from data alone: no change to the code that listens."""

from __future__ import annotations

import ast
import re
from dataclasses import replace
from pathlib import Path

import pytest
from voice_examples import DOCUMENT, EXAMPLES, NOT_CONFIRMING, OPTION_TWO, render, write

from custom_components.datawatch.voice import custom, language
from custom_components.datawatch.voice.actions import title_of
from custom_components.datawatch.voice.conversation import Conversation
from custom_components.datawatch.voice.lang import en
from custom_components.datawatch.voice.names import match_names
from custom_components.datawatch.voice.phrases import Command, Kind, parse
from custom_components.datawatch.voice.questions import Option, Question

VOICE = Path(__file__).parents[1] / "custom_components" / "datawatch" / "voice"

# A made-up language, with letters outside a-z.
PRETEND = replace(
    en.LANGUAGE,
    code="xx",
    grammar=replace(
        en.LANGUAGE.grammar,
        phrases={**en.LANGUAGE.grammar.phrases, "STATUS": ("zuständ",)},
        numbers={"zwölf": 12},
    ),
)


def test_english_is_what_is_spoken_unless_another_is_chosen() -> None:
    assert language.current() is en.LANGUAGE
    assert parse("status") == Command(Kind.STATUS)


def test_another_language_changes_what_is_understood() -> None:
    with language.speaking(PRETEND):
        assert parse("Zuständ.") == Command(Kind.STATUS)
        assert parse("zwölf") == Command(Kind.NUMBER, number=12)
        assert parse("status").kind is Kind.UNKNOWN
    assert parse("status") == Command(Kind.STATUS)


def test_a_language_without_voice_gets_english() -> None:
    for tag in ("en", "en-GB", "nl", "", None):
        assert language.for_tag(tag) is en.LANGUAGE, tag


def test_voice_has_every_datawatch_language() -> None:
    assert sorted(language.LANGUAGES) == ["de", "en", "es", "fr", "ja"]
    for tag, code in (("de-CH", "de"), ("es_MX", "es"), ("fr-FR", "fr"), ("ja-JP", "ja")):
        assert language.for_tag(tag).code == code, tag


# What a reply tells the user to say: each language must quote its own first phrase for it.
TOLD = {
    "Say confirm answer to send it, or cancel.": ("CONFIRM", "CANCEL"),
    "Say confirm automation to send it, or cancel.": ("CONFIRM_AUTOMATON", "CANCEL"),
    "Say confirm bug to send it, or cancel.": ("CONFIRM_BUG", "CANCEL"),
    "Say confirm send to send it, or cancel.": ("CONFIRM_SEND", "CANCEL"),
    "Not sent yet. Say confirm answer, or cancel.": ("CONFIRM", "CANCEL"),
    "Not sent yet. Say confirm automation, or cancel.": ("CONFIRM_AUTOMATON", "CANCEL"),
    "Not sent yet. Say confirm bug, or cancel.": ("CONFIRM_BUG", "CANCEL"),
    "Not sent yet. Say confirm send, or cancel.": ("CONFIRM_SEND", "CANCEL"),
    "Go ahead. Say your answer, or cancel.": ("CANCEL",),
    "Go ahead. Describe the bug, or cancel.": ("CANCEL",),
    "Go ahead. Say what to send, or cancel.": ("CANCEL",),
    "Go ahead. Say what the automation should do, or cancel.": ("CANCEL",),
    "Say more detail for more.": ("DETAIL",),
    "Sorry, I didn't get that. Say help.": ("HELP",),
    "There is no list yet. Say list projects.": ("LIST_PROJECTS",),
    "I can't reach datawatch. Try again, or say stop.": ("EXIT",),
    "Your assistant didn't answer. Try again, or say stop.": ("EXIT",),
    "I haven't read a question yet. Say questions.": ("QUESTIONS",),
    "Answer sent. Say next question.": ("NEXT_QUESTION",),
    "Say option and a number, my answer, more detail, or next question.": (
        "OWN_WORDS",
        "DETAIL",
        "NEXT_QUESTION",
    ),
    "I can't reach datawatch, so nothing was sent. Say my answer or option again.": ("OWN_WORDS",),
    "I don't know whether the answer was sent. Say questions to check.": ("QUESTIONS",),
    "Say attention, running or held items, then a number.": ("ATTENTION", "RUNNING", "HELD"),
    "Say why, or tasks.": ("WHY", "TASKS"),
    "For a full reason say why and its number.": ("WHY",),
    "Say more.": ("MORE",),
    "Say more, or which number?": ("MORE",),
    "Say more, or set and a number or name.": ("MORE",),
    "I haven't read a number {number}. Say more, or pick one you heard.": ("MORE",),
    "I haven't read a number {number}. Say more, or pick a number you heard.": ("MORE",),
    "Choose something first: say its number, then set it.": ("SET_THIS",),
    "Choose something first, then say history.": ("HISTORY",),
    "Choose something first, then say its questions. Or say questions.": (
        "ITS_QUESTIONS",
        "QUESTIONS",
    ),
    "Say plans or automations, choose one, then say automata.": (
        "PLANS",
        "AUTOMATIONS",
        "AUTOMATA",
    ),
    "Choose a session first: say sessions, then its number.": ("SESSIONS",),
    "Set a project first: say list projects, or set and a project name.": ("LIST_PROJECTS",),
    "I couldn't find a project matching {name}. Say list projects.": ("LIST_PROJECTS",),
    "datawatch links no unread alerts to the {item}. There is {number} unread alert in all. "
    "Say unset, then alerts.": ("UNSET", "ALERTS"),
    "datawatch links no unread alerts to the {item}. There are {number} unread alerts in all. "
    "Say unset, then alerts.": ("UNSET", "ALERTS"),
    "datawatch links no open questions to the {item}. There is {number} open question in all. "
    "Say all questions.": ("ALL_QUESTIONS",),
    "datawatch links no open questions to the {item}. There are {number} open questions in all. "
    "Say all questions.": ("ALL_QUESTIONS",),
    "Order: by name, for sessions, automations and running work. Say the list again to hear it "
    "that way. Say most recent first to switch.": ("ORDER_RECENT",),
    "Order: most recent first, for sessions, automations and running work. Say the list again "
    "to hear it that way. Say sort by name to switch.": ("ORDER_NAME",),
    "Sessions, automations and running work are listed by name. Say most recent first to switch.": (
        "ORDER_RECENT",
    ),
    "Sessions, automations and running work are listed most recent first. Say sort by name to "
    "switch.": ("ORDER_NAME",),
}
# The commands the help sentence names.
HELP_KINDS = [
    "QUESTIONS",
    "NEXT_QUESTION",
    "OWN_WORDS",
    "CONFIRM",
    "CANCEL",
    "STATUS",
    "DETAIL",
    "ATTENTION",
    "RUNNING",
    "HELD",
    "WHY",
    "TASKS",
    "PROGRESS",
    "RESULTS",
    "FINISHED",
    "SESSIONS",
    "WAITING",
    "RUNNING_SESSIONS",
    "FAILED_SESSIONS",
    "PLANS",
    "OVERVIEW",
    "WHATS_NEXT",
    "AUTOMATIONS",
    "REPORTS",
    "LIST_PROJECTS",
    "MORE",
    "SET_THIS",
    "ITS_QUESTIONS",
    "ALL_QUESTIONS",
    "AUTOMATA",
    "HISTORY",
    "GO_BACK",
    "WHERE",
    "ALERTS",
    "ORDER",
    "ORDER_NAME",
    "ORDER_RECENT",
    "UNSET",
    "REPEAT",
    "EXIT",
]


@pytest.mark.parametrize("code", ["en", "de", "es", "fr", "ja"])
def test_replies_only_tell_the_user_to_say_what_is_understood(code: str) -> None:
    found = language.LANGUAGES[code]
    grammar = found.grammar
    sentences = set(spoken_texts())
    help_text = next(s for s in sentences if s.startswith("You can say: "))
    wanted = {**TOLD, help_text: tuple(HELP_KINDS)}
    assert set(wanted) <= sentences
    missing = [
        (english, kind)
        for english, kinds in wanted.items()
        for kind in kinds
        if grammar.clean(grammar.phrases[kind][0])
        not in grammar.clean(found.texts.get(english, english))
    ]
    assert missing == []


@pytest.mark.parametrize("code", ["en", "de", "es", "fr", "ja"])
def test_every_fixed_phrase_gives_its_own_command(code: str) -> None:
    found = language.LANGUAGES[code]
    with language.speaking(found):
        wrong = [
            (name, said, parse(said).kind.name)
            for name, group in found.grammar.phrases.items()
            for said in group
            if parse(said).kind.name != name
        ]
    assert wrong == []


@pytest.mark.parametrize("code", ["en", "de", "es", "fr", "ja"])
def test_phrases_stay_distinct_once_tidied(code: str) -> None:
    grammar = language.LANGUAGES[code].grammar
    said: dict[str, set[str]] = {}
    for name, group in grammar.phrases.items():
        for phrase in group:
            said.setdefault(grammar.clean(phrase), set()).add(name)
    assert {phrase: names for phrase, names in said.items() if len(names) > 1} == {}


@pytest.mark.parametrize("code", sorted(EXAMPLES))
def test_commands_with_a_number_name_or_words_are_understood(code: str) -> None:
    with language.speaking(language.LANGUAGES[code]):
        wrong = [(said, parse(said)) for said, command in EXAMPLES[code] if parse(said) != command]
    assert wrong == []


@pytest.mark.parametrize("code", sorted(NOT_CONFIRMING))
def test_nothing_but_a_confirming_phrase_confirms(code: str) -> None:
    confirming = {Kind.CONFIRM, Kind.CONFIRM_AUTOMATON, Kind.CONFIRM_BUG, Kind.CONFIRM_SEND}
    with language.speaking(language.LANGUAGES[code]):
        sent = [said for said in NOT_CONFIRMING[code] if parse(said).kind in confirming]
    assert sent == []


@pytest.mark.parametrize("code", ["de", "es", "fr", "ja"])
def test_a_question_is_answered_only_after_confirming(code: str) -> None:
    found = language.LANGUAGES[code]
    phrases = found.grammar.phrases
    question = Question("q1", "Ship it?", (Option("a", "yes"), Option("b", "no")))
    with language.speaking(found):
        conversation = Conversation()
        conversation.enter()
        conversation.hear(phrases["QUESTIONS"][0], None, [question])
        read_back = conversation.hear(next(s for s, c in EXAMPLES[code] if c == OPTION_TWO), None)
        assert read_back.send is None
        for wrong in NOT_CONFIRMING[code][:2]:
            assert conversation.hear(wrong, None).send is None, wrong
        sent = conversation.hear(phrases["CONFIRM"][0], None)
    assert sent.send is not None and sent.send.option == question.options[1]


def test_every_command_can_be_said() -> None:
    # These are recognised by their shape, such as "option two", not by a fixed phrase.
    shaped = {
        "SET_NUMBER", "SET_NAME", "NUMBER", "CHOOSE", "PICK", "ABOUT", "UNKNOWN",
        "ADD_AUTOMATON", "ADD_BUG", "SEND_SESSION",
    }  # fmt: skip
    for found in language.LANGUAGES.values():
        names = set(found.grammar.phrases)
        assert names == {kind.name for kind in Kind} - shaped, found.code
        said = [phrase for phrases in found.grammar.phrases.values() for phrase in phrases]
        assert len(said) == len(set(said)), f"{found.code}: one phrase, two commands"


def test_a_first_sentence_in_japanese_becomes_the_title() -> None:
    assert title_of("ログイン画面を直す。それから色も変える。") == "ログイン画面を直す"
    assert title_of("直せる？お願い") == "直せる"
    assert title_of("fix v1.2 now. Then rest") == "Fix v1.2 now"


def test_japanese_replies_have_japanese_punctuation() -> None:
    tidy = language.LANGUAGES["ja"].tidy
    assert tidy("1, oak. 2, elm. もっと。.") == "1、oak。2、elm。もっと。"
    assert tidy("v1.2.3 です。 Paint: 完了.") == "v1.2.3 です。Paint、完了。"


def test_names_in_any_alphabet_can_be_matched() -> None:
    assert match_names("küche", ["Küche", "Bad"]) == ["Küche"]
    assert match_names("テスト", ["テスト計画", "other"]) == ["テスト計画"]
    assert custom.spoken_form("Täglicher") == "täglicher"


def test_the_parser_holds_no_english_words() -> None:
    """Words to listen for belong in a language's data, never in the code that listens."""
    tree = ast.parse((VOICE / "phrases.py").read_text(encoding="utf-8"))
    documented = {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef)
        and ast.get_docstring(node)
        and isinstance(node.body[0], ast.Expr)
    }
    words = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in documented
        # Group names in patterns are not words that are listened for.
        and node.value not in ("kind", "chosen", "number", "project")
        and re.search(r"[a-z]{3}", node.value)
    ]
    assert words == []


# Everything that words what is said. The AI tools use it too, and are always English.
SPOKEN = [VOICE / f"{name}.py" for name in (
    "actions", "automata", "conversation", "custom", "items", "order", "questions",
    "reports", "speech", "work",
)] + [VOICE.parent / f"{name}.py" for name in ("mode", "doing", "cards", "reporting")]  # fmt: skip
# Calls whose text is looked up in the language, and calls whose text is never spoken.
_LOOKED_UP = ("t", "tn", "N_")
_UNSPOKEN = ("_LOGGER.", "re.", "DatawatchError")


def _texts(tree: ast.AST) -> list[str]:
    """The English that translators see: the text arguments of t, tn and N_."""
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and ast.unparse(node.func) in _LOOKED_UP:
            wanted = node.args[1:3] if ast.unparse(node.func) == "tn" else node.args[:1]
            found += [a.value for a in wanted if isinstance(a, ast.Constant)]
    return [text for text in found if isinstance(text, str)]


def spoken_texts() -> list[str]:
    """Every sentence a language has to translate."""
    return sorted({text for path in SPOKEN for text in _texts(ast.parse(path.read_text()))})


# Two words, or a word ending a sentence, is something said. One bare word is a code.
_SAID = r"[A-Za-z]{2,}[,.:]? [A-Za-z]|[A-Za-z]{2,}[.?!]( |$)|^ ?[A-Z][a-z]+ "


# Never said: a bug id's start, a tag's start, a storage key and a background task's name.
_CODES = ("voice-", "automaton:", ".focus", " voice")


def _loose_english(tree: ast.AST) -> list[str]:
    """Words that would be said without being looked up."""
    skipped: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            if ast.get_docstring(node) and isinstance(node.body[0], ast.Expr):
                skipped.add(id(node.body[0].value))
        elif isinstance(node, ast.Call):
            name = ast.unparse(node.func)
            if name in _LOOKED_UP:
                text_args = node.args[1:3] if name == "tn" else node.args[:1]
                skipped |= {id(a) for a in text_args}
            elif name.startswith(_UNSPOKEN):
                skipped |= {id(part) for part in ast.walk(node)}
        elif isinstance(node, ast.Assert) and node.msg:
            skipped |= {id(part) for part in ast.walk(node.msg)}
    # Inside an f-string, even one word is something said.
    inside = {
        id(part)
        for node in ast.walk(tree)
        if isinstance(node, ast.JoinedStr)
        for part in node.values
    }
    return [
        f"{node.lineno}: {node.value!r}"
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in skipped
        and node.value not in _CODES
        and re.search(r"[A-Za-z]{2}" if id(node) in inside else _SAID, node.value)
    ]


def test_nothing_is_said_without_being_looked_up() -> None:
    loose = {
        path.name: found
        for path in SPOKEN
        if (found := _loose_english(ast.parse(path.read_text())))
    }
    assert loose == {}


def test_every_language_translates_every_sentence() -> None:
    sentences = spoken_texts()
    for found in language.LANGUAGES.values():
        if found is en.LANGUAGE:
            continue
        assert sorted(found.texts) == sentences, found.code
        for english, translated in found.texts.items():
            assert (
                re.findall(r"\{\w+\}", translated).sort() == re.findall(r"\{\w+\}", english).sort()
            )
            assert set(re.findall(r"\{\w+\}", translated)) == set(re.findall(r"\{\w+\}", english))


def test_another_language_changes_what_is_said() -> None:
    marked = replace(en.LANGUAGE, code="xx", texts={s: f"«{s}»" for s in spoken_texts()})
    conversation = Conversation()
    with language.speaking(marked):
        assert conversation.enter().text == "«Datawatch activated.»"
        assert conversation.hear("help", None).text.startswith("«You can say: ")
    assert Conversation().enter().text == "Datawatch activated."


def test_the_voice_command_reference_matches_what_is_listened_for(tmp_path: Path) -> None:
    assert DOCUMENT.read_text(encoding="utf-8") == render(), "run scripts/voice_examples.py"
    write(tmp_path / "written.md")
    assert (tmp_path / "written.md").read_text(encoding="utf-8") == render()
