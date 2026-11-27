"""Which language datawatch mode listens for and speaks.

A language is data in voice/lang/: nothing else changes to add one. English is used
wherever a language has no voice.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar

from .grammar import Language
from .lang import de, en, es, fr, ja

LANGUAGES: dict[str, Language] = {
    found.code: found for found in (en.LANGUAGE, de.LANGUAGE, es.LANGUAGE, fr.LANGUAGE, ja.LANGUAGE)
}
# Each visit to datawatch mode runs in its own task, so choosing a language in one never
# changes another.
_current: ContextVar[Language] = ContextVar("datawatch_voice_language", default=en.LANGUAGE)


def current() -> Language:
    """The language being spoken here."""
    return _current.get()


def for_tag(tag: str | None) -> Language:
    """The language for a tag such as "de-CH": English where there is no voice for it."""
    return LANGUAGES.get((tag or "").replace("_", "-").split("-")[0].lower(), en.LANGUAGE)


@contextmanager
def speaking(language: Language) -> Iterator[None]:
    """Listen and speak in language inside this block."""
    token = _current.set(language)
    try:
        yield
    finally:
        _current.reset(token)


def t(english: str, /, **values: object) -> str:
    """english in the current language, with its {names} filled in.

    Pass whole sentences: a language may order the words differently.
    """
    text = current().texts.get(english, english)
    return text.format(**values) if values else text


def tn(number: int, one: str, many: str, /, **values: object) -> str:
    """The singular or plural sentence for number, which both may show as {number}."""
    return t(one if current().singular(number) else many, number=number, **values)


def N_(english: str) -> str:
    """Mark a sentence that is looked up later, with t(), when it is said."""
    return english
