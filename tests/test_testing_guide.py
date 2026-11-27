"""The voice testing guide only tells testers to say things the integration understands."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from custom_components.datawatch.voice.phrases import Kind, parse

GUIDE = (Path(__file__).parents[1] / "docs/testing.md").read_text()
# Said before datawatch mode is open, so they are not commands inside it.
_OPENING = {"open datawatch", "use datawatch", "datawatch"}
# A command in the guide's style, with the words in italics that may follow it.
_SAID = re.compile(r"`([^`]+)`(?:\s+\*([^*]+)\*)?")


def rows() -> list[tuple[str, str]]:
    """Each numbered row's number and its "say" or "do" cell."""
    found = re.findall(r"^\| (\d+\.\d+)(?: ⚠️)? \| (.*?) \| .*\| ☐ \|$", GUIDE, re.M)
    return [(number, cell) for number, cell in found]


# Section 14 is done with a finger or a mouse, and 15 is a list.
SPOKEN = [(n, cell) for n, cell in rows() if not n.startswith("14.")]


def commands() -> list[tuple[str, str]]:
    return [
        (number, " ".join(part for part in match if part))
        for number, cell in SPOKEN
        for match in _SAID.findall(cell)
    ]


def test_the_guide_covers_every_section_and_has_unique_numbers() -> None:
    numbers = [number for number, _ in rows()]
    assert len(numbers) == len(set(numbers)) > 90
    assert {int(number.split(".")[0]) for number in numbers} == set(range(15))


@pytest.mark.parametrize(("row", "said"), commands())
def test_every_command_in_the_guide_is_understood(row: str, said: str) -> None:
    if said not in _OPENING:
        assert parse(said).kind is not Kind.UNKNOWN, f"row {row}: {said}"


def test_every_kind_of_command_has_a_row() -> None:
    tried = {parse(said).kind for _, said in commands()}
    # Heard only as an answer to a question the integration asked, or by their number.
    untried = set(Kind) - tried - {Kind.UNKNOWN}
    assert untried == set(), sorted(kind.name for kind in untried)


@pytest.mark.parametrize(
    "words",
    [
        "which would you pick and why",
        "go ahead and send it",
        "can you file a bug report for me",
        "purple monkey",
        "yes",
    ],
)
def test_talk_the_guide_expects_not_to_be_a_command_is_not_one(words: str) -> None:
    assert words in GUIDE.lower()
    assert parse(words).kind is Kind.UNKNOWN
