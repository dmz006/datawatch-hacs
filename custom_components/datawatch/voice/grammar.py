"""What a language needs so that datawatch mode can understand it."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Grammar:
    """What can be said. Patterns marked "heard" match speech-to-text's own writing; the
    rest match it after normalise(). The group "chosen" is a number or a name.
    """

    # Fixed phrases for each command, by its name in phrases.Kind.
    phrases: Mapping[str, tuple[str, ...]]
    # Every way a number may be written, including what speech-to-text writes by mistake.
    numbers: Mapping[str, int]
    # Characters dropped before matching, so that "what's" and "whats" are the same.
    apostrophes: str
    # Politeness at either end, which changes nothing.
    polite: re.Pattern[str]
    # "number two" or just "two".
    number: re.Pattern[str]
    # Heard: the opening of an answer in the user's own words. The words follow it.
    own_words: re.Pattern[str]
    # Heard: the openings of actions, by Kind name. Any words may follow.
    actions: tuple[tuple[str, re.Pattern[str]], ...]
    # Questions about one numbered line, by Kind name, such as "why is two blocked".
    about_one: tuple[tuple[str, re.Pattern[str]], ...]
    # "tell me about two", or about a name.
    about: re.Pattern[str]
    # "option two". With several groups, the one that matched is the choice.
    choose: re.Pattern[str]
    # "set ...": what follows is the group "chosen".
    set_command: re.Pattern[str]
    # Within "set ...": a kind of item (group "kind") and then which one.
    set_item: re.Pattern[str]
    # The words used for each kind of item, giving the kind's own name.
    item_kinds: Mapping[str, str]
    # Within "set ...": filler to drop, and how a project is named.
    set_filler: re.Pattern[str]
    set_project: re.Pattern[str]
    # Dropped from a report's name, and from what is heard, before they are compared.
    report_filler: tuple[re.Pattern[str], ...]
    # Home Assistant sentences that open datawatch mode.
    entry_sentences: tuple[str, ...]
    # What a person says to open it, for screens and documents.
    entry_examples: tuple[str, ...]
    # Names a report must not take, because they open datawatch mode.
    entry_names: tuple[str, ...]
    # False for a writing system without spaces between words: they are then ignored.
    spaced: bool = True

    def clean(self, heard: str) -> str:
        """heard as the patterns and fixed phrases match it."""
        text = normalise(heard, self.apostrophes)
        return text if self.spaced else text.replace(" ", "")


@dataclass(frozen=True)
class Language:
    """One language voice can use."""

    code: str
    grammar: Grammar
    # What is said, keyed by the English sentence. English needs none.
    texts: Mapping[str, str] = field(default_factory=dict)
    # Whether a number takes the singular.
    singular: Callable[[int], bool] = lambda number: number == 1
    # The last touch on a whole reply before it is spoken, such as its punctuation.
    tidy: Callable[[str], str] = lambda reply: reply


def normalise(heard: str, apostrophes: str = "'\N{RIGHT SINGLE QUOTATION MARK}") -> str:
    """Letters and numbers of any alphabet, in lower case, with single spaces."""
    text = unicodedata.normalize("NFKC", heard).casefold()
    text = text.translate(str.maketrans("", "", apostrophes))
    return " ".join(re.sub(r"[\W_]+", " ", text).split())
