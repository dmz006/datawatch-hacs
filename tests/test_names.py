"""A spoken name may be partial. Return every candidate; never pick between several."""

from __future__ import annotations

import pytest

from custom_components.datawatch.voice.names import match_names

NAMES = ["maple-syrup", "maple_leaf", "Oak Tree", "birch", "birch-tools", "RedCedar"]


@pytest.mark.parametrize(
    ("spoken", "expected"),
    [
        ("maple syrup", ["maple-syrup"]),
        ("maple", ["maple-syrup", "maple_leaf"]),
        ("syrup", ["maple-syrup"]),
        ("oak", ["Oak Tree"]),
        ("oaktree", ["Oak Tree"]),
        ("red cedar", ["RedCedar"]),
        ("cedar", ["RedCedar"]),
        ("map lea", ["maple_leaf"]),
        ("willow", []),
        ("", []),
        ("a", []),
    ],
)
def test_matching(spoken: str, expected: list[str]) -> None:
    assert match_names(spoken, NAMES) == expected


def test_an_exact_name_wins_over_longer_names_that_contain_it() -> None:
    assert match_names("birch", NAMES) == ["birch"]


def test_two_names_that_sound_identical_are_both_returned() -> None:
    assert match_names("big cat", ["big-cat", "Big Cat"]) == ["big-cat", "Big Cat"]
