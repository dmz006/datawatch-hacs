"""Voice takes another language from data alone: no change to the code that listens."""

from __future__ import annotations

import ast
import re
from dataclasses import replace
from pathlib import Path

from custom_components.datawatch.voice import custom, language
from custom_components.datawatch.voice.conversation import Conversation
from custom_components.datawatch.voice.lang import en
from custom_components.datawatch.voice.names import match_names
from custom_components.datawatch.voice.phrases import Command, Kind, parse

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
