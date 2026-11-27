"""Spanish: what datawatch mode says, keyed by the English sentence."""

TEXTS: dict[str, str] = {
    ", ": ", ",
    "A warning": "Una advertencia",
    "Added a draft automaton to project {project}, but I could not name it, so it may show "
    "as untitled. Do not add it again.": (
        "He añadido un autómata en borrador al proyecto {project}, pero no he podido ponerle "
        "nombre, así que puede aparecer sin título. No lo añadas otra vez."
    ),
    "Added a draft automaton to project {project}, named {title}. I did not ask datawatch "
    "to plan or start it.": (
        "He añadido un autómata en borrador al proyecto {project}, con el nombre {title}. No "
        "he pedido a datawatch que lo planifique ni que lo inicie."
    ),
    "All projects": "Todos los proyectos",
    "Also {number} archived.": "Además, archivados: {number}.",
    "An alert": "Una alerta",
    "An error": "Un error",
    "Answer sent. Say next question.": "Respuesta enviada. Di siguiente pregunta.",
    "Automation {line}": "Automatización {line}",
    "Automaton {title}: {state}.": "Autómata {title}: {state}.",
    "Back.": "Atrás.",
    "Bug reported for project {project}.": "Error notificado para el proyecto {project}.",
    "Cancelled. Nothing was sent.": "Cancelado. No se ha enviado nada.",
    "Choose a session first: say sessions, then its number.": (
        "Primero elige una sesión: di sesiones y después su número."
    ),
    "Choose something first, then say history.": "Primero elige algo y después di historial.",
    "Choose something first, then say its questions. Or say questions.": (
        "Primero elige algo y después di sus preguntas. O di preguntas."
    ),
    "Choose something first: say its number, then set it.": (
        "Primero elige algo: di su número y después fíjalo."
    ),
    "Closing datawatch.": "Cerrando datawatch.",
    "Datawatch activated.": "Datawatch activado.",
    "Datawatch mode works from a voice device.": (
        "El modo datawatch funciona desde un dispositivo de voz."
    ),
    "Elsewhere: {counts}.": "En otros sitios: {counts}.",
    "Focus cleared. Now showing everything.": "Foco quitado. Ahora se muestra todo.",
    "Focus: {focus}.": "Foco: {focus}.",
    "For a full reason say why and its number.": (
        "Para oír un motivo completo, di por qué y su número."
    ),
    "For the task {title}: {reason}": "Sobre la tarea {title}: {reason}",
    "For the {item}.": "Para: {item}.",
    "For the {item}: {number} unread alert, newest first.": (
        "Para {item}: {number} alerta sin leer, primero la más reciente."
    ),
    "For the {item}: {number} unread alerts, newest first.": (
        "Para {item}: {number} alertas sin leer, primero las más recientes."
    ),
    "Go ahead. Describe the bug, or cancel.": "Adelante. Describe el error, o di cancelar.",
    "Go ahead. Say what the automation should do, or cancel.": (
        "Adelante. Di qué debe hacer la automatización, o di cancelar."
    ),
    "Go ahead. Say what to send, or cancel.": "Adelante. Di qué quieres enviar, o di cancelar.",
    "Go ahead. Say your answer, or cancel.": "Adelante. Di tu respuesta, o di cancelar.",
    "I can read the first {number}.": "Puedo leer los primeros {number}.",
    "I can't reach datawatch, so nothing was sent. Say it again.": (
        "No puedo conectar con datawatch, así que no se ha enviado nada. Dilo otra vez."
    ),
    "I can't reach datawatch, so nothing was sent. Say my answer or option again.": (
        "No puedo conectar con datawatch, así que no se ha enviado nada. Di otra vez mi "
        "respuesta o una opción."
    ),
    "I can't reach datawatch. Try again, or say stop.": (
        "No puedo conectar con datawatch. Inténtalo otra vez, o di salir."
    ),
    "I can't read a session's history by voice. Open it in datawatch.": (
        "No puedo leer por voz el historial de una sesión. Ábrela en datawatch."
    ),
    "I couldn't find a plan matching {name}.": (
        "No he encontrado ningún plan que coincida con {name}."
    ),
    "I couldn't find a project matching {name}. Say list projects.": (
        "No he encontrado ningún proyecto que coincida con {name}. Di listar proyectos."
    ),
    "I couldn't find a session matching {name}.": (
        "No he encontrado ninguna sesión que coincida con {name}."
    ),
    "I couldn't find a task matching {name}.": (
        "No he encontrado ninguna tarea que coincida con {name}."
    ),
    "I couldn't find an automation matching {name}.": (
        "No he encontrado ninguna automatización que coincida con {name}."
    ),
    "I couldn't find an automaton matching {name}.": (
        "No he encontrado ningún autómata que coincida con {name}."
    ),
    "I couldn't find {name} among the automata that need attention, are running, are on "
    "hold or finished recently.": (
        "No he encontrado {name} entre los autómatas que requieren atención, están en "
        "ejecución, están retenidos o han terminado hace poco."
    ),
    "I did not keep your words.": "No he guardado tus palabras.",
    "I didn't understand three times. Closing datawatch.": (
        "No te he entendido tres veces. Cerrando datawatch."
    ),
    "I don't know whether it was sent. Check datawatch before saying it again.": (
        "No sé si se ha enviado. Compruébalo en datawatch antes de decirlo otra vez."
    ),
    "I don't know whether the answer was sent. Say questions to check.": (
        "No sé si se ha enviado la respuesta. Di preguntas para comprobarlo."
    ),
    "I found {number} matches.": "He encontrado {number} coincidencias.",
    "I found {number} matches. Say set and a number.": (
        "He encontrado {number} coincidencias. Di fija y un número."
    ),
    "I found {number} matching {name}. Say a number.": (
        "He encontrado {number} coincidencias con {name}. Di un número."
    ),
    "I haven't read a number {number}. Say more, or pick a number you heard.": (
        "No he leído ningún número {number}. Di más, o elige un número que hayas oído."
    ),
    "I haven't read a number {number}. Say more, or pick one you heard.": (
        "No he leído ningún número {number}. Di más, o elige uno que hayas oído."
    ),
    "I haven't read a question yet. Say questions.": (
        "Todavía no he leído ninguna pregunta. Di preguntas."
    ),
    "In project {project}: {lead}{counts} across all projects.": (
        "En el proyecto {project}: {lead}{counts} en todos los proyectos."
    ),
    "In project {project}: {lead}{counts}.": "En el proyecto {project}: {lead}{counts}.",
    "In the automaton {title}.": "En el autómata {title}.",
    "It changed {files} in {packages}, and added {tests}.": (
        "Ha cambiado {files} en {packages} y ha añadido {tests}."
    ),
    "It has no tasks.": "No tiene tareas.",
    "It has {number} member.": "Tiene {number} miembro.",
    "It has {number} members.": "Tiene {number} miembros.",
    "It is blocking work.": "Está bloqueando trabajo.",
    "It is on hold: {reason}": "Está retenido: {reason}",
    "It uses {backend}.": "Usa {backend}.",
    "Its description": "Su descripción",
    "Its goal": "Su objetivo",
    "Its goal: {goal}.": "Su objetivo: {goal}.",
    "Last activity {when}.": "Última actividad {when}.",
    "New work is paused.": "El trabajo nuevo está en pausa.",
    "Next: {title}, in the plan {plan}.": "Siguiente: {title}, en el plan {plan}.",
    "Next: {title}.": "Siguiente: {title}.",
    "No automata are running across all projects.": (
        "No hay autómatas en ejecución en ningún proyecto."
    ),
    "No automata are running in project {project}.": (
        "No hay autómatas en ejecución en el proyecto {project}."
    ),
    "No automata have completed across all projects.": (
        "No ha terminado ningún autómata en ningún proyecto."
    ),
    "No automata have completed in project {project}.": (
        "No ha terminado ningún autómata en el proyecto {project}."
    ),
    "No focus. Showing everything.": "Sin foco. Se muestra todo.",
    "No reason given": "No se indica ningún motivo",
    "Not sent yet.": "Todavía no se ha enviado.",
    "Not sent yet. Say confirm answer, or cancel.": (
        "Todavía no se ha enviado. Di confirmar respuesta, o cancelar."
    ),
    "Not sent yet. Say confirm automation, or cancel.": (
        "Todavía no se ha enviado. Di confirmar automatización, o cancelar."
    ),
    "Not sent yet. Say confirm bug, or cancel.": (
        "Todavía no se ha enviado. Di confirmar error, o cancelar."
    ),
    "Not sent yet. Say confirm send, or cancel.": (
        "Todavía no se ha enviado. Di confirmar envío, o cancelar."
    ),
    "Not sent yet. This is {target}. Your words: {words}": (
        "Todavía no se ha enviado. Es {target}. Tus palabras: {words}"
    ),
    "Nothing is marked as next in any project.": (
        "No hay nada marcado como siguiente en ningún proyecto."
    ),
    "Nothing is marked as next.": "No hay nada marcado como siguiente.",
    "Nothing is on hold.": "No hay nada retenido.",
    "Nothing needs your attention.": "Nada requiere tu atención.",
    "Number {number} is the {item}. Say set {number}.": (
        "El número {number} es: {item}. Di fija {number}."
    ),
    "Option {number}: {label}": "Opción {number}: {label}",
    "Order: by name, for sessions, automations and running work. Say the list again to "
    "hear it that way. Say most recent first to switch.": (
        "Orden: por nombre, para sesiones, automatizaciones y trabajo en ejecución. Pide la "
        "lista otra vez para oírla así. Para cambiar, di más recientes primero."
    ),
    "Order: most recent first, for sessions, automations and running work. Say the list "
    "again to hear it that way. Say sort by name to switch.": (
        "Orden: más recientes primero, para sesiones, automatizaciones y trabajo en ejecución. "
        "Pide la lista otra vez para oírla así. Para cambiar, di ordenar por nombre."
    ),
    "Plan {line}.": "Plan {line}.",
    "Plan {number}, {line}.": "Plan {number}, {line}.",
    "Project {project}": "Proyecto {project}",
    "Project {project} has no current plans.": "El proyecto {project} no tiene planes actuales.",
    "Project {project} has {number} current plan.": (
        "El proyecto {project} tiene {number} plan actual."
    ),
    "Project {project} has {number} current plans.": (
        "El proyecto {project} tiene {number} planes actuales."
    ),
    "Project {project} no longer exists, so the focus is cleared.": (
        "El proyecto {project} ya no existe, así que se ha quitado el foco."
    ),
    "Project {project}.": "Proyecto {project}.",
    "Project {project}. {next}": "Proyecto {project}. {next}",
    "Project {project}: {plans}.": "Proyecto {project}: {plans}.",
    "Question {number} of {total}, from datawatch.": "Pregunta {number} de {total}, de datawatch.",
    "Question {number} of {total}, from the supervisor.": (
        "Pregunta {number} de {total}, del supervisor."
    ),
    "Reason: {reason}": "Motivo: {reason}",
    "Say attention, running or held items, then a number.": (
        "Di atención, en ejecución o elementos retenidos, y después un número."
    ),
    "Say confirm answer to send it, or cancel.": (
        "Di confirmar respuesta para enviarla, o cancelar."
    ),
    "Say confirm automation to send it, or cancel.": (
        "Di confirmar automatización para enviarla, o cancelar."
    ),
    "Say confirm bug to send it, or cancel.": "Di confirmar error para enviarlo, o cancelar.",
    "Say confirm send to send it, or cancel.": "Di confirmar envío para enviarlo, o cancelar.",
    "Say more detail for more.": "Di más detalles para saber más.",
    "Say more, or set and a number or name.": "Di más, o fija y un número o un nombre.",
    "Say more, or which number?": "¿Di más, o qué número?",
    "Say more.": "Di más.",
    "Say option and a number, my answer, more detail, or next question.": (
        "Di opción y un número, mi respuesta, más detalles o siguiente pregunta."
    ),
    "Say plans or automations, choose one, then say automata.": (
        "Di planes o automatizaciones, elige algo y después di autómatas."
    ),
    "Say why, or tasks.": "Di por qué, o tareas.",
    "Sending to a session is not turned on yet. It is waiting for datawatch's access "
    "controls. Nothing was sent.": (
        "El envío a una sesión todavía no está activado. Está a la espera de los controles de "
        "acceso de datawatch. No se ha enviado nada."
    ),
    "Sent to the {item}.": "Enviado a: {item}.",
    "Session named {name}: {state}.": "Sesión llamada {name}: {state}.",
    "Sessions, automations and running work are listed by name. Say most recent first to switch.": (
        "Las sesiones, las automatizaciones y el trabajo en ejecución se listan por nombre. "
        "Para cambiar, di más recientes primero."
    ),
    "Sessions, automations and running work are listed most recent first. Say sort by name "
    "to switch.": (
        "Las sesiones, las automatizaciones y el trabajo en ejecución se listan con los más "
        "recientes primero. Para cambiar, di ordenar por nombre."
    ),
    "Set a plan or an automaton first, then set the task.": (
        "Primero fija un plan o un autómata y después fija la tarea."
    ),
    "Set a project first: say list projects, or set and a project name.": (
        "Primero fija un proyecto: di listar proyectos, o fija y el nombre de un proyecto."
    ),
    "Something went wrong in datawatch mode. Closing datawatch.": (
        "Algo ha fallado en el modo datawatch. Cerrando datawatch."
    ),
    "Sorry, I didn't get that. Say help.": "Perdona, no lo he entendido. Di ayuda.",
    "Still there?": "¿Sigues ahí?",
    "Task {number}, {title}: {state}.": "Tarea {number}, {title}: {state}.",
    "Task {title}: {state}.": "Tarea {title}: {state}.",
    "Tasks are listed for a plan or an automaton.": (
        "Las tareas se listan para un plan o un autómata."
    ),
    "That is a session. I can only say what is in the list and its details.": (
        "Eso es una sesión. Solo puedo decir lo que aparece en la lista y sus detalles."
    ),
    "That is all.": "Eso es todo.",
    "That is the end of the list.": "Ese es el final de la lista.",
    "That is the last question.": "Esa es la última pregunta.",
    "That question was already answered or withdrawn. Nothing was sent.": (
        "Esa pregunta ya se había respondido o retirado. No se ha enviado nada."
    ),
    "That session is {state} now, not waiting for input. Nothing was sent.": (
        "El estado de esa sesión ahora es {state}, no está esperando entrada. No se ha enviado "
        "nada."
    ),
    "The asker recommends option {number}.": "Quien pregunta recomienda la opción {number}.",
    "The automation {title}": "La automatización {title}",
    "The automaton {title}": "El autómata {title}",
    "The datawatch certificate has changed. Check it in Home Assistant. Closing datawatch.": (
        "El certificado de datawatch ha cambiado. Compruébalo en Home Assistant. Cerrando "
        "datawatch."
    ),
    "The most recently updated come first, which may not be the order they finished.": (
        "Primero van los actualizados más recientemente, que puede no ser el orden en que "
        "terminaron."
    ),
    "The plan {title}": "El plan {title}",
    "The question begins: {words}": "La pregunta empieza así: {words}",
    "The rest: {parts}.": "El resto: {parts}.",
    "The {item}": "{item}",
    "There are no current plans.": "No hay planes actuales.",
    "There are no open questions.": "No hay preguntas abiertas.",
    "There are no projects.": "No hay proyectos.",
    "There are no unread alerts.": "No hay alertas sin leer.",
    "There are no waiting, running or failed sessions.": (
        "No hay sesiones en espera, en ejecución ni fallidas."
    ),
    "There is no answer waiting.": "No hay ninguna respuesta esperando.",
    "There is no list yet. Say list projects.": (
        "Todavía no hay ninguna lista. Di listar proyectos."
    ),
    "There is no option {number}.": "No existe la opción {number}.",
    "There is nothing to go back to.": "No hay nada a lo que volver.",
    "There is nothing waiting to be sent.": "No hay nada esperando a ser enviado.",
    "This question has no more detail.": "Esta pregunta no tiene más detalles.",
    "This voice device can't hold a datawatch conversation.": (
        "Este dispositivo de voz no puede mantener una conversación de datawatch."
    ),
    "To read the rest, open datawatch.": "Para leer el resto, abre datawatch.",
    "To see what it said, open it in datawatch.": "Para ver lo que ha dicho, ábrela en datawatch.",
    "What it is for": "Para qué es",
    "Which number?": "¿Qué número?",
    "Why the asker recommends it: {reason}": "Por qué la recomienda quien pregunta: {reason}",
    "You can say: questions, next question, option and a number, my answer, confirm "
    "answer, cancel, status, more detail, attention, running, held items, tell me about a "
    "number or name, why, tasks, progress, results, what finished, sessions, waiting "
    "sessions, running sessions, failed sessions, plans, overview, what's next, "
    "automations, reports or a report's name, list projects, more, set and a number or "
    "name, set it, its questions, all questions, automata, history, add automation, add "
    "bug, send to session, go back, where am I, alerts, list order, sort by name, most "
    "recent first, unset, repeat, or stop.": (
        "Puedes decir: preguntas, siguiente pregunta, opción y un número, mi respuesta, "
        "confirmar respuesta, cancelar, estado, más detalles, atención, en ejecución, "
        "elementos retenidos, háblame de un número o un nombre, por qué, tareas, progreso, "
        "resultados, qué ha terminado, sesiones, sesiones en espera, sesiones en ejecución, "
        "sesiones fallidas, planes, resumen, qué sigue, automatizaciones, informes o el nombre "
        "de un informe, listar proyectos, más, fija y un número o un nombre, fíjalo, sus "
        "preguntas, todas las preguntas, autómatas, historial, nueva automatización, informar "
        "de un error, enviar a la sesión, volver, dónde estoy, alertas, orden de las listas, "
        "ordenar por nombre, más recientes primero, quitar el foco, repite o salir."
    ),
    "You have no reports yet. Add one on the datawatch page in Home Assistant.": (
        "Todavía no tienes informes. Añade uno en la página de datawatch en Home Assistant."
    ),
    "You have {number} report: {names}. Say a name.": (
        "Tienes {number} informe: {names}. Di un nombre."
    ),
    "You have {number} reports: {names}. Say a name.": (
        "Tienes {number} informes: {names}. Di un nombre."
    ),
    "Your answer was not sent.": "Tu respuesta no se ha enviado.",
    "Your assistant didn't answer. Try again, or say stop.": (
        "Tu asistente no ha respondido. Inténtalo otra vez, o di salir."
    ),
    "Your assistant had nothing to say.": "Tu asistente no tenía nada que decir.",
    "Your automation was not sent.": "Tu automatización no se ha enviado.",
    "Your bug was not sent.": "Tu informe de error no se ha enviado.",
    "Your choice: option {number}, {label}": "Has elegido: opción {number}, {label}",
    "Your message was not sent.": "Tu mensaje no se ha enviado.",
    "Your words: {words}": "Tus palabras: {words}",
    "a bug for project {project}": "un error para el proyecto {project}",
    "a message to the {item}": "un mensaje para: {item}",
    "a new draft automaton in project {project}": (
        "un autómata nuevo en borrador en el proyecto {project}"
    ),
    "active": "activo",
    "active {when}": "actividad {when}",
    "all new work is paused.": "todo el trabajo nuevo está en pausa.",
    "approved": "aprobado",
    "archived": "archivado",
    "at least {count}": "al menos {count}",
    "automation {title}": "automatización {title}",
    "automaton {title}": "autómata {title}",
    "awaiting approval": "pendiente de aprobación",
    "blocked": "con bloqueo",
    "cancelled": "cancelado",
    "completed": "completado",
    "datawatch added it to an open draft bug group.": (
        "datawatch lo ha añadido a un grupo de errores en borrador ya abierto."
    ),
    "datawatch did not accept it, so nothing was sent. The session may be showing a prompt "
    "to answer in datawatch.": (
        "datawatch no lo ha aceptado, así que no se ha enviado nada. Puede que la sesión esté "
        "mostrando una petición que hay que responder en datawatch."
    ),
    "datawatch did not accept it. Nothing was sent.": (
        "datawatch no lo ha aceptado. No se ha enviado nada."
    ),
    "datawatch gives no folder for project {project}. Nothing was sent.": (
        "datawatch no indica ninguna carpeta para el proyecto {project}. No se ha enviado nada."
    ),
    "datawatch gives no history for a plan.": "datawatch no da historial de un plan.",
    "datawatch gives no reason.": "datawatch no indica ningún motivo.",
    "datawatch has no change record for it.": "datawatch no tiene registro de cambios de esto.",
    "datawatch has no history for {title}.": "datawatch no tiene historial de {title}.",
    "datawatch links no open questions to the {item}. There are {number} open questions in "
    "all. Say all questions.": (
        "datawatch no vincula ninguna pregunta abierta con: {item}. En total hay {number} "
        "preguntas abiertas. Di todas las preguntas."
    ),
    "datawatch links no open questions to the {item}. There is {number} open question in "
    "all. Say all questions.": (
        "datawatch no vincula ninguna pregunta abierta con: {item}. En total hay {number} "
        "pregunta abierta. Di todas las preguntas."
    ),
    "datawatch links no unread alerts to the {item}. There are {number} unread alerts in "
    "all. Say unset, then alerts.": (
        "datawatch no vincula ninguna alerta sin leer con: {item}. En total hay {number} "
        "alertas sin leer. Di quitar el foco y después alertas."
    ),
    "datawatch links no unread alerts to the {item}. There is {number} unread alert in "
    "all. Say unset, then alerts.": (
        "datawatch no vincula ninguna alerta sin leer con: {item}. En total hay {number} "
        "alerta sin leer. Di quitar el foco y después alertas."
    ),
    "datawatch made a new draft bug group for it.": (
        "datawatch ha creado un nuevo grupo de errores en borrador."
    ),
    "datawatch made a one-task draft for it.": "datawatch ha creado un borrador de una sola tarea.",
    "datawatch no longer has that session. Nothing was sent.": (
        "datawatch ya no tiene esa sesión. No se ha enviado nada."
    ),
    "datawatch no longer has the project {project}. Nothing was sent.": (
        "datawatch ya no tiene el proyecto {project}. No se ha enviado nada."
    ),
    "datawatch no longer has the {item}, so I moved your focus up.": (
        "datawatch ya no tiene esto: {item}. He subido tu foco un nivel."
    ),
    "datawatch no longer has the {item}.": "datawatch ya no tiene esto: {item}.",
    "datawatch records history for an automaton, not for one task. Choose its automaton to "
    "hear it.": (
        "datawatch guarda el historial de un autómata, no de una tarea. Elige su autómata para "
        "oírlo."
    ),
    "datawatch refused access. Check the token in Home Assistant. Closing datawatch.": (
        "datawatch ha denegado el acceso. Comprueba el token en Home Assistant. Cerrando datawatch."
    ),
    "datawatch refused that answer because it looks like it holds a secret. Nothing was sent.": (
        "datawatch ha rechazado esa respuesta porque parece contener un secreto. No se ha "
        "enviado nada."
    ),
    "datawatch refused that answer. Nothing was sent.": (
        "datawatch ha rechazado esa respuesta. No se ha enviado nada."
    ),
    "datawatch says: {reason}": "datawatch dice: {reason}",
    "datawatch's bug intake is turned off for project {project}. Nothing was sent.": (
        "El registro de errores de datawatch está desactivado en el proyecto {project}. No se "
        "ha enviado nada."
    ),
    "done": "hecho",
    "draft": "en borrador",
    "error": "error",
    "failed": "con fallo",
    "held": "retenido",
    "in progress": "en curso",
    "just now": "ahora mismo",
    "not shipped": "sin publicar",
    "not started": "sin empezar",
    "paused": "en pausa",
    "plan {title}": "plan {title}",
    "planning": "en planificación",
    "project {project}": "proyecto {project}",
    "queued": "en cola",
    "review needed": "pendiente de revisión",
    "running": "en ejecución",
    "session {title}": "sesión {title}",
    "shipped": "publicado",
    "shipped in {release}": "publicado en {release}",
    "task {title}": "tarea {title}",
    "unknown": "desconocido",
    "unnamed": "sin nombre",
    "untitled": "sin título",
    "waiting decision": "pendiente de decisión",
    "waiting for input": "en espera de entrada",
    "waiting for review": "pendiente de revisar",
    "warning": "advertencia",
    "{counts} across all projects.": "{counts} en todos los proyectos.",
    "{done} of {number} task completed.": "{done} de {number} tarea completada.",
    "{done} of {number} tasks completed.": "{done} de {number} tareas completadas.",
    "{done} of {total} automata done": "{done} de {total} autómatas terminados",
    "{done} of {total} automata done.": "{done} de {total} autómatas terminados.",
    "{done} of {total} tasks completed": "{done} de {total} tareas completadas",
    "{first} and {last}": "{first} y {last}",
    "{found} among the newest {number}": "{found} entre las {number} más recientes",
    "{kind} from {when}": "{kind}, {when}",
    "{lead}{counts}.": "{lead}{counts}.",
    "{name} has no automata.": "{name} no tiene autómatas.",
    "{name} has no tasks.": "{name} no tiene tareas.",
    "{name} has nothing in it. Change it on the datawatch page in Home Assistant.": (
        "{name} no tiene nada. Cámbialo en la página de datawatch en Home Assistant."
    ),
    "{name} has {number} automata.": "{name} tiene {number} autómatas.",
    "{name} has {number} automaton.": "{name} tiene {number} autómata.",
    "{name} has {number} task.": "{name} tiene {number} tarea.",
    "{name} has {number} tasks.": "{name} tiene {number} tareas.",
    "{number} automata are running across all projects.": (
        "{number} autómatas están en ejecución en todos los proyectos."
    ),
    "{number} automata are running in project {project}.": (
        "{number} autómatas están en ejecución en el proyecto {project}."
    ),
    "{number} automata have completed across all projects.": (
        "{number} autómatas han terminado en todos los proyectos."
    ),
    "{number} automata have completed in project {project}.": (
        "{number} autómatas han terminado en el proyecto {project}."
    ),
    "{number} automata need attention, across all projects: {parts}.": (
        "{number} autómatas requieren atención, en todos los proyectos: {parts}."
    ),
    "{number} automaton has completed across all projects.": (
        "{number} autómata ha terminado en todos los proyectos."
    ),
    "{number} automaton has completed in project {project}.": (
        "{number} autómata ha terminado en el proyecto {project}."
    ),
    "{number} automaton is running across all projects.": (
        "{number} autómata está en ejecución en todos los proyectos."
    ),
    "{number} automaton is running in project {project}.": (
        "{number} autómata está en ejecución en el proyecto {project}."
    ),
    "{number} automaton needs attention, across all projects: {parts}.": (
        "{number} autómata requiere atención, en todos los proyectos: {parts}."
    ),
    "{number} current plan": "{number} plan actual",
    "{number} current plans": "{number} planes actuales",
    "{number} day ago": "hace {number} día",
    "{number} days ago": "hace {number} días",
    "{number} failed or blocked automata": "{number} autómatas fallidos o bloqueados",
    "{number} failed or blocked automaton": "{number} autómata fallido o bloqueado",
    "{number} failed session": "{number} sesión fallida",
    "{number} failed sessions": "{number} sesiones fallidas",
    "{number} file": "{number} archivo",
    "{number} files": "{number} archivos",
    "{number} finished or set aside with tasks held for review": (
        "{number} terminados o apartados con tareas retenidas para revisión"
    ),
    "{number} held item": "{number} elemento retenido",
    "{number} held items": "{number} elementos retenidos",
    "{number} hour ago": "hace {number} hora",
    "{number} hours ago": "hace {number} horas",
    "{number} item is on hold, across all projects.": (
        "Hay {number} elemento retenido, en todos los proyectos."
    ),
    "{number} items are on hold, across all projects.": (
        "Hay {number} elementos retenidos, en todos los proyectos."
    ),
    "{number} member": "{number} miembro",
    "{number} members": "{number} miembros",
    "{number} minute ago": "hace {number} minuto",
    "{number} minutes ago": "hace {number} minutos",
    "{number} not started": "{number} sin empezar",
    "{number} open question": "{number} pregunta abierta",
    "{number} open question, across all projects.": (
        "{number} pregunta abierta, en todos los proyectos."
    ),
    "{number} open questions": "{number} preguntas abiertas",
    "{number} open questions, across all projects.": (
        "{number} preguntas abiertas, en todos los proyectos."
    ),
    "{number} package": "{number} paquete",
    "{number} packages": "{number} paquetes",
    "{number} plan": "{number} plan",
    "{number} plans": "{number} planes",
    "{number} plans archived.": "Planes archivados: {number}.",
    "{number} project": "{number} proyecto",
    "{number} project has something next.": "{number} proyecto tiene algo como siguiente.",
    "{number} projects": "{number} proyectos",
    "{number} projects have something next.": "{number} proyectos tienen algo como siguiente.",
    "{number} running": "{number} en ejecución",
    "{number} session waiting for input": "{number} sesión esperando entrada",
    "{number} sessions waiting for input": "{number} sesiones esperando entrada",
    "{number} task held for review": "{number} tarea retenida para revisión",
    "{number} task is stuck. First: {title}, {state}.": (
        "{number} tarea está atascada. La primera: {title}, {state}."
    ),
    "{number} tasks are stuck. First: {title}, {state}.": (
        "{number} tareas están atascadas. La primera: {title}, {state}."
    ),
    "{number} tasks held for review": "{number} tareas retenidas para revisión",
    "{number} test": "{number} prueba",
    "{number} tests": "{number} pruebas",
    "{number} unread alert, across all projects, newest first.": (
        "{number} alerta sin leer, en todos los proyectos, primero la más reciente."
    ),
    "{number} unread alerts, across all projects, newest first.": (
        "{number} alertas sin leer, en todos los proyectos, primero las más recientes."
    ),
    "{number} warning or error": "{number} advertencia o error",
    "{number} warnings or errors": "{number} advertencias o errores",
    "{number} {state}": "{number} {state}",
    "{number}, session named {name}, {state}": "{number}, sesión llamada {name}, {state}",
    "{plans} in {projects}.": "{plans} en {projects}.",
    "{start}, and more": "{start}, y más",
    "{start}, and more. See datawatch for the rest.": (
        "{start}, y más. Consulta el resto en datawatch."
    ),
    "{title} has no tasks.": "{title} no tiene tareas.",
    "{title} has {number} entries. The latest: {lines}": (
        "{title} tiene {number} entradas. Las últimas: {lines}"
    ),
    "{title} has {number} entry. The latest: {lines}": (
        "{title} tiene {number} entrada. La última: {lines}"
    ),
    "{title} is {state}.": "{title}: {state}.",
    "{what}, by {actor}": "{what}, por {actor}",
    "{where}: no automations.": "{where}: no hay automatizaciones.",
    "{where}: sessions, {counts}.": "{where}: sesiones, {counts}.",
    "{where}: {number} automation, {parts}.": "{where}: {number} automatización, {parts}.",
    "{where}: {number} automations, {parts}.": "{where}: {number} automatizaciones, {parts}.",
}
