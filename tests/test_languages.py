"""Voice takes another language from data alone: no change to the code that listens."""

from __future__ import annotations

import ast
import re
from dataclasses import replace
from pathlib import Path

from custom_components.datawatch.voice import custom, language
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
