"""Spanish: what datawatch mode listens for. What it says is in es_texts.py."""

from __future__ import annotations

import re

from ..grammar import Grammar, Language
from .es_texts import TEXTS

# The first wording of each command is the one the replies quote.
_PHRASES: dict[str, tuple[str, ...]] = {
    "STATUS": ("estado", "cuál es el estado", "dame el estado"),
    "DETAIL": ("más detalles", "detalles", "cuéntame más"),
    "LIST_PROJECTS": ("listar proyectos", "lista los proyectos", "proyectos", "mis proyectos"),
    "MORE": ("más", "siguiente", "los siguientes", "sigue"),
    "WHERE": ("dónde estoy", "cuál es mi foco", "cuál es el foco"),
    "UNSET": ("quitar el foco", "quita el foco", "borrar el foco", "sin foco"),
    "REPEAT": ("repite", "repetir", "repítelo", "otra vez", "dilo otra vez"),
    "HELP": ("ayuda", "qué puedo decir"),
    "EXIT": ("salir", "para", "parar", "terminar", "cerrar datawatch", "cierra datawatch"),
    "QUESTIONS": (
        "preguntas",
        "lee las preguntas",
        "mis preguntas",
        "hay preguntas",
        "preguntas abiertas",
        "primera pregunta",
        "la primera pregunta",
    ),
    "NEXT_QUESTION": ("siguiente pregunta", "saltar", "saltar la pregunta"),
    "OWN_WORDS": ("mi respuesta", "responder con mis palabras"),
    # Only these send an answer, so there is no shorter form such as "sí".
    "CONFIRM": ("confirmar respuesta", "confirmar la respuesta", "confirma la respuesta"),
    # Like the answer, each of these sends one kind of thing and nothing else.
    "CONFIRM_AUTOMATON": (
        "confirmar automatización",
        "confirmar la automatización",
        "confirmar autómata",
    ),
    "CONFIRM_BUG": ("confirmar error", "confirmar el error", "confirmar bug"),
    "CONFIRM_SEND": ("confirmar envío", "confirmar el envío"),
    "CANCEL": ("cancelar", "cancela", "cancelar respuesta", "cancelar la respuesta"),
    "ATTENTION": ("atención", "qué requiere atención", "qué requiere mi atención"),
    "PLANS": ("planes", "listar planes", "cuántos planes", "cuántos planes hay"),
    "OVERVIEW": ("resumen", "resumen del proyecto"),
    "WHATS_NEXT": ("qué sigue", "qué es lo siguiente", "qué viene ahora"),
    "AUTOMATIONS": ("automatizaciones", "listar automatizaciones"),
    "RUNNING": ("en ejecución", "qué se está ejecutando", "autómatas en ejecución"),
    "HELD": ("elementos retenidos", "retenidos", "qué está retenido"),
    "WHY": (
        "por qué",
        "por qué está bloqueado",
        "por qué está retenido",
        "por qué ha fallado",
        "por qué está atascado",
    ),
    "TASKS": ("tareas", "muestra las tareas", "listar tareas", "sus tareas"),
    "PROGRESS": ("progreso", "cuánto lleva", "cómo va"),
    "SESSIONS": ("sesiones", "listar sesiones", "lista las sesiones"),
    "WAITING": ("sesiones en espera", "qué está esperando", "qué espera entrada"),
    "RUNNING_SESSIONS": ("sesiones en ejecución", "qué sesiones se están ejecutando"),
    "FAILED_SESSIONS": ("sesiones fallidas", "qué sesiones han fallado"),
    "FINISHED": ("qué ha terminado", "qué se ha completado", "terminados", "completados"),
    "RESULTS": ("resultados", "los resultados", "qué ha entregado", "qué ha cambiado"),
    "REPORTS": ("informes", "listar informes", "mis informes"),
    "SET_THIS": ("fíjalo", "fija eso", "fija ese", "pon el foco ahí"),
    "GO_BACK": ("volver", "atrás", "vuelve", "subir un nivel"),
    "ALL_QUESTIONS": ("todas las preguntas", "todas las preguntas abiertas"),
    "ITS_QUESTIONS": ("sus preguntas", "preguntas sobre eso"),
    "HISTORY": ("historial", "qué ha pasado", "ver historial", "decisiones"),
    "AUTOMATA": ("autómatas", "listar autómatas", "sus autómatas", "muestra los autómatas"),
    "ALERTS": ("alertas", "listar alertas", "hay alertas", "mis alertas", "alertas sin leer"),
    "ORDER": ("orden de las listas", "qué orden", "cuál es el orden"),
    "ORDER_NAME": ("ordenar por nombre", "orden alfabético", "ordena por nombre"),
    "ORDER_RECENT": ("más recientes primero", "los más recientes primero", "ordenar por fecha"),
}

_UNITS = [
    "uno",
    "dos",
    "tres",
    "cuatro",
    "cinco",
    "seis",
    "siete",
    "ocho",
    "nueve",
    "diez",
    "once",
    "doce",
    "trece",
    "catorce",
    "quince",
    "dieciséis",
    "diecisiete",
    "dieciocho",
    "diecinueve",
    "veinte",
    "veintiuno",
    "veintidós",
    "veintitrés",
    "veinticuatro",
    "veinticinco",
    "veintiséis",
    "veintisiete",
    "veintiocho",
    "veintinueve",
]
_TENS = {"treinta": 30, "cuarenta": 40, "cincuenta": 50}
_NUMBERS = (
    {word: value for value, word in enumerate(_UNITS, start=1)}
    | _TENS
    | {
        f"{ten} y {unit}": tens + value
        for ten, tens in _TENS.items()
        for value, unit in enumerate(_UNITS[:9], start=1)
    }
    # Before a noun, and as speech-to-text writes them without accents.
    | {"un": 1, "una": 1, "veintiún": 21, "dieciseis": 16}
    | {"veintidos": 22, "veintitres": 23, "veintiseis": 26}
)


def _starting(opening: str) -> re.Pattern[str]:
    """Words that open an action, matched on what speech-to-text wrote."""
    return re.compile(rf"^\W*(?:por\W+favor\W+)?(?:{opening})\b[\s,:.\-]*", re.IGNORECASE)


_NUMBERED = r"(?:número )?(?P<chosen>.+)"
_OF = r"(?:del|de la|de) "

GRAMMAR = Grammar(
    phrases=_PHRASES,
    numbers=_NUMBERS,
    apostrophes="'\N{RIGHT SINGLE QUOTATION MARK}",
    polite=re.compile(r"^por favor | por favor$"),
    number=re.compile(r"(?:(?:el )?número |el )?(?P<chosen>.+)"),
    own_words=re.compile(r"^\W*(?:por\W+favor\W+)?mi\W+respuesta\W+es\b[\s,:.\-]*", re.IGNORECASE),
    actions=(
        (
            "ADD_AUTOMATON",
            _starting(
                r"nueva\W+automatizaci[oó]n|nuevo\W+aut[oó]mata"
                r"|(?:añade|añadir|agrega|agregar|crea|crear)\W+"
                r"(?:(?:un|una|nuevo|nueva)\W+){0,2}(?:automatizaci[oó]n|aut[oó]mata)"
            ),
        ),
        (
            "ADD_BUG",
            _starting(
                r"nuevo\W+(?:error|bug|fallo)"
                r"|(?:añade|añadir|agrega|agregar|reporta|reportar|notifica|notificar"
                r"|registra|registrar|informa\W+de|informar\W+de)\W+"
                r"(?:(?:un|nuevo)\W+){0,2}(?:error|bug|fallo)"
            ),
        ),
        (
            "SEND_SESSION",
            _starting(
                r"(?:envía|envia|enviar|manda|mandar)\W+a\W+la\W+sesi[oó]n"
                r"|(?:envía|envia|enviar)\W+(?:un\W+)?(?:comando|mensaje)"
                r"|dile\W+a\W+la\W+sesi[oó]n"
            ),
        ),
    ),
    about_one=(
        (
            "WHY",
            re.compile(
                r"por qu[eé] (?:(?:está|se ha|ha|se) )?"
                r"(?:(?:bloquead[oa]|retenid[oa]|atascad[oa]|fallado) )?"
                r"(?:el |la )?(?:número )?(?P<chosen>.+?)"
                r"(?: está bloquead[oa]| está retenid[oa]| está atascad[oa]| ha fallado| falló)?"
            ),
        ),
        ("TASKS", re.compile(r"(?:(?:muestra|dime) )?(?:las )?tareas " + _OF + _NUMBERED)),
        ("PROGRESS", re.compile(r"(?:el )?progreso " + _OF + _NUMBERED)),
        ("RESULTS", re.compile(r"(?:los )?resultados " + _OF + _NUMBERED)),
        ("ITS_QUESTIONS", re.compile(r"(?:las )?preguntas " + _OF + _NUMBERED)),
        ("HISTORY", re.compile(r"(?:el )?historial " + _OF + _NUMBERED)),
    ),
    about=re.compile(
        r"(?:(?:háblame|cuéntame) (?:del|de la|de|sobre el|sobre)"
        r"|(?:información|detalles) (?:sobre el|sobre|del|de)|qué pasa con(?: el)?) " + _NUMBERED
    ),
    choose=re.compile(
        r"(?:(?:responde|elige|escoge|elegir)(?: la)? )?opción (?:número )?(.+)"
        r"|(?:responde|elige|escoge|elegir) (?:la |el )?(.+)"
    ),
    set_command=re.compile(
        r"(?:fija|fijar|enfoca|enfocar|selecciona|seleccionar|pon el foco en) (?P<chosen>.+)"
    ),
    set_item=re.compile(
        r"(?:el |la )?(?:foco )?(?:en )?(?:el |la )?"
        r"(?P<kind>plan|automatización|automatizacion|autómata|automata|tarea|sesión|sesion) "
        r"(?P<chosen>.+)"
    ),
    item_kinds={
        "plan": "plan",
        "automatización": "automation",
        "automatizacion": "automation",
        "autómata": "automaton",
        "automata": "automaton",
        "tarea": "task",
        "sesión": "session",
        "sesion": "session",
    },
    set_filler=re.compile(r"^(?:el )?(?:foco )?(?:en )?(?:el |la )?"),
    set_project=re.compile(r"proyecto (?P<chosen>.+)"),
    report_filler=(
        re.compile(r"^(?:dame|léeme|lee|ejecuta|pon)(?: mi| el)? "),
        re.compile(r"^(?:mi|el) "),
        re.compile(r"^informe (?:de )?"),
        re.compile(r" informe$"),
    ),
    entry_sentences=(
        "(abre|abrir|usa|inicia) (datawatch|data watch)",
        "(datawatch|data watch)",
    ),
    entry_examples=("abre datawatch", "usa datawatch", "datawatch"),
    entry_names=(
        "datawatch",
        "data watch",
        "abre datawatch",
        "abrir datawatch",
        "usa datawatch",
        "inicia datawatch",
    ),
)

LANGUAGE = Language(code="es", grammar=GRAMMAR, texts=TEXTS)
