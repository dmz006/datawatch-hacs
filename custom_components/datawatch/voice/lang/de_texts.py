"""German: what datawatch mode says, keyed by the English sentence."""

TEXTS: dict[str, str] = {
    ", ": ", ",
    "A warning": "Eine Warnung",
    "Added a draft automaton to project {project}, but I could not name it, so it may show "
    "as untitled. Do not add it again.": (
        "Ich habe dem Projekt {project} einen Automaten als Entwurf hinzugefügt, konnte ihn "
        "aber nicht benennen. Er wird vielleicht ohne Titel angezeigt. Füge ihn nicht noch "
        "einmal hinzu."
    ),
    "Added a draft automaton to project {project}, named {title}. I did not ask datawatch "
    "to plan or start it.": (
        "Ich habe dem Projekt {project} einen Automaten als Entwurf hinzugefügt, mit dem Namen "
        "{title}. Ich habe datawatch nicht gebeten, ihn zu planen oder zu starten."
    ),
    "All projects": "Alle Projekte",
    "Also {number} archived.": "Außerdem {number} archiviert.",
    "An alert": "Ein Alarm",
    "An error": "Ein Fehler",
    "Answer sent. Say next question.": "Antwort gesendet. Sag nächste Frage.",
    "Automation {line}": "Automatisierung {line}",
    "Automaton {title}: {state}.": "Automat {title}: {state}.",
    "Back.": "Zurück.",
    "Bug reported for project {project}.": "Fehler für das Projekt {project} gemeldet.",
    "Cancelled. Nothing was sent.": "Abgebrochen. Nichts wurde gesendet.",
    "Choose a session first: say sessions, then its number.": (
        "Wähle zuerst eine Sitzung: sag Sitzungen und dann ihre Nummer."
    ),
    "Choose something first, then say history.": "Wähle zuerst etwas aus und sag dann Verlauf.",
    "Choose something first, then say its questions. Or say questions.": (
        "Wähle zuerst etwas aus und sag dann Fragen dazu. Oder sag Fragen."
    ),
    "Choose something first: say its number, then set it.": (
        "Wähle zuerst etwas aus: sag seine Nummer und dann setze es."
    ),
    "Closing datawatch.": "datawatch wird geschlossen.",
    "Datawatch activated.": "Datawatch ist aktiv.",
    "Datawatch mode works from a voice device.": (
        "Der datawatch-Modus funktioniert nur mit einem Sprachgerät."
    ),
    "Elsewhere: {counts}.": "Anderswo: {counts}.",
    "Focus cleared. Now showing everything.": "Fokus aufgehoben. Jetzt wird alles angezeigt.",
    "Focus: {focus}.": "Fokus: {focus}.",
    "For a full reason say why and its number.": "Für den ganzen Grund sag warum und die Nummer.",
    "For the task {title}: {reason}": "Zur Aufgabe {title}: {reason}",
    "For the {item}.": "Für: {item}.",
    "For the {item}: {number} unread alert, newest first.": (
        "Für {item}: {number} ungelesener Alarm, der neueste zuerst."
    ),
    "For the {item}: {number} unread alerts, newest first.": (
        "Für {item}: {number} ungelesene Alarme, die neuesten zuerst."
    ),
    "Go ahead. Describe the bug, or cancel.": "Los. Beschreibe den Fehler oder sag abbrechen.",
    "Go ahead. Say what the automation should do, or cancel.": (
        "Los. Sag, was die Automatisierung tun soll, oder sag abbrechen."
    ),
    "Go ahead. Say what to send, or cancel.": (
        "Los. Sag, was gesendet werden soll, oder sag abbrechen."
    ),
    "Go ahead. Say your answer, or cancel.": "Los. Sag deine Antwort oder sag abbrechen.",
    "I can read the first {number}.": "Ich kann die ersten {number} vorlesen.",
    "I can't reach datawatch, so nothing was sent. Say it again.": (
        "Ich erreiche datawatch nicht, daher wurde nichts gesendet. Sag es noch einmal."
    ),
    "I can't reach datawatch, so nothing was sent. Say my answer or option again.": (
        "Ich erreiche datawatch nicht, daher wurde nichts gesendet. Sag noch einmal meine "
        "Antwort oder eine Option."
    ),
    "I can't reach datawatch. Try again, or say stop.": (
        "Ich erreiche datawatch nicht. Versuch es noch einmal oder sag stopp."
    ),
    "I can't read a session's history by voice. Open it in datawatch.": (
        "Ich kann den Verlauf einer Sitzung nicht vorlesen. Öffne sie in datawatch."
    ),
    "I couldn't find a plan matching {name}.": (
        "Ich habe keinen Plan gefunden, der zu {name} passt."
    ),
    "I couldn't find a project matching {name}. Say list projects.": (
        "Ich habe kein Projekt gefunden, das zu {name} passt. Sag Projekte auflisten."
    ),
    "I couldn't find a session matching {name}.": (
        "Ich habe keine Sitzung gefunden, die zu {name} passt."
    ),
    "I couldn't find a task matching {name}.": (
        "Ich habe keine Aufgabe gefunden, die zu {name} passt."
    ),
    "I couldn't find an automation matching {name}.": (
        "Ich habe keine Automatisierung gefunden, die zu {name} passt."
    ),
    "I couldn't find an automaton matching {name}.": (
        "Ich habe keinen Automaten gefunden, der zu {name} passt."
    ),
    "I couldn't find {name} among the automata that need attention, are running, are on "
    "hold or finished recently.": (
        "Ich habe {name} nicht unter den Automaten gefunden, die Aufmerksamkeit brauchen, "
        "laufen, zurückgehalten werden oder kürzlich abgeschlossen wurden."
    ),
    "I did not keep your words.": "Ich habe deine Worte nicht behalten.",
    "I didn't understand three times. Closing datawatch.": (
        "Ich habe dreimal nichts verstanden. datawatch wird geschlossen."
    ),
    "I don't know whether it was sent. Check datawatch before saying it again.": (
        "Ich weiß nicht, ob es gesendet wurde. Prüfe datawatch, bevor du es noch einmal sagst."
    ),
    "I don't know whether the answer was sent. Say questions to check.": (
        "Ich weiß nicht, ob die Antwort gesendet wurde. Sag Fragen, um das zu prüfen."
    ),
    "I found {number} matches.": "Ich habe {number} Treffer gefunden.",
    "I found {number} matches. Say set and a number.": (
        "Ich habe {number} Treffer gefunden. Sag setze und eine Zahl."
    ),
    "I found {number} matching {name}. Say a number.": (
        "Ich habe {number} Treffer für {name} gefunden. Sag eine Zahl."
    ),
    "I haven't read a number {number}. Say more, or pick a number you heard.": (
        "Eine Nummer {number} habe ich nicht vorgelesen. Sag mehr oder wähle eine Zahl, die du "
        "gehört hast."
    ),
    "I haven't read a number {number}. Say more, or pick one you heard.": (
        "Eine Nummer {number} habe ich nicht vorgelesen. Sag mehr oder wähle eine, die du "
        "gehört hast."
    ),
    "I haven't read a question yet. Say questions.": (
        "Ich habe noch keine Frage vorgelesen. Sag Fragen."
    ),
    "In project {project}: {lead}{counts} across all projects.": (
        "Im Projekt {project}: {lead}{counts} in allen Projekten."
    ),
    "In project {project}: {lead}{counts}.": "Im Projekt {project}: {lead}{counts}.",
    "In the automaton {title}.": "Im Automaten {title}.",
    "It changed {files} in {packages}, and added {tests}.": (
        "Geändert: {files} in {packages}. Hinzugefügt: {tests}."
    ),
    "It has no tasks.": "Es gibt keine Aufgaben.",
    "It has {number} member.": "Anzahl der Mitglieder: {number}.",
    "It has {number} members.": "Anzahl der Mitglieder: {number}.",
    "It is blocking work.": "Sie blockiert Arbeit.",
    "It is on hold: {reason}": "Zurückgehalten: {reason}",
    "It uses {backend}.": "Verwendet {backend}.",
    "Its description": "Beschreibung",
    "Its goal": "Ziel",
    "Its goal: {goal}.": "Das Ziel: {goal}.",
    "Last activity {when}.": "Letzte Aktivität {when}.",
    "New work is paused.": "Neue Arbeit ist pausiert.",
    "Next: {title}, in the plan {plan}.": "Als Nächstes: {title}, im Plan {plan}.",
    "Next: {title}.": "Als Nächstes: {title}.",
    "No automata are running across all projects.": "In allen Projekten laufen keine Automaten.",
    "No automata are running in project {project}.": "Im Projekt {project} laufen keine Automaten.",
    "No automata have completed across all projects.": (
        "In keinem Projekt wurden Automaten abgeschlossen."
    ),
    "No automata have completed in project {project}.": (
        "Im Projekt {project} wurden keine Automaten abgeschlossen."
    ),
    "No focus. Showing everything.": "Kein Fokus. Alles wird angezeigt.",
    "No reason given": "Kein Grund angegeben",
    "Not sent yet.": "Noch nicht gesendet.",
    "Not sent yet. Say confirm answer, or cancel.": (
        "Noch nicht gesendet. Sag Antwort bestätigen oder abbrechen."
    ),
    "Not sent yet. Say confirm automation, or cancel.": (
        "Noch nicht gesendet. Sag Automatisierung bestätigen oder abbrechen."
    ),
    "Not sent yet. Say confirm bug, or cancel.": (
        "Noch nicht gesendet. Sag Fehler bestätigen oder abbrechen."
    ),
    "Not sent yet. Say confirm send, or cancel.": (
        "Noch nicht gesendet. Sag Senden bestätigen oder abbrechen."
    ),
    "Not sent yet. This is {target}. Your words: {words}": (
        "Noch nicht gesendet. Das ist {target}. Deine Worte: {words}"
    ),
    "Nothing is marked as next in any project.": (
        "In keinem Projekt ist etwas als nächstes markiert."
    ),
    "Nothing is marked as next.": "Nichts ist als nächstes markiert.",
    "Nothing is on hold.": "Nichts wird zurückgehalten.",
    "Nothing needs your attention.": "Nichts braucht deine Aufmerksamkeit.",
    "Number {number} is the {item}. Say set {number}.": (
        "Nummer {number} ist: {item}. Sag setze {number}."
    ),
    "Option {number}: {label}": "Option {number}: {label}",
    "Order: by name, for sessions, automations and running work. Say the list again to "
    "hear it that way. Say most recent first to switch.": (
        "Reihenfolge: nach Namen, für Sitzungen, Automatisierungen und laufende Arbeit. Sag "
        "die Liste noch einmal, um sie so zu hören. Zum Wechseln sag neueste zuerst."
    ),
    "Order: most recent first, for sessions, automations and running work. Say the list "
    "again to hear it that way. Say sort by name to switch.": (
        "Reihenfolge: die neuesten zuerst, für Sitzungen, Automatisierungen und laufende "
        "Arbeit. Sag die Liste noch einmal, um sie so zu hören. Zum Wechseln sag nach Namen "
        "sortieren."
    ),
    "Plan {line}.": "Plan {line}.",
    "Plan {number}, {line}.": "Plan {number}, {line}.",
    "Project {project}": "Projekt {project}",
    "Project {project} has no current plans.": "Das Projekt {project} hat keine aktuellen Pläne.",
    "Project {project} has {number} current plan.": (
        "Das Projekt {project} hat {number} aktuellen Plan."
    ),
    "Project {project} has {number} current plans.": (
        "Das Projekt {project} hat {number} aktuelle Pläne."
    ),
    "Project {project} no longer exists, so the focus is cleared.": (
        "Das Projekt {project} gibt es nicht mehr, daher ist der Fokus aufgehoben."
    ),
    "Project {project}.": "Projekt {project}.",
    "Project {project}. {next}": "Projekt {project}. {next}",
    "Project {project}: {plans}.": "Projekt {project}: {plans}.",
    "Question {number} of {total}, from datawatch.": "Frage {number} von {total}, von datawatch.",
    "Question {number} of {total}, from the supervisor.": (
        "Frage {number} von {total}, vom Supervisor."
    ),
    "Reason: {reason}": "Grund: {reason}",
    "Say attention, running or held items, then a number.": (
        "Sag Aufmerksamkeit, was läuft oder zurückgehaltene Elemente und dann eine Zahl."
    ),
    "Say confirm answer to send it, or cancel.": (
        "Sag Antwort bestätigen, um sie zu senden, oder abbrechen."
    ),
    "Say confirm automation to send it, or cancel.": (
        "Sag Automatisierung bestätigen, um sie zu senden, oder abbrechen."
    ),
    "Say confirm bug to send it, or cancel.": (
        "Sag Fehler bestätigen, um ihn zu senden, oder abbrechen."
    ),
    "Say confirm send to send it, or cancel.": (
        "Sag Senden bestätigen, um es zu senden, oder abbrechen."
    ),
    "Say more detail for more.": "Sag mehr Details, um mehr zu hören.",
    "Say more, or set and a number or name.": (
        "Sag mehr, oder setze und eine Zahl oder einen Namen."
    ),
    "Say more, or which number?": "Sag mehr, oder welche Nummer?",
    "Say more.": "Sag mehr.",
    "Say option and a number, my answer, more detail, or next question.": (
        "Sag Option und eine Zahl, meine Antwort, mehr Details oder nächste Frage."
    ),
    "Say plans or automations, choose one, then say automata.": (
        "Sag Pläne oder Automatisierungen, wähle etwas aus und sag dann Automaten."
    ),
    "Say why, or tasks.": "Sag warum oder Aufgaben.",
    "Sending to a session is not turned on yet. It is waiting for datawatch's access "
    "controls. Nothing was sent.": (
        "Das Senden an eine Sitzung ist noch nicht eingeschaltet. Es wartet auf die "
        "Zugriffskontrollen von datawatch. Nichts wurde gesendet."
    ),
    "Sent to the {item}.": "Gesendet an: {item}.",
    "Session named {name}: {state}.": "Sitzung mit dem Namen {name}: {state}.",
    "Sessions, automations and running work are listed by name. Say most recent first to switch.": (
        "Sitzungen, Automatisierungen und laufende Arbeit werden nach Namen sortiert. Zum "
        "Wechseln sag neueste zuerst."
    ),
    "Sessions, automations and running work are listed most recent first. Say sort by name "
    "to switch.": (
        "Sitzungen, Automatisierungen und laufende Arbeit werden mit den neuesten zuerst "
        "aufgelistet. Zum Wechseln sag nach Namen sortieren."
    ),
    "Set a plan or an automaton first, then set the task.": (
        "Wähle zuerst einen Plan oder einen Automaten und dann die Aufgabe."
    ),
    "Set a project first: say list projects, or set and a project name.": (
        "Wähle zuerst ein Projekt: sag Projekte auflisten, oder setze und einen Projektnamen."
    ),
    "Something went wrong in datawatch mode. Closing datawatch.": (
        "Im datawatch-Modus ist etwas schiefgegangen. datawatch wird geschlossen."
    ),
    "Sorry, I didn't get that. Say help.": "Das habe ich leider nicht verstanden. Sag Hilfe.",
    "Still there?": "Bist du noch da?",
    "Task {number}, {title}: {state}.": "Aufgabe {number}, {title}: {state}.",
    "Task {title}: {state}.": "Aufgabe {title}: {state}.",
    "Tasks are listed for a plan or an automaton.": (
        "Aufgaben gibt es für einen Plan oder einen Automaten."
    ),
    "That is a session. I can only say what is in the list and its details.": (
        "Das ist eine Sitzung. Ich kann nur sagen, was in der Liste und in ihren Details steht."
    ),
    "That is all.": "Das ist alles.",
    "That is the end of the list.": "Das ist das Ende der Liste.",
    "That is the last question.": "Das ist die letzte Frage.",
    "That question was already answered or withdrawn. Nothing was sent.": (
        "Diese Frage wurde bereits beantwortet oder zurückgezogen. Nichts wurde gesendet."
    ),
    "That session is {state} now, not waiting for input. Nothing was sent.": (
        "Der Status dieser Sitzung ist jetzt {state}, sie wartet nicht auf Eingabe. Nichts "
        "wurde gesendet."
    ),
    "The asker recommends option {number}.": "Empfohlen wird Option {number}.",
    "The automation {title}": "Die Automatisierung {title}",
    "The automaton {title}": "Der Automat {title}",
    "The datawatch certificate has changed. Check it in Home Assistant. Closing datawatch.": (
        "Das Zertifikat von datawatch hat sich geändert. Prüfe es in Home Assistant. datawatch "
        "wird geschlossen."
    ),
    "The most recently updated come first, which may not be the order they finished.": (
        "Die zuletzt aktualisierten kommen zuerst. Das muss nicht die Reihenfolge sein, in der "
        "sie abgeschlossen wurden."
    ),
    "The plan {title}": "Der Plan {title}",
    "The question begins: {words}": "Die Frage beginnt so: {words}",
    "The rest: {parts}.": "Der Rest: {parts}.",
    "The {item}": "{item}",
    "There are no current plans.": "Es gibt keine aktuellen Pläne.",
    "There are no open questions.": "Es gibt keine offenen Fragen.",
    "There are no projects.": "Es gibt keine Projekte.",
    "There are no unread alerts.": "Es gibt keine ungelesenen Alarme.",
    "There are no waiting, running or failed sessions.": (
        "Es gibt keine wartenden, laufenden oder fehlgeschlagenen Sitzungen."
    ),
    "There is no answer waiting.": "Es wartet keine Antwort.",
    "There is no list yet. Say list projects.": "Es gibt noch keine Liste. Sag Projekte auflisten.",
    "There is no option {number}.": "Es gibt keine Option {number}.",
    "There is nothing to go back to.": "Es gibt nichts, wohin ich zurückgehen kann.",
    "There is nothing waiting to be sent.": "Nichts wartet darauf, gesendet zu werden.",
    "This question has no more detail.": "Zu dieser Frage gibt es keine weiteren Details.",
    "This voice device can't hold a datawatch conversation.": (
        "Dieses Sprachgerät kann kein datawatch-Gespräch führen."
    ),
    "To read the rest, open datawatch.": "Um den Rest zu lesen, öffne datawatch.",
    "To see what it said, open it in datawatch.": (
        "Was sie gesagt hat, siehst du, wenn du sie in datawatch öffnest."
    ),
    "What it is for": "Wofür es ist",
    "Which number?": "Welche Nummer?",
    "Why the asker recommends it: {reason}": "Warum das empfohlen wird: {reason}",
    "You can say: questions, next question, option and a number, my answer, confirm "
    "answer, cancel, status, more detail, attention, running, held items, tell me about a "
    "number or name, why, tasks, progress, results, what finished, sessions, waiting "
    "sessions, running sessions, failed sessions, plans, overview, what's next, "
    "automations, reports or a report's name, list projects, more, set and a number or "
    "name, set it, its questions, all questions, automata, history, add automation, add "
    "bug, send to session, go back, where am I, alerts, list order, sort by name, most "
    "recent first, unset, repeat, or stop.": (
        "Du kannst sagen: Fragen, nächste Frage, Option und eine Zahl, meine Antwort, Antwort "
        "bestätigen, abbrechen, Status, mehr Details, Aufmerksamkeit, was läuft, "
        "zurückgehaltene Elemente, erzähl mir etwas über eine Zahl oder einen Namen, warum, "
        "Aufgaben, Fortschritt, Ergebnisse, was ist fertig, Sitzungen, wartende Sitzungen, "
        "laufende Sitzungen, fehlgeschlagene Sitzungen, Pläne, Übersicht, was kommt als "
        "Nächstes, Automatisierungen, Berichte oder den Namen eines Berichts, Projekte "
        "auflisten, mehr, setze und eine Zahl oder einen Namen, setze es, Fragen dazu, alle "
        "Fragen, Automaten, Verlauf, neue Automatisierung, Fehler melden, an Sitzung senden, "
        "zurück, wo bin ich, Alarme, Listenreihenfolge, nach Namen sortieren, neueste zuerst, "
        "Fokus aufheben, wiederholen oder stopp."
    ),
    "You have no reports yet. Add one on the datawatch page in Home Assistant.": (
        "Du hast noch keine Berichte. Füge auf der datawatch-Seite in Home Assistant einen hinzu."
    ),
    "You have {number} report: {names}. Say a name.": (
        "Du hast {number} Bericht: {names}. Sag einen Namen."
    ),
    "You have {number} reports: {names}. Say a name.": (
        "Du hast {number} Berichte: {names}. Sag einen Namen."
    ),
    "Your answer was not sent.": "Deine Antwort wurde nicht gesendet.",
    "Your assistant didn't answer. Try again, or say stop.": (
        "Dein Assistent hat nicht geantwortet. Versuch es noch einmal oder sag stopp."
    ),
    "Your assistant had nothing to say.": "Dein Assistent hatte nichts zu sagen.",
    "Your automation was not sent.": "Deine Automatisierung wurde nicht gesendet.",
    "Your bug was not sent.": "Dein Fehlerbericht wurde nicht gesendet.",
    "Your choice: option {number}, {label}": "Deine Wahl: Option {number}, {label}",
    "Your message was not sent.": "Deine Nachricht wurde nicht gesendet.",
    "Your words: {words}": "Deine Worte: {words}",
    "a bug for project {project}": "ein Fehler für das Projekt {project}",
    "a message to the {item}": "eine Nachricht an: {item}",
    "a new draft automaton in project {project}": (
        "ein neuer Automat als Entwurf im Projekt {project}"
    ),
    "active": "aktiv",
    "active {when}": "aktiv {when}",
    "all new work is paused.": "alle neue Arbeit ist pausiert.",
    "approved": "genehmigt",
    "archived": "archiviert",
    "at least {count}": "mindestens {count}",
    "automation {title}": "Automatisierung {title}",
    "automaton {title}": "Automat {title}",
    "awaiting approval": "zur Genehmigung offen",
    "blocked": "blockiert",
    "cancelled": "abgebrochen",
    "completed": "abgeschlossen",
    "datawatch added it to an open draft bug group.": (
        "datawatch hat ihn zu einer offenen Fehlergruppe im Entwurf hinzugefügt."
    ),
    "datawatch did not accept it, so nothing was sent. The session may be showing a prompt "
    "to answer in datawatch.": (
        "datawatch hat es nicht angenommen, daher wurde nichts gesendet. Vielleicht zeigt die "
        "Sitzung eine Rückfrage, die du in datawatch beantworten musst."
    ),
    "datawatch did not accept it. Nothing was sent.": (
        "datawatch hat es nicht angenommen. Nichts wurde gesendet."
    ),
    "datawatch gives no folder for project {project}. Nothing was sent.": (
        "datawatch nennt keinen Ordner für das Projekt {project}. Nichts wurde gesendet."
    ),
    "datawatch gives no history for a plan.": "datawatch liefert keinen Verlauf für einen Plan.",
    "datawatch gives no reason.": "datawatch nennt keinen Grund.",
    "datawatch has no change record for it.": "datawatch hat dazu keinen Änderungsbericht.",
    "datawatch has no history for {title}.": "datawatch hat keinen Verlauf für {title}.",
    "datawatch links no open questions to the {item}. There are {number} open questions in "
    "all. Say all questions.": (
        "datawatch verknüpft keine offenen Fragen mit: {item}. Insgesamt gibt es {number} "
        "offene Fragen. Sag alle Fragen."
    ),
    "datawatch links no open questions to the {item}. There is {number} open question in "
    "all. Say all questions.": (
        "datawatch verknüpft keine offenen Fragen mit: {item}. Insgesamt gibt es {number} "
        "offene Frage. Sag alle Fragen."
    ),
    "datawatch links no unread alerts to the {item}. There are {number} unread alerts in "
    "all. Say unset, then alerts.": (
        "datawatch verknüpft keine ungelesenen Alarme mit: {item}. Insgesamt gibt es {number} "
        "ungelesene Alarme. Sag Fokus aufheben und dann Alarme."
    ),
    "datawatch links no unread alerts to the {item}. There is {number} unread alert in "
    "all. Say unset, then alerts.": (
        "datawatch verknüpft keine ungelesenen Alarme mit: {item}. Insgesamt gibt es {number} "
        "ungelesenen Alarm. Sag Fokus aufheben und dann Alarme."
    ),
    "datawatch made a new draft bug group for it.": (
        "datawatch hat dafür eine neue Fehlergruppe als Entwurf angelegt."
    ),
    "datawatch made a one-task draft for it.": (
        "datawatch hat dafür einen Entwurf mit einer Aufgabe angelegt."
    ),
    "datawatch no longer has that session. Nothing was sent.": (
        "datawatch hat diese Sitzung nicht mehr. Nichts wurde gesendet."
    ),
    "datawatch no longer has the project {project}. Nothing was sent.": (
        "datawatch hat das Projekt {project} nicht mehr. Nichts wurde gesendet."
    ),
    "datawatch no longer has the {item}, so I moved your focus up.": (
        "datawatch hat Folgendes nicht mehr: {item}. Ich habe deinen Fokus eine Ebene höher "
        "gesetzt."
    ),
    "datawatch no longer has the {item}.": "datawatch hat Folgendes nicht mehr: {item}.",
    "datawatch records history for an automaton, not for one task. Choose its automaton to "
    "hear it.": (
        "datawatch führt den Verlauf für einen Automaten, nicht für eine einzelne Aufgabe. "
        "Wähle den Automaten, um ihn zu hören."
    ),
    "datawatch refused access. Check the token in Home Assistant. Closing datawatch.": (
        "datawatch hat den Zugriff verweigert. Prüfe das Token in Home Assistant. datawatch "
        "wird geschlossen."
    ),
    "datawatch refused that answer because it looks like it holds a secret. Nothing was sent.": (
        "datawatch hat diese Antwort abgelehnt, weil sie anscheinend ein Geheimnis enthält. "
        "Nichts wurde gesendet."
    ),
    "datawatch refused that answer. Nothing was sent.": (
        "datawatch hat diese Antwort abgelehnt. Nichts wurde gesendet."
    ),
    "datawatch says: {reason}": "datawatch sagt: {reason}",
    "datawatch's bug intake is turned off for project {project}. Nothing was sent.": (
        "Die Fehlererfassung von datawatch ist für das Projekt {project} ausgeschaltet. Nichts "
        "wurde gesendet."
    ),
    "done": "erledigt",
    "draft": "im Entwurf",
    "error": "Fehler",
    "failed": "fehlgeschlagen",
    "held": "zurückgehalten",
    "in progress": "in Arbeit",
    "just now": "gerade eben",
    "not shipped": "nicht ausgeliefert",
    "not started": "nicht begonnen",
    "paused": "pausiert",
    "plan {title}": "Plan {title}",
    "planning": "in Planung",
    "project {project}": "Projekt {project}",
    "queued": "in der Warteschlange",
    "review needed": "zur Prüfung offen",
    "running": "in Ausführung",
    "session {title}": "Sitzung {title}",
    "shipped": "ausgeliefert",
    "shipped in {release}": "ausgeliefert in {release}",
    "task {title}": "Aufgabe {title}",
    "unknown": "unbekannt",
    "unnamed": "unbenannt",
    "untitled": "ohne Titel",
    "waiting decision": "zur Entscheidung offen",
    "waiting for input": "auf Eingabe wartend",
    "waiting for review": "zur Überprüfung offen",
    "warning": "Warnung",
    "{counts} across all projects.": "{counts} in allen Projekten.",
    "{done} of {number} task completed.": "{done} von {number} Aufgabe abgeschlossen.",
    "{done} of {number} tasks completed.": "{done} von {number} Aufgaben abgeschlossen.",
    "{done} of {total} automata done": "{done} von {total} Automaten erledigt",
    "{done} of {total} automata done.": "{done} von {total} Automaten erledigt.",
    "{done} of {total} tasks completed": "{done} von {total} Aufgaben abgeschlossen",
    "{first} and {last}": "{first} und {last}",
    "{found} among the newest {number}": "{found} unter den neuesten {number}",
    "{kind} from {when}": "{kind}, {when}",
    "{lead}{counts}.": "{lead}{counts}.",
    "{name} has no automata.": "{name} hat keine Automaten.",
    "{name} has no tasks.": "{name} hat keine Aufgaben.",
    "{name} has nothing in it. Change it on the datawatch page in Home Assistant.": (
        "{name} ist leer. Ändere den Bericht auf der datawatch-Seite in Home Assistant."
    ),
    "{name} has {number} automata.": "{name} hat {number} Automaten.",
    "{name} has {number} automaton.": "{name} hat {number} Automaten.",
    "{name} has {number} task.": "{name} hat {number} Aufgabe.",
    "{name} has {number} tasks.": "{name} hat {number} Aufgaben.",
    "{number} automata are running across all projects.": (
        "{number} Automaten laufen in allen Projekten."
    ),
    "{number} automata are running in project {project}.": (
        "{number} Automaten laufen im Projekt {project}."
    ),
    "{number} automata have completed across all projects.": (
        "{number} Automaten wurden in allen Projekten abgeschlossen."
    ),
    "{number} automata have completed in project {project}.": (
        "{number} Automaten wurden im Projekt {project} abgeschlossen."
    ),
    "{number} automata need attention, across all projects: {parts}.": (
        "{number} Automaten brauchen Aufmerksamkeit, in allen Projekten: {parts}."
    ),
    "{number} automaton has completed across all projects.": (
        "{number} Automat wurde in allen Projekten abgeschlossen."
    ),
    "{number} automaton has completed in project {project}.": (
        "{number} Automat wurde im Projekt {project} abgeschlossen."
    ),
    "{number} automaton is running across all projects.": (
        "{number} Automat läuft in allen Projekten."
    ),
    "{number} automaton is running in project {project}.": (
        "{number} Automat läuft im Projekt {project}."
    ),
    "{number} automaton needs attention, across all projects: {parts}.": (
        "{number} Automat braucht Aufmerksamkeit, in allen Projekten: {parts}."
    ),
    "{number} current plan": "{number} aktueller Plan",
    "{number} current plans": "{number} aktuelle Pläne",
    "{number} day ago": "vor {number} Tag",
    "{number} days ago": "vor {number} Tagen",
    "{number} failed or blocked automata": "{number} fehlgeschlagene oder blockierte Automaten",
    "{number} failed or blocked automaton": "{number} fehlgeschlagener oder blockierter Automat",
    "{number} failed session": "{number} fehlgeschlagene Sitzung",
    "{number} failed sessions": "{number} fehlgeschlagene Sitzungen",
    "{number} file": "{number} Datei",
    "{number} files": "{number} Dateien",
    "{number} finished or set aside with tasks held for review": (
        "{number} abgeschlossen oder zurückgestellt, mit zur Prüfung zurückgehaltenen Aufgaben"
    ),
    "{number} held item": "{number} zurückgehaltenes Element",
    "{number} held items": "{number} zurückgehaltene Elemente",
    "{number} hour ago": "vor {number} Stunde",
    "{number} hours ago": "vor {number} Stunden",
    "{number} item is on hold, across all projects.": (
        "{number} Element wird zurückgehalten, in allen Projekten."
    ),
    "{number} items are on hold, across all projects.": (
        "{number} Elemente werden zurückgehalten, in allen Projekten."
    ),
    "{number} member": "{number} Mitglied",
    "{number} members": "{number} Mitglieder",
    "{number} minute ago": "vor {number} Minute",
    "{number} minutes ago": "vor {number} Minuten",
    "{number} not started": "{number} nicht begonnen",
    "{number} open question": "{number} offene Frage",
    "{number} open question, across all projects.": "{number} offene Frage, in allen Projekten.",
    "{number} open questions": "{number} offene Fragen",
    "{number} open questions, across all projects.": "{number} offene Fragen, in allen Projekten.",
    "{number} package": "{number} Paket",
    "{number} packages": "{number} Paketen",
    "{number} plan": "{number} Plan",
    "{number} plans": "{number} Pläne",
    "{number} plans archived.": "{number} Pläne archiviert.",
    "{number} project": "{number} Projekt",
    "{number} project has something next.": "{number} Projekt hat etwas als Nächstes.",
    "{number} projects": "{number} Projekte",
    "{number} projects have something next.": "{number} Projekte haben etwas als Nächstes.",
    "{number} running": "{number} in Ausführung",
    "{number} session waiting for input": "{number} Sitzung wartet auf Eingabe",
    "{number} sessions waiting for input": "{number} Sitzungen warten auf Eingabe",
    "{number} task held for review": "{number} Aufgabe zur Prüfung zurückgehalten",
    "{number} task is stuck. First: {title}, {state}.": (
        "{number} Aufgabe hängt fest. Die erste: {title}, {state}."
    ),
    "{number} tasks are stuck. First: {title}, {state}.": (
        "{number} Aufgaben hängen fest. Die erste: {title}, {state}."
    ),
    "{number} tasks held for review": "{number} Aufgaben zur Prüfung zurückgehalten",
    "{number} test": "{number} Test",
    "{number} tests": "{number} Tests",
    "{number} unread alert, across all projects, newest first.": (
        "{number} ungelesener Alarm, in allen Projekten, der neueste zuerst."
    ),
    "{number} unread alerts, across all projects, newest first.": (
        "{number} ungelesene Alarme, in allen Projekten, die neuesten zuerst."
    ),
    "{number} warning or error": "{number} Warnung oder Fehler",
    "{number} warnings or errors": "{number} Warnungen oder Fehler",
    "{number} {state}": "{number} {state}",
    "{number}, session named {name}, {state}": "{number}, Sitzung mit dem Namen {name}, {state}",
    "{plans} in {projects}.": "{plans} in {projects}.",
    "{start}, and more": "{start}, und mehr",
    "{start}, and more. See datawatch for the rest.": (
        "{start}, und mehr. Den Rest siehst du in datawatch."
    ),
    "{title} has no tasks.": "{title} hat keine Aufgaben.",
    "{title} has {number} entries. The latest: {lines}": (
        "{title} hat {number} Einträge. Die neuesten: {lines}"
    ),
    "{title} has {number} entry. The latest: {lines}": (
        "{title} hat {number} Eintrag. Der neueste: {lines}"
    ),
    "{title} is {state}.": "{title} ist {state}.",
    "{what}, by {actor}": "{what}, von {actor}",
    "{where}: no automations.": "{where}: keine Automatisierungen.",
    "{where}: sessions, {counts}.": "{where}: Sitzungen, {counts}.",
    "{where}: {number} automation, {parts}.": "{where}: {number} Automatisierung, {parts}.",
    "{where}: {number} automations, {parts}.": "{where}: {number} Automatisierungen, {parts}.",
}
