"""Match a spoken, possibly partial, name against real names."""

from __future__ import annotations

import re
from collections.abc import Sequence

from .grammar import normalise

_MINIMUM_PARTIAL = 3


def _words(name: str) -> list[str]:
    split_camel = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name)
    return normalise(split_camel, apostrophes="").split()


def _is_partial(spoken: list[str], name: list[str]) -> bool:
    if "".join(spoken) in "".join(name):
        return True
    # Every spoken word starts a word of the name, in the same order.
    remaining = iter(name)
    return all(any(word.startswith(part) for word in remaining) for part in spoken)


def match_names(spoken: str, names: Sequence[str]) -> list[str]:
    """Return every name that fits. Exact matches, if any, are the only ones returned."""
    heard = _words(spoken)
    compact = "".join(heard)
    if not compact:
        return []
    exact = [name for name in names if "".join(_words(name)) == compact]
    if exact:
        return exact
    if len(compact) < _MINIMUM_PARTIAL:
        return []
    return [name for name in names if _is_partial(heard, _words(name))]
