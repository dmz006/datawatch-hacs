"""Example sentences for each voice language, and the command reference made from them.

The tests check that each example gives the command shown here, so the reference in
docs/voice-languages.md cannot drift from what voice understands. To rewrite it:

    python3 scripts/voice_examples.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from custom_components.datawatch.voice.language import LANGUAGES  # noqa: E402
from custom_components.datawatch.voice.phrases import Command, Kind  # noqa: E402

DOCUMENT = ROOT / "docs" / "voice-languages.md"
NAMES = {"en": "English", "de": "Deutsch", "es": "Español", "fr": "Français", "ja": "日本語"}

OPTION_TWO = Command(Kind.CHOOSE, number=2)
_TWO_PLAN = Command(Kind.SET_NUMBER, number=2, item="plan")
_TWO = Command(Kind.SET_NUMBER, number=2)
_PROJECT = Command(Kind.SET_NAME, name="oak", item="project")
_AUTOMATON = Command(Kind.SET_NAME, name="roof", item="automaton")
_PICK = Command(Kind.PICK, number=2)
_ABOUT = Command(Kind.ABOUT, name="roof")
_NUMBER = Command(Kind.NUMBER, number=2)
_WHY = Command(Kind.WHY, number=2)
_TASKS = Command(Kind.TASKS, number=2)
_PROGRESS = Command(Kind.PROGRESS, number=2)
_RESULTS = Command(Kind.RESULTS, number=2)
_QUESTIONS = Command(Kind.ITS_QUESTIONS, number=2)
_HISTORY = Command(Kind.HISTORY, number=2)


def _said(kind: Kind, words: str | None = None) -> Command:
    return Command(kind, text=words)


# What to say, and the command it must give. The first of each command is the one shown.
EXAMPLES: dict[str, tuple[tuple[str, Command], ...]] = {
    "en": (
        ("two", _NUMBER),
        ("option two", OPTION_TWO),
        ("choose two", OPTION_TWO),
        ("set two", _TWO),
        ("set plan two", _TWO_PLAN),
        ("set project oak", _PROJECT),
        ("set the automaton roof", _AUTOMATON),
        ("tell me about two", _PICK),
        ("about roof", _ABOUT),
        ("why two", _WHY),
        ("tasks for two", _TASKS),
        ("progress of two", _PROGRESS),
        ("results of two", _RESULTS),
        ("questions for two", _QUESTIONS),
        ("history of two", _HISTORY),
        ("My answer is: ship it", _said(Kind.OWN_WORDS, "ship it")),
        ("Add automation: fix the roof", _said(Kind.ADD_AUTOMATON, "fix the roof")),
        ("Add bug: login fails", _said(Kind.ADD_BUG, "login fails")),
        ("Send to session: go on", _said(Kind.SEND_SESSION, "go on")),
        ("add bug", _said(Kind.ADD_BUG)),
    ),
    "de": (
        ("zwei", _NUMBER),
        ("Nummer zwei", _NUMBER),
        ("Option zwei", OPTION_TWO),
        ("wähle zwei", OPTION_TWO),
        ("setze zwei", _TWO),
        ("setze Plan zwei", _TWO_PLAN),
        ("setze Projekt oak", _PROJECT),
        ("setze den Automaten roof", _AUTOMATON),
        ("erzähl mir etwas über zwei", _PICK),
        ("Details zu roof", _ABOUT),
        ("warum zwei", _WHY),
        ("warum ist Nummer zwei blockiert", _WHY),
        ("Aufgaben von zwei", _TASKS),
        ("Fortschritt von zwei", _PROGRESS),
        ("Ergebnisse von zwei", _RESULTS),
        ("Fragen zu zwei", _QUESTIONS),
        ("Verlauf von zwei", _HISTORY),
        ("Meine Antwort ist: raus damit", _said(Kind.OWN_WORDS, "raus damit")),
        ("Neue Automatisierung: Dach reparieren", _said(Kind.ADD_AUTOMATON, "Dach reparieren")),
        (
            "Füge eine Automatisierung hinzu: Dach reparieren",
            _said(Kind.ADD_AUTOMATON, "Dach reparieren"),
        ),
        ("Fehler melden: Anmeldung geht nicht", _said(Kind.ADD_BUG, "Anmeldung geht nicht")),
        ("An Sitzung senden: mach weiter", _said(Kind.SEND_SESSION, "mach weiter")),
        ("neuer Fehler", _said(Kind.ADD_BUG)),
    ),
    "es": (
        ("dos", _NUMBER),
        ("número dos", _NUMBER),
        ("opción dos", OPTION_TWO),
        ("elige dos", OPTION_TWO),
        ("fija dos", _TWO),
        ("fija el plan dos", _TWO_PLAN),
        ("fija el proyecto oak", _PROJECT),
        ("fija el autómata roof", _AUTOMATON),
        ("háblame del dos", _PICK),
        ("información sobre roof", _ABOUT),
        ("por qué dos", _WHY),
        ("por qué está bloqueado el número dos", _WHY),
        ("tareas del dos", _TASKS),
        ("progreso del dos", _PROGRESS),
        ("resultados del dos", _RESULTS),
        ("preguntas del dos", _QUESTIONS),
        ("historial del dos", _HISTORY),
        ("Mi respuesta es: adelante", _said(Kind.OWN_WORDS, "adelante")),
        (
            "Nueva automatización: arreglar el techo",
            _said(Kind.ADD_AUTOMATON, "arreglar el techo"),
        ),
        (
            "Añade una automatización: arreglar el techo",
            _said(Kind.ADD_AUTOMATON, "arreglar el techo"),
        ),
        ("Informar de un error: no deja entrar", _said(Kind.ADD_BUG, "no deja entrar")),
        ("Enviar a la sesión: continúa", _said(Kind.SEND_SESSION, "continúa")),
        ("nuevo error", _said(Kind.ADD_BUG)),
    ),
    "fr": (
        ("deux", _NUMBER),
        ("numéro deux", _NUMBER),
        ("option deux", OPTION_TWO),
        ("choisis deux", OPTION_TWO),
        ("sélectionne deux", _TWO),
        ("sélectionne le plan deux", _TWO_PLAN),
        ("sélectionne le projet oak", _PROJECT),
        ("sélectionne l'automate roof", _AUTOMATON),
        ("parle-moi du deux", _PICK),
        ("détails sur roof", _ABOUT),
        ("pourquoi deux", _WHY),
        ("pourquoi le numéro deux est bloqué", _WHY),
        ("tâches du deux", _TASKS),
        ("progression du deux", _PROGRESS),
        ("résultats du deux", _RESULTS),
        ("questions du deux", _QUESTIONS),
        ("historique du deux", _HISTORY),
        ("Ma réponse est : on y va", _said(Kind.OWN_WORDS, "on y va")),
        (
            "Nouvelle automatisation : réparer le toit",
            _said(Kind.ADD_AUTOMATON, "réparer le toit"),
        ),
        (
            "Ajoute une automatisation : réparer le toit",
            _said(Kind.ADD_AUTOMATON, "réparer le toit"),
        ),
        ("Signaler un bug : connexion impossible", _said(Kind.ADD_BUG, "connexion impossible")),
        ("Envoyer à la session : continue", _said(Kind.SEND_SESSION, "continue")),
        ("nouveau bug", _said(Kind.ADD_BUG)),
    ),
    "ja": (
        ("2番", _NUMBER),
        ("に", _NUMBER),
        ("選択肢2", OPTION_TWO),
        ("2番を選んで。", OPTION_TWO),
        ("2に設定", _TWO),
        ("プラン2に設定", _TWO_PLAN),
        ("プロジェクト oak に設定してください", _PROJECT),
        ("オートマトン roof に設定", _AUTOMATON),
        ("2番について教えて", _PICK),
        ("roofについて", _ABOUT),
        ("なぜ2番", _WHY),
        ("2番はなぜブロックされているの", _WHY),
        ("2のタスク", _TASKS),
        ("2の進捗", _PROGRESS),
        ("2の結果", _RESULTS),
        ("2の質問", _QUESTIONS),
        ("2の履歴", _HISTORY),
        ("私の回答は、出荷してください", _said(Kind.OWN_WORDS, "出荷してください")),
        ("オートメーションを追加。屋根を直す", _said(Kind.ADD_AUTOMATON, "屋根を直す")),
        ("バグを報告、ログインできない", _said(Kind.ADD_BUG, "ログインできない")),
        ("セッションに送信。続けて", _said(Kind.SEND_SESSION, "続けて")),
        ("バグを追加してください。", _said(Kind.ADD_BUG)),
    ),
}

# None of these may send anything. The first two are also tried while an answer waits.
NOT_CONFIRMING: dict[str, tuple[str, ...]] = {
    "en": ("yes", "confirm", "send", "send it", "do not confirm answer", "dont confirm bug"),
    "de": (
        "ja",
        "bestätigen",
        "senden",
        "okay",
        "antwort nicht bestätigen",
        "bestätige die antwort nicht",
        "fehler nicht bestätigen",
        "nicht senden bestätigen",
    ),
    "es": (
        "sí",
        "confirmar",
        "enviar",
        "vale",
        "no confirmar respuesta",
        "no confirmes la respuesta",
        "no confirmar error",
        "no confirmar envío",
    ),
    "fr": (
        "oui",
        "confirmer",
        "envoyer",
        "d'accord",
        "ne pas confirmer la réponse",
        "ne confirme pas la réponse",
        "ne pas confirmer le bug",
        "ne confirmez pas l'envoi",
    ),
    "ja": (
        "はい",
        "確定",
        "送信",
        "オーケー",
        "回答を確定しないで",
        "回答を確定しないでください",
        "バグを確定しない",
        "送信を確定しません",
    ),
}

_HEADINGS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Leaving and getting help",
        ("HELP", "REPEAT", "GO_BACK", "EXIT"),
    ),
    (
        "Status and projects",
        ("STATUS", "DETAIL", "LIST_PROJECTS", "MORE", "WHERE", "UNSET", "SET_THIS"),
    ),
    (
        "Questions",
        (
            "QUESTIONS",
            "NEXT_QUESTION",
            "ALL_QUESTIONS",
            "ITS_QUESTIONS",
            "OWN_WORDS",
            "CONFIRM",
            "CANCEL",
        ),
    ),
    (
        "Work",
        (
            "ATTENTION",
            "RUNNING",
            "HELD",
            "WHY",
            "TASKS",
            "PROGRESS",
            "RESULTS",
            "FINISHED",
            "PLANS",
            "OVERVIEW",
            "WHATS_NEXT",
            "AUTOMATIONS",
            "AUTOMATA",
            "HISTORY",
        ),
    ),
    (
        "Sessions, alerts and reports",
        ("SESSIONS", "WAITING", "RUNNING_SESSIONS", "FAILED_SESSIONS", "ALERTS", "REPORTS"),
    ),
    ("List order", ("ORDER", "ORDER_NAME", "ORDER_RECENT")),
    ("Confirming an action", ("CONFIRM_AUTOMATON", "CONFIRM_BUG", "CONFIRM_SEND")),
)

_INTRODUCTION = """# Voice commands in each language

Datawatch mode listens and speaks in the language of the voice assistant that heard you:
English, German, Spanish, French or Japanese. With any other language it uses English.

This page is made from the words the integration listens for. Each column is one language.
Where a command has several wordings, the first is shown; the replies quote that one.

Corrections are welcome: [open an issue](https://github.com/dmz006/datawatch-hacs/issues) or a
pull request that changes the language's file in `custom_components/datawatch/voice/lang/`.
"""

_SHAPES: tuple[tuple[str, str], ...] = (
    ("A number on its own", "NUMBER"),
    ("Choose an option", "CHOOSE"),
    ("Choose a line", "SET_NUMBER"),
    ("Choose by name", "SET_NAME"),
    ("Ask about a line", "PICK"),
    ("Ask about a name", "ABOUT"),
    ("Why a line is stuck", "WHY"),
    ("Tasks of a line", "TASKS"),
    ("Progress of a line", "PROGRESS"),
    ("Results of a line", "RESULTS"),
    ("Questions of a line", "ITS_QUESTIONS"),
    ("History of a line", "HISTORY"),
    ("Answer in your own words", "OWN_WORDS"),
    ("Add a draft automaton", "ADD_AUTOMATON"),
    ("Report a bug", "ADD_BUG"),
    ("Send to a session (switched off)", "SEND_SESSION"),
)


def _row(first: str, cells: list[str]) -> str:
    return f"| {first} | {' | '.join(cells)} |"


def _table(first: str, rows: list[str]) -> list[str]:
    head = _row(first, [NAMES[code] for code in NAMES])
    return [head, "|---" * (len(NAMES) + 1) + "|", *rows, ""]


def render() -> str:
    """The whole reference, as it should be in the document."""
    lines = [_INTRODUCTION]
    opening = [
        _row(
            "Open datawatch mode",
            [f"`{LANGUAGES[code].grammar.entry_examples[0]}`" for code in NAMES],
        )
    ]
    lines += ["## Opening", "", *_table("To", opening)]
    for heading, kinds in _HEADINGS:
        rows = [
            _row(
                f"`{LANGUAGES['en'].grammar.phrases[kind][0]}`",
                [f"`{LANGUAGES[code].grammar.phrases[kind][0]}`" for code in NAMES],
            )
            for kind in kinds
        ]
        lines += [f"## {heading}", "", *_table("Command", rows)]
    rows = []
    for title, kind in _SHAPES:
        cells = [
            next(f"`{said}`" for said, command in EXAMPLES[code] if command.kind.name == kind)
            for code in NAMES
        ]
        rows.append(_row(title, cells))
    lines += [
        "## With a number, a name or your own words",
        "",
        "The examples use the number two and made-up names. For an action, the words after the "
        "opening are yours; you can also say the opening alone and give the words next.",
        "",
        *_table("To", rows),
    ]
    return "\n".join(lines)


def write(document: Path = DOCUMENT) -> None:
    document.write_text(render(), encoding="utf-8")


if __name__ == "__main__":
    write()
