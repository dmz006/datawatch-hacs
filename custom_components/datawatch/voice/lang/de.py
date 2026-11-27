"""German: what datawatch mode listens for. What it says is in de_texts.py."""

from __future__ import annotations

import re

from ..grammar import Grammar, Language
from .de_texts import TEXTS

# The first wording of each command is the one the replies quote.
_PHRASES: dict[str, tuple[str, ...]] = {
    "STATUS": ("status", "wie ist der status", "was ist der status", "gib mir den status"),
    "DETAIL": ("mehr details", "details", "mehr dazu", "erzähl mir mehr"),
    "LIST_PROJECTS": (
        "projekte auflisten",
        "liste die projekte auf",
        "projekte",
        "meine projekte",
    ),
    "MORE": ("mehr", "weiter", "die nächsten", "mach weiter"),
    "WHERE": ("wo bin ich", "was ist mein fokus", "was ist der fokus"),
    "UNSET": ("fokus aufheben", "fokus löschen", "heb den fokus auf", "kein fokus"),
    "REPEAT": ("wiederholen", "wiederhole das", "sag das noch einmal", "noch einmal", "nochmal"),
    "HELP": ("hilfe", "was kann ich sagen"),
    "EXIT": ("stopp", "stop", "beenden", "fertig", "datawatch schließen", "data watch schließen"),
    "QUESTIONS": (
        "fragen",
        "fragen vorlesen",
        "lies die fragen vor",
        "meine fragen",
        "gibt es fragen",
        "offene fragen",
        "erste frage",
        "die erste frage",
    ),
    "NEXT_QUESTION": ("nächste frage", "überspringen", "frage überspringen"),
    "OWN_WORDS": ("meine antwort", "in eigenen worten antworten"),
    # Only these send an answer, so there is no shorter form such as "ja".
    "CONFIRM": ("antwort bestätigen", "die antwort bestätigen", "meine antwort bestätigen"),
    # Like the answer, each of these sends one kind of thing and nothing else.
    "CONFIRM_AUTOMATON": (
        "automatisierung bestätigen",
        "automation bestätigen",
        "automat bestätigen",
        "automaten bestätigen",
    ),
    "CONFIRM_BUG": ("fehler bestätigen", "bug bestätigen"),
    "CONFIRM_SEND": ("senden bestätigen", "versand bestätigen"),
    "CANCEL": ("abbrechen", "antwort abbrechen", "die antwort abbrechen", "abbruch"),
    "ATTENTION": (
        "aufmerksamkeit",
        "was braucht aufmerksamkeit",
        "was braucht meine aufmerksamkeit",
    ),
    "PLANS": ("pläne", "pläne auflisten", "wie viele pläne", "wie viele pläne gibt es"),
    "OVERVIEW": ("übersicht", "projektübersicht"),
    "WHATS_NEXT": (
        "was kommt als nächstes",
        "was ist als nächstes dran",
        "was steht als nächstes an",
    ),
    "AUTOMATIONS": ("automatisierungen", "automatisierungen auflisten", "automationen"),
    "RUNNING": ("was läuft", "was läuft gerade", "laufende automaten"),
    "HELD": (
        "zurückgehaltene elemente",
        "zurückgehalten",
        "was ist zurückgehalten",
        "was wird zurückgehalten",
        "angehalten",
        "was ist angehalten",
    ),
    "WHY": (
        "warum",
        "warum ist es blockiert",
        "warum ist er blockiert",
        "warum ist es zurückgehalten",
        "warum wird es zurückgehalten",
        "warum ist es fehlgeschlagen",
        "warum hängt es",
    ),
    "TASKS": ("aufgaben", "aufgaben anzeigen", "zeig die aufgaben", "seine aufgaben"),
    "PROGRESS": ("fortschritt", "wie weit ist es", "wie läuft es"),
    "SESSIONS": ("sitzungen", "sitzungen auflisten", "liste die sitzungen auf"),
    "WAITING": ("wartende sitzungen", "was wartet", "was wartet auf eingabe"),
    "RUNNING_SESSIONS": ("laufende sitzungen", "welche sitzungen laufen"),
    "FAILED_SESSIONS": ("fehlgeschlagene sitzungen", "welche sitzungen sind fehlgeschlagen"),
    "FINISHED": ("was ist fertig", "was ist abgeschlossen", "abgeschlossen", "kürzlich fertig"),
    "RESULTS": ("ergebnisse", "die ergebnisse", "was wurde geliefert", "was wurde geändert"),
    "REPORTS": ("berichte", "berichte auflisten", "meine berichte"),
    "SET_THIS": ("setze es", "setz es", "setze das", "setz das", "fokus darauf"),
    "GO_BACK": ("zurück", "geh zurück", "eine ebene höher"),
    "ALL_QUESTIONS": ("alle fragen", "alle offenen fragen"),
    "ITS_QUESTIONS": ("fragen dazu", "seine fragen", "ihre fragen", "die fragen dazu"),
    "HISTORY": ("verlauf", "was ist passiert", "verlauf anzeigen", "entscheidungen"),
    "AUTOMATA": ("automaten", "automaten auflisten", "seine automaten", "automaten anzeigen"),
    "ALERTS": ("alarme", "alarme auflisten", "gibt es alarme", "meine alarme", "ungelesene alarme"),
    "ORDER": ("listenreihenfolge", "welche reihenfolge", "sortierreihenfolge"),
    "ORDER_NAME": ("nach namen sortieren", "nach name sortieren", "alphabetisch"),
    "ORDER_RECENT": ("neueste zuerst", "die neuesten zuerst", "nach neuesten sortieren"),
}

_UNITS = [
    "eins",
    "zwei",
    "drei",
    "vier",
    "fünf",
    "sechs",
    "sieben",
    "acht",
    "neun",
    "zehn",
    "elf",
    "zwölf",
    "dreizehn",
    "vierzehn",
    "fünfzehn",
    "sechzehn",
    "siebzehn",
    "achtzehn",
    "neunzehn",
]
# As normalise() writes them: "ß" becomes "ss".
_TENS = {"zwanzig": 20, "dreissig": 30, "vierzig": 40, "fünfzig": 50}
_BEFORE_AND = ["ein", *_UNITS[1:9]]
_NUMBERS = (
    {word: value for value, word in enumerate(_UNITS, start=1)}
    | _TENS
    | {
        joined: tens + value
        for ten, tens in _TENS.items()
        for value, unit in enumerate(_BEFORE_AND, start=1)
        for joined in (f"{unit}und{ten}", f"{unit} und {ten}")
    }
    | {"ein": 1, "eine": 1, "einen": 1, "zwo": 2}
)


def _starting(opening: str) -> re.Pattern[str]:
    """Words that open an action, matched on what speech-to-text wrote."""
    return re.compile(rf"^\W*(?:bitte\W+)?(?:{opening})\b[\s,:.\-]*", re.IGNORECASE)


_NUMBERED = r"(?:nummer )?(?P<chosen>.+)"

GRAMMAR = Grammar(
    phrases=_PHRASES,
    numbers=_NUMBERS,
    apostrophes="'\N{RIGHT SINGLE QUOTATION MARK}",
    polite=re.compile(r"^bitte | bitte$"),
    number=re.compile(_NUMBERED),
    own_words=re.compile(
        r"^\W*(?:bitte\W+)?meine\W+antwort\W+(?:ist|lautet)\b[\s,:.\-]*", re.IGNORECASE
    ),
    actions=(
        (
            "ADD_AUTOMATON",
            _starting(
                r"neue\W+(?:automatisierung|automation)|neuer\W+automat"
                r"|(?:automatisierung|automation|automat)\W+(?:hinzufügen|anlegen)"
                r"|(?:füge|lege)\W+(?:(?:eine|einen|neue|neuen)\W+){0,2}"
                r"(?:automatisierung|automation|automaten|automat)(?:\W+(?:hinzu|an))?"
            ),
        ),
        (
            "ADD_BUG",
            _starting(
                r"neuer\W+(?:fehler|bug)|(?:fehler|bug)\W+(?:melden|hinzufügen|erfassen)"
                r"|(?:melde|füge)\W+(?:(?:einen|neuen)\W+){0,2}(?:fehler|bug)(?:\W+hinzu)?"
            ),
        ),
        (
            "SEND_SESSION",
            _starting(
                r"an\W+(?:die\W+)?sitzung\W+senden|sende\W+an\W+(?:die\W+)?sitzung"
                r"|(?:befehl|nachricht)\W+senden|sag\W+der\W+sitzung"
            ),
        ),
    ),
    about_one=(
        (
            "WHY",
            re.compile(
                r"warum (?:(?:ist|wird|hängt) )?" + r"(?:nummer )?(?P<chosen>.+?)"
                r"(?: blockiert| zurückgehalten| angehalten| fehlgeschlagen| fest)?"
            ),
        ),
        (
            "TASKS",
            re.compile(r"(?:zeig(?:e)? (?:mir )?(?:die )?)?aufgaben (?:von|für|zu) " + _NUMBERED),
        ),
        ("PROGRESS", re.compile(r"(?:der )?fortschritt (?:von|für|bei|zu) " + _NUMBERED)),
        ("RESULTS", re.compile(r"(?:die )?ergebnisse (?:von|für|zu) " + _NUMBERED)),
        ("ITS_QUESTIONS", re.compile(r"(?:die )?fragen (?:zu|für|über|von) " + _NUMBERED)),
        ("HISTORY", re.compile(r"(?:der )?verlauf (?:von|für|zu) " + _NUMBERED)),
    ),
    about=re.compile(
        r"(?:(?:erzähl|erzähle|sag) (?:mir )?(?:etwas |mehr )?(?:über|von|zu)"
        r"|(?:details|mehr|infos|informationen) (?:zu|über)|was ist mit) " + _NUMBERED
    ),
    choose=re.compile(
        r"(?:(?:antworte|wähle|nimm) )?option (?:nummer )?(.+?)(?: wählen| nehmen)?"
        r"|(?:antworte|wähle|nimm) (.+)"
    ),
    set_command=re.compile(r"(?:setze|setz|setzen|fokus auf|fokussiere(?: auf)?) (?P<chosen>.+)"),
    set_item=re.compile(
        r"(?:den |die |das )?(?:fokus )?(?:auf )?(?:den |die |das )?"
        r"(?P<kind>plan|automatisierung|automaten|automat|aufgabe|sitzung) (?P<chosen>.+)"
    ),
    item_kinds={
        "plan": "plan",
        "automatisierung": "automation",
        "automat": "automaton",
        "automaten": "automaton",
        "aufgabe": "task",
        "sitzung": "session",
    },
    set_filler=re.compile(r"^(?:den )?(?:fokus )?(?:auf )?(?:den |die |das )?"),
    set_project=re.compile(r"projekt (?P<chosen>.+)"),
    report_filler=(
        re.compile(r"^(?:gib mir|lies mir|lies|starte|zeig mir)(?: meinen| den| die| das)? "),
        re.compile(r"^(?:meinen|meine|mein|der|die|das|den) "),
        re.compile(r" (?:bericht|report)$"),
    ),
    entry_sentences=(
        "(öffne|starte|nutze) (datawatch|data watch)",
        "(datawatch|data watch) (öffnen|starten)",
        "(datawatch|data watch)",
    ),
    entry_examples=("öffne datawatch", "datawatch öffnen", "datawatch"),
    entry_names=(
        "datawatch",
        "data watch",
        "öffne datawatch",
        "starte datawatch",
        "nutze datawatch",
        "datawatch öffnen",
        "datawatch starten",
    ),
)

LANGUAGE = Language(code="de", grammar=GRAMMAR, texts=TEXTS)
