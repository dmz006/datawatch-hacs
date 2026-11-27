"""Home Assistant's screens are translated into every language datawatch ships."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import aiohttp
import pytest
from fake_datawatch import Fake, serve
from ha_harness import add_datawatch, running_hass
from homeassistant.setup import async_setup_component

from custom_components.datawatch.voice.language import LANGUAGES as LANGUAGES_SPOKEN

FOLDER = Path(__file__).resolve().parents[1] / "custom_components" / "datawatch" / "translations"
# datawatch's own languages. Add one here when datawatch adds one.
LANGUAGES = ("en", "de", "es", "fr", "ja")
TRANSLATED = LANGUAGES[1:]
# What screens tell the user to say. Each language quotes the words its own voice listens for.
SPOKEN = ("open", "ORDER_NAME", "ORDER_RECENT")


def _to_say(language: str, wanted: str) -> str:
    grammar = LANGUAGES_SPOKEN[language].grammar
    said = grammar.entry_examples[0] if wanted == "open" else grammar.phrases[wanted][0]
    return f'"{said}"'


def _strings(node: Any, path: str = "") -> dict[str, str]:
    if isinstance(node, str):
        return {path: node}
    found: dict[str, str] = {}
    for key, value in node.items():
        found |= _strings(value, f"{path}.{key}" if path else key)
    return found


def _load(language: str) -> dict[str, str]:
    return _strings(json.loads((FOLDER / f"{language}.json").read_text(encoding="utf-8")))


def _fixed(text: str) -> list[str]:
    """What a translation must not change: placeholders and code."""
    return sorted(re.findall(r"`[^`]*`|\{[a-z_]+\}", text))


def test_there_is_a_file_for_each_datawatch_language_and_no_other() -> None:
    assert sorted(path.stem for path in FOLDER.glob("*.json")) == sorted(LANGUAGES)


@pytest.mark.parametrize("language", TRANSLATED)
def test_every_english_text_is_translated(language: str) -> None:
    english, other = _load("en"), _load(language)
    assert list(other) == list(english)
    assert [key for key, text in other.items() if not text.strip()] == []


@pytest.mark.parametrize("language", TRANSLATED)
def test_placeholders_and_code_are_unchanged_and_spoken_words_are_its_own(language: str) -> None:
    english, other = _load("en"), _load(language)
    for key, text in english.items():
        assert _fixed(other[key]) == _fixed(text), key
        for wanted in SPOKEN:
            quoted = other[key].casefold().count(_to_say(language, wanted).casefold())
            assert quoted == text.count(_to_say("en", wanted)), f"{key}: {wanted}"


@pytest.mark.parametrize("language", TRANSLATED)
def test_prd_is_never_shown(language: str) -> None:
    assert [key for key, text in _load(language).items() if re.search(r"\bPRDs?\b", text)] == []


# Home Assistant builds new entity ids from German, Spanish and French names, not Japanese.
@pytest.mark.parametrize(
    ("language", "entity_id"),
    [
        ("en", "sensor.datawatch_open_questions"),
        ("de", "sensor.datawatch_offene_fragen"),
        ("es", "sensor.datawatch_preguntas_abiertas"),
        ("fr", "sensor.datawatch_questions_ouvertes"),
        ("ja", "sensor.datawatch_open_questions"),
    ],
)
def test_home_assistant_names_the_sensors_in_its_language(
    certificate: tuple[Path, Path, str], tmp_path: Path, language: str, entity_id: str
) -> None:
    async def body(url: str, session: aiohttp.ClientSession, fake: Fake) -> None:
        async with running_hass(tmp_path) as hass:
            hass.config.language = language
            for component in ("homeassistant", "assist_satellite", "conversation"):
                assert await async_setup_component(hass, component, {})
            await add_datawatch(hass, url)
            await hass.async_block_till_done(wait_background_tasks=True)
            state = hass.states.get(entity_id)
            assert state, sorted(hass.states.async_entity_ids("sensor"))
            name = _load(language)["entity.sensor.open_questions.name"]
            assert state.attributes["friendly_name"] == f"datawatch {name}"

    serve(certificate, body)
