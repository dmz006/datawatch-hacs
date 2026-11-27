"""French: what datawatch mode listens for. What it says is in fr_texts.py."""

from __future__ import annotations

import re

from ..grammar import Grammar, Language
from .fr_texts import TEXTS

# The first wording of each command is the one the replies quote. Spellings that sound the
# same are listed together, because speech-to-text may write any of them.
_PHRASES: dict[str, tuple[str, ...]] = {
    "STATUS": ("état", "quel est l'état", "donne-moi l'état", "statut"),
    "DETAIL": ("plus de détails", "détails", "dis-m'en plus"),
    "LIST_PROJECTS": ("liste des projets", "liste les projets", "projets", "mes projets"),
    "MORE": ("suite", "la suite", "suivants", "continue", "continuer"),
    "WHERE": ("où suis-je", "où en suis-je", "quel est mon focus", "quel est le focus"),
    "UNSET": ("retirer le focus", "retire le focus", "enlever le focus", "sans focus"),
    "REPEAT": ("répète", "répéter", "répétez", "redis-le", "encore une fois"),
    "HELP": ("aide", "que puis-je dire", "qu'est-ce que je peux dire"),
    "EXIT": ("stop", "arrête", "quitter", "terminé", "fermer datawatch", "ferme datawatch"),
    "QUESTIONS": (
        "questions",
        "lis les questions",
        "mes questions",
        "y a-t-il des questions",
        "questions ouvertes",
        "première question",
        "la première question",
    ),
    "NEXT_QUESTION": ("question suivante", "passer", "passer la question"),
    "OWN_WORDS": ("ma réponse", "répondre avec mes mots"),
    # Only these send an answer, so there is no shorter form such as "oui".
    "CONFIRM": (
        "confirmer la réponse",
        "confirme la réponse",
        "confirmez la réponse",
        "confirmer ma réponse",
        "confirmer réponse",
    ),
    # Like the answer, each of these sends one kind of thing and nothing else.
    "CONFIRM_AUTOMATON": (
        "confirmer l'automatisation",
        "confirme l'automatisation",
        "confirmez l'automatisation",
        "confirmer l'automate",
    ),
    "CONFIRM_BUG": ("confirmer le bug", "confirme le bug", "confirmez le bug"),
    "CONFIRM_SEND": ("confirmer l'envoi", "confirme l'envoi", "confirmez l'envoi"),
    "CANCEL": ("annuler", "annule", "annulez", "annuler la réponse"),
    "ATTENTION": ("à traiter", "a traiter", "qu'est-ce qui est à traiter"),
    "PLANS": ("plans", "liste des plans", "combien de plans", "combien y a-t-il de plans"),
    "OVERVIEW": ("vue d'ensemble", "vue d'ensemble du projet"),
    "WHATS_NEXT": ("quelle est la suite", "qu'est-ce qui vient ensuite", "à suivre"),
    "AUTOMATIONS": ("automatisations", "liste des automatisations"),
    "RUNNING": ("en cours", "qu'est-ce qui est en cours", "automates en cours"),
    "HELD": ("éléments retenus", "retenus", "qu'est-ce qui est retenu", "en attente"),
    "WHY": (
        "pourquoi",
        "pourquoi est-ce bloqué",
        "pourquoi est-il bloqué",
        "pourquoi est-il retenu",
        "pourquoi a-t-il échoué",
        "pourquoi est-il coincé",
    ),
    "TASKS": ("tâches", "montre les tâches", "liste des tâches", "ses tâches"),
    "PROGRESS": ("progression", "où en est-il", "comment ça avance"),
    "SESSIONS": ("sessions", "liste des sessions", "liste les sessions"),
    "WAITING": ("sessions en attente", "qu'est-ce qui attend", "qu'est-ce qui attend une saisie"),
    "RUNNING_SESSIONS": ("sessions en cours", "quelles sessions sont en cours"),
    "FAILED_SESSIONS": ("sessions en échec", "quelles sessions ont échoué"),
    "FINISHED": ("travaux terminés", "qu'est-ce qui est terminé", "récemment terminés"),
    "RESULTS": ("résultats", "les résultats", "qu'est-ce qui a été livré"),
    "REPORTS": ("rapports", "liste des rapports", "mes rapports"),
    "SET_THIS": ("sélectionne-le", "sélectionnez-le", "sélectionne ça", "focus dessus"),
    "GO_BACK": ("retour", "reviens", "revenir en arrière", "en arrière"),
    "ALL_QUESTIONS": ("toutes les questions", "toutes les questions ouvertes"),
    "ITS_QUESTIONS": ("ses questions", "les questions à ce sujet"),
    "HISTORY": ("historique", "que s'est-il passé", "voir l'historique", "décisions"),
    "AUTOMATA": ("automates", "liste des automates", "ses automates", "montre les automates"),
    "ALERTS": ("alertes", "liste des alertes", "mes alertes", "alertes non lues"),
    "ORDER": ("ordre des listes", "quel ordre", "quel est l'ordre"),
    "ORDER_NAME": ("trier par nom", "ordre alphabétique", "trie par nom"),
    "ORDER_RECENT": ("les plus récents d'abord", "plus récents d'abord", "trier par date"),
}

_UNITS = [
    "un",
    "deux",
    "trois",
    "quatre",
    "cinq",
    "six",
    "sept",
    "huit",
    "neuf",
    "dix",
    "onze",
    "douze",
    "treize",
    "quatorze",
    "quinze",
    "seize",
    "dix sept",
    "dix huit",
    "dix neuf",
]
_TENS = {"vingt": 20, "tren" + "te": 30, "quarante": 40, "cinquante": 50}
_NUMBERS = (
    {word: value for value, word in enumerate(_UNITS, start=1)}
    | _TENS
    | {
        f"{ten} {unit}": tens + value
        for ten, tens in _TENS.items()
        for value, unit in enumerate(_UNITS[1:9], start=2)
    }
    | {f"{ten} et {unit}": tens + 1 for ten, tens in _TENS.items() for unit in ("un", "une")}
    # "cet" is often written for "sept" said on its own.
    | {"une": 1, "cet": 7}
)


def _starting(opening: str) -> re.Pattern[str]:
    """Words that open an action, matched on what speech-to-text wrote."""
    return re.compile(rf"^\W*(?:{opening})\b[\s,:.\-]*", re.IGNORECASE)


_NUMBERED = r"(?:numéro )?(?P<chosen>.+)"
_OF = r"(?:du|de la|de) "
_PLEASE = r"(?:sil vous plaît|sil vous plait|sil te plaît|sil te plait|stp)"
_ADD = r"(?:ajoute|ajouter|ajoutez|crée|créer|créez)"

GRAMMAR = Grammar(
    phrases=_PHRASES,
    numbers=_NUMBERS,
    apostrophes="'\N{RIGHT SINGLE QUOTATION MARK}",
    polite=re.compile(rf"^{_PLEASE} | {_PLEASE}$"),
    number=re.compile(r"(?:(?:le )?numéro |le )?(?P<chosen>.+)"),
    own_words=re.compile(r"^\W*ma\W+réponse\W+est\b[\s,:.\-]*", re.IGNORECASE),
    actions=(
        (
            "ADD_AUTOMATON",
            _starting(
                r"nouvelle\W+automatisation|nouvel\W+automate|"
                + _ADD
                + r"\W+(?:(?:une|un|la|l|nouvelle|nouvel)\W+){0,2}(?:automatisation|automate)"
            ),
        ),
        (
            "ADD_BUG",
            _starting(
                r"nouveau\W+(?:bug|bogue)"
                r"|(?:ajoute|ajouter|ajoutez|signale|signaler|signalez|déclare|déclarer)\W+"
                r"(?:(?:un|nouveau|le)\W+){0,2}(?:bug|bogue)"
            ),
        ),
        (
            "SEND_SESSION",
            _starting(
                r"(?:envoie|envoyer|envoyez)\W+(?:à|a)\W+la\W+session"
                r"|(?:envoie|envoyer|envoyez)\W+(?:une\W+)?commande"
                r"|(?:dis|dire|dites)\W+à\W+la\W+session"
            ),
        ),
    ),
    about_one=(
        (
            "WHY",
            re.compile(
                r"pourquoi (?:est ce que )?(?:(?:le )?numéro |le |la )?(?P<chosen>.+?)"
                r"(?: (?:est (?:il |elle )?)?"
                r"(?:bloqué|bloquée|retenu|retenue|coincé|coincée|en échec)| a (?:il )?échoué)?"
            ),
        ),
        (
            "TASKS",
            re.compile(
                r"(?:(?:montre|affiche)(?: moi)? )?(?:les )?(?:tâches|taches) " + _OF + _NUMBERED
            ),
        ),
        ("PROGRESS", re.compile(r"(?:la )?progression " + _OF + _NUMBERED)),
        ("RESULTS", re.compile(r"(?:les )?résultats " + _OF + _NUMBERED)),
        ("ITS_QUESTIONS", re.compile(r"(?:les )?questions " + _OF + _NUMBERED)),
        ("HISTORY", re.compile(r"l?historique " + _OF + _NUMBERED)),
    ),
    about=re.compile(
        r"(?:(?:parle|parlez)(?: moi)? " + _OF + r"|(?:détails|informations|infos) "
        r"(?:sur le |sur |du |de )|à propos " + _OF + r")" + _NUMBERED
    ),
    choose=re.compile(
        r"(?:(?:réponds|répondre|choisis|choisir|choisissez) )?(?:la |l)?option (?:numéro )?(.+)"
        r"|(?:réponds|répondre|choisis|choisir|choisissez) (?:le )?(.+)"
    ),
    set_command=re.compile(r"(?:sélectionne|sélectionner|sélectionnez|focus sur) (?P<chosen>.+)"),
    set_item=re.compile(
        r"(?:le |la )?(?:focus )?(?:sur )?(?:le |la |l)?"
        r"(?P<kind>plan|automatisation|automate|tâche|tache|session) (?P<chosen>.+)"
    ),
    item_kinds={
        "plan": "plan",
        "automatisation": "automation",
        "automate": "automaton",
        "tâche": "task",
        "tache": "task",
        "session": "session",
    },
    set_filler=re.compile(r"^(?:le )?(?:focus )?(?:sur )?(?:le |la )?"),
    set_project=re.compile(r"projet (?P<chosen>.+)"),
    report_filler=(
        re.compile(r"^(?:donne moi|lis moi|lis|lance)(?: mon| le)? "),
        re.compile(r"^(?:mon|le) "),
        re.compile(r"^rapport (?:de )?"),
        re.compile(r" rapport$"),
    ),
    entry_sentences=(
        "(ouvre|ouvrir|ouvrez|lance|utilise) (datawatch|data watch)",
        "(datawatch|data watch)",
    ),
    entry_examples=("ouvre datawatch", "lance datawatch", "datawatch"),
    entry_names=(
        "datawatch",
        "data watch",
        "ouvre datawatch",
        "ouvrir datawatch",
        "ouvrez datawatch",
        "lance datawatch",
        "utilise datawatch",
    ),
)


# French treats nought like one: "0 session".
LANGUAGE = Language(code="fr", grammar=GRAMMAR, texts=TEXTS, singular=lambda number: number < 2)
