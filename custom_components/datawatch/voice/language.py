"""Which language datawatch mode listens for.

A language is data in voice/lang/: nothing else changes to add one. English is the only
one so far, and is used wherever a language has no voice.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar

from .grammar import Language
from .lang import en

LANGUAGES: dict[str, Language] = {found.code: found for found in (en.LANGUAGE,)}
# Each visit to datawatch mode runs in its own task, so choosing a language in one never
# changes another.
_current: ContextVar[Language] = ContextVar("datawatch_voice_language", default=en.LANGUAGE)


def current() -> Language:
    """The language being spoken here."""
    return _current.get()


def for_tag(tag: str | None) -> Language:
    """The language for a tag such as "de-CH": English where there is no voice for it."""
    return LANGUAGES.get((tag or "").split("-")[0].lower(), en.LANGUAGE)


@contextmanager
def speaking(language: Language) -> Iterator[None]:
    """Listen in language inside this block."""
    token = _current.set(language)
    try:
        yield
    finally:
        _current.reset(token)
