"""Fixed phrases: what the user says becomes a command. Speech-to-text adds noise."""

from __future__ import annotations

import pytest

from custom_components.datawatch.voice.phrases import Command, Kind, parse


@pytest.mark.parametrize(
    ("heard", "kind"),
    [
        ("status", Kind.STATUS),
        ("Status.", Kind.STATUS),
        ("what's the status", Kind.STATUS),
        ("more detail", Kind.DETAIL),
        ("more details please", Kind.DETAIL),
        ("list projects", Kind.LIST_PROJECTS),
        ("List the projects.", Kind.LIST_PROJECTS),
        ("projects", Kind.LIST_PROJECTS),
        ("more", Kind.MORE),
        ("next", Kind.MORE),
        ("where am I?", Kind.WHERE),
        ("what's my focus", Kind.WHERE),
        ("unset", Kind.UNSET),
        ("un set", Kind.UNSET),
        ("clear focus", Kind.UNSET),
        ("repeat", Kind.REPEAT),
        ("say that again", Kind.REPEAT),
        ("help", Kind.HELP),
        ("what can I say", Kind.HELP),
        ("stop", Kind.EXIT),
        ("Stop!", Kind.EXIT),
        ("exit", Kind.EXIT),
        ("done", Kind.EXIT),
        ("close datawatch", Kind.EXIT),
        ("close data watch", Kind.EXIT),
        ("Close Data-Watch.", Kind.EXIT),
    ],
)
def test_phrases(heard: str, kind: Kind) -> None:
    assert parse(heard).kind is kind


@pytest.mark.parametrize(
    ("heard", "number"),
    [
        ("set two", 2),
        ("Set 2.", 2),
        ("set number three", 3),
        ("set project four", 4),
        ("set to", 2),
        ("set too", 2),
        ("set for", 4),
        ("set twelve", 12),
        ("set twenty one", 21),
        ("set twenty-one", 21),
    ],
)
def test_set_by_number(heard: str, number: int) -> None:
    assert parse(heard) == Command(Kind.SET_NUMBER, number=number)


@pytest.mark.parametrize(("heard", "number"), [("two", 2), ("number 5", 5), ("Three.", 3)])
def test_bare_number_is_reported_as_a_number(heard: str, number: int) -> None:
    assert parse(heard) == Command(Kind.NUMBER, number=number)


@pytest.mark.parametrize(
    ("heard", "name"),
    [
        ("set project maple", "maple"),
        ("set maple", "maple"),
        ("Set project Maple Syrup.", "maple syrup"),
        ("set focus to maple", "maple"),
    ],
)
def test_set_by_name(heard: str, name: str) -> None:
    assert parse(heard) == Command(Kind.SET_NAME, name=name)


@pytest.mark.parametrize("heard", ["", "  ", "turn on the lights", "set", "stop the music now"])
def test_anything_else_is_unknown(heard: str) -> None:
    result = parse(heard)
    assert result.kind is Kind.UNKNOWN
    assert result.text == " ".join(heard.lower().split())
