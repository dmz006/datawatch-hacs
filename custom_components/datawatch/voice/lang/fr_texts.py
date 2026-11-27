"""French: what datawatch mode says, keyed by the English sentence."""

TEXTS: dict[str, str] = {
    ", ": ", ",
    "A warning": "Un avertissement",
    "Added a draft automaton to project {project}, but I could not name it, so it may show "
    "as untitled. Do not add it again.": (
        "J'ai ajouté un automate en brouillon au projet {project}, mais je n'ai pas pu le "
        "nommer ; il peut donc apparaître sans titre. Ne l'ajoutez pas une deuxième fois."
    ),
    "Added a draft automaton to project {project}, named {title}. I did not ask datawatch "
    "to plan or start it.": (
        "J'ai ajouté un automate en brouillon au projet {project}, nommé {title}. Je n'ai pas "
        "demandé à datawatch de le planifier ni de le démarrer."
    ),
    "All projects": "Tous les projets",
    "Also {number} archived.": "Et aussi, archivés : {number}.",
    "An alert": "Une alerte",
    "An error": "Une erreur",
    "Answer sent. Say next question.": "Réponse envoyée. Dites question suivante.",
    "Automation {line}": "Automatisation {line}",
    "Automaton {title}: {state}.": "Automate {title} : {state}.",
    "Back.": "Retour.",
    "Bug reported for project {project}.": "Bug signalé pour le projet {project}.",
    "Cancelled. Nothing was sent.": "Annulé. Rien n'a été envoyé.",
    "Choose a session first: say sessions, then its number.": (
        "Choisissez d'abord une session : dites sessions, puis son numéro."
    ),
    "Choose something first, then say history.": (
        "Choisissez d'abord un élément, puis dites historique."
    ),
    "Choose something first, then say its questions. Or say questions.": (
        "Choisissez d'abord un élément, puis dites ses questions. Ou dites questions."
    ),
    "Choose something first: say its number, then set it.": (
        "Choisissez d'abord un élément : dites son numéro, puis sélectionne-le."
    ),
    "Closing datawatch.": "Fermeture de datawatch.",
    "Datawatch activated.": "Datawatch activé.",
    "Datawatch mode works from a voice device.": (
        "Le mode datawatch fonctionne depuis un appareil vocal."
    ),
    "Elsewhere: {counts}.": "Ailleurs : {counts}.",
    "Focus cleared. Now showing everything.": "Focus retiré. Tout est maintenant affiché.",
    "Focus: {focus}.": "Focus : {focus}.",
    "For a full reason say why and its number.": (
        "Pour la raison complète, dites pourquoi et son numéro."
    ),
    "For the task {title}: {reason}": "Pour la tâche {title} : {reason}",
    "For the {item}.": "Pour : {item}.",
    "For the {item}: {number} unread alert, newest first.": (
        "Pour {item} : {number} alerte non lue, la plus récente d'abord."
    ),
    "For the {item}: {number} unread alerts, newest first.": (
        "Pour {item} : {number} alertes non lues, les plus récentes d'abord."
    ),
    "Go ahead. Describe the bug, or cancel.": "Allez-y. Décrivez le bug, ou dites annuler.",
    "Go ahead. Say what the automation should do, or cancel.": (
        "Allez-y. Dites ce que l'automatisation doit faire, ou dites annuler."
    ),
    "Go ahead. Say what to send, or cancel.": (
        "Allez-y. Dites ce qu'il faut envoyer, ou dites annuler."
    ),
    "Go ahead. Say your answer, or cancel.": "Allez-y. Dites votre réponse, ou dites annuler.",
    "I can read the first {number}.": "Je peux lire les {number} premiers.",
    "I can't reach datawatch, so nothing was sent. Say it again.": (
        "Je n'arrive pas à joindre datawatch, rien n'a donc été envoyé. Répétez votre demande."
    ),
    "I can't reach datawatch, so nothing was sent. Say my answer or option again.": (
        "Je n'arrive pas à joindre datawatch, rien n'a donc été envoyé. Redites ma réponse ou "
        "une option."
    ),
    "I can't reach datawatch. Try again, or say stop.": (
        "Je n'arrive pas à joindre datawatch. Réessayez, ou dites stop."
    ),
    "I can't read a session's history by voice. Open it in datawatch.": (
        "Je ne peux pas lire à voix haute l'historique d'une session. Ouvrez-la dans datawatch."
    ),
    "I couldn't find a plan matching {name}.": "Je n'ai trouvé aucun plan correspondant à {name}.",
    "I couldn't find a project matching {name}. Say list projects.": (
        "Je n'ai trouvé aucun projet correspondant à {name}. Dites liste des projets."
    ),
    "I couldn't find a session matching {name}.": (
        "Je n'ai trouvé aucune session correspondant à {name}."
    ),
    "I couldn't find a task matching {name}.": (
        "Je n'ai trouvé aucune tâche correspondant à {name}."
    ),
    "I couldn't find an automation matching {name}.": (
        "Je n'ai trouvé aucune automatisation correspondant à {name}."
    ),
    "I couldn't find an automaton matching {name}.": (
        "Je n'ai trouvé aucun automate correspondant à {name}."
    ),
    "I couldn't find {name} among the automata that need attention, are running, are on "
    "hold or finished recently.": (
        "Je n'ai pas trouvé {name} parmi les automates à traiter, en cours, retenus ou "
        "terminés récemment."
    ),
    "I did not keep your words.": "Je n'ai pas gardé vos paroles.",
    "I didn't understand three times. Closing datawatch.": (
        "Je n'ai pas compris trois fois de suite. Fermeture de datawatch."
    ),
    "I don't know whether it was sent. Check datawatch before saying it again.": (
        "Je ne sais pas si l'envoi a réussi. Vérifiez dans datawatch avant de le redire."
    ),
    "I don't know whether the answer was sent. Say questions to check.": (
        "Je ne sais pas si la réponse a été envoyée. Dites questions pour vérifier."
    ),
    "I found {number} matches.": "J'ai trouvé {number} correspondances.",
    "I found {number} matches. Say set and a number.": (
        "J'ai trouvé {number} correspondances. Dites sélectionne et un numéro."
    ),
    "I found {number} matching {name}. Say a number.": (
        "J'ai trouvé {number} correspondances pour {name}. Dites un numéro."
    ),
    "I haven't read a number {number}. Say more, or pick a number you heard.": (
        "Je n'ai pas lu de numéro {number}. Dites suite, ou choisissez un numéro que vous avez "
        "entendu."
    ),
    "I haven't read a number {number}. Say more, or pick one you heard.": (
        "Je n'ai pas lu de numéro {number}. Dites suite, ou choisissez-en un que vous avez entendu."
    ),
    "I haven't read a question yet. Say questions.": (
        "Je n'ai pas encore lu de question. Dites questions."
    ),
    "In project {project}: {lead}{counts} across all projects.": (
        "Dans le projet {project} : {lead}{counts} dans l'ensemble des projets."
    ),
    "In project {project}: {lead}{counts}.": "Dans le projet {project} : {lead}{counts}.",
    "In the automaton {title}.": "Dans l'automate {title}.",
    "It changed {files} in {packages}, and added {tests}.": (
        "Modifications : {files} dans {packages}. Ajouts : {tests}."
    ),
    "It has no tasks.": "Il n'y a aucune tâche.",
    "It has {number} member.": "Il y a {number} membre.",
    "It has {number} members.": "Il y a {number} membres.",
    "It is blocking work.": "Elle bloque du travail.",
    "It is on hold: {reason}": "En attente : {reason}",
    "It uses {backend}.": "Utilise {backend}.",
    "Its description": "Sa description",
    "Its goal": "Son objectif",
    "Its goal: {goal}.": "Son objectif : {goal}.",
    "Last activity {when}.": "Dernière activité {when}.",
    "New work is paused.": "Le nouveau travail est en pause.",
    "Next: {title}, in the plan {plan}.": "À suivre : {title}, dans le plan {plan}.",
    "Next: {title}.": "À suivre : {title}.",
    "No automata are running across all projects.": (
        "Aucun automate n'est en cours dans l'ensemble des projets."
    ),
    "No automata are running in project {project}.": (
        "Aucun automate n'est en cours dans le projet {project}."
    ),
    "No automata have completed across all projects.": (
        "Aucun automate n'est terminé dans l'ensemble des projets."
    ),
    "No automata have completed in project {project}.": (
        "Aucun automate n'est terminé dans le projet {project}."
    ),
    "No focus. Showing everything.": "Pas de focus. Tout est affiché.",
    "No reason given": "Aucune raison indiquée",
    "Not sent yet.": "Pas encore envoyé.",
    "Not sent yet. Say confirm answer, or cancel.": (
        "Pas encore envoyé. Dites confirmer la réponse, ou annuler."
    ),
    "Not sent yet. Say confirm automation, or cancel.": (
        "Pas encore envoyé. Dites confirmer l'automatisation, ou annuler."
    ),
    "Not sent yet. Say confirm bug, or cancel.": (
        "Pas encore envoyé. Dites confirmer le bug, ou annuler."
    ),
    "Not sent yet. Say confirm send, or cancel.": (
        "Pas encore envoyé. Dites confirmer l'envoi, ou annuler."
    ),
    "Not sent yet. This is {target}. Your words: {words}": (
        "Pas encore envoyé. C'est {target}. Vos paroles : {words}"
    ),
    "Nothing is marked as next in any project.": (
        "Rien n'est indiqué comme étant à suivre, dans aucun projet."
    ),
    "Nothing is marked as next.": "Rien n'est indiqué comme étant à suivre.",
    "Nothing is on hold.": "Rien n'est retenu.",
    "Nothing needs your attention.": "Rien ne demande votre attention.",
    "Number {number} is the {item}. Say set {number}.": (
        "Le numéro {number} est : {item}. Dites sélectionne {number}."
    ),
    "Option {number}: {label}": "Option {number} : {label}",
    "Order: by name, for sessions, automations and running work. Say the list again to "
    "hear it that way. Say most recent first to switch.": (
        "Ordre : par nom, pour les sessions, les automatisations et les travaux en cours. "
        "Redemandez la liste pour l'entendre ainsi. Pour changer, dites les plus récents "
        "d'abord."
    ),
    "Order: most recent first, for sessions, automations and running work. Say the list "
    "again to hear it that way. Say sort by name to switch.": (
        "Ordre : les plus récents d'abord, pour les sessions, les automatisations et les "
        "travaux en cours. Redemandez la liste pour l'entendre ainsi. Pour changer, dites "
        "trier par nom."
    ),
    "Plan {line}.": "Plan {line}.",
    "Plan {number}, {line}.": "Plan {number}, {line}.",
    "Project {project}": "Projet {project}",
    "Project {project} has no current plans.": (
        "Le projet {project} n'a aucun plan en cours de validité."
    ),
    "Project {project} has {number} current plan.": "Le projet {project} a {number} plan actuel.",
    "Project {project} has {number} current plans.": (
        "Le projet {project} a {number} plans actuels."
    ),
    "Project {project} no longer exists, so the focus is cleared.": (
        "Le projet {project} n'existe plus, le focus est donc retiré."
    ),
    "Project {project}.": "Projet {project}.",
    "Project {project}. {next}": "Projet {project}. {next}",
    "Project {project}: {plans}.": "Projet {project} : {plans}.",
    "Question {number} of {total}, from datawatch.": "Question {number} sur {total}, de datawatch.",
    "Question {number} of {total}, from the supervisor.": (
        "Question {number} sur {total}, du superviseur."
    ),
    "Reason: {reason}": "Raison : {reason}",
    "Say attention, running or held items, then a number.": (
        "Dites à traiter, en cours ou éléments retenus, puis un numéro."
    ),
    "Say confirm answer to send it, or cancel.": (
        "Dites confirmer la réponse pour l'envoyer, ou annuler."
    ),
    "Say confirm automation to send it, or cancel.": (
        "Dites confirmer l'automatisation pour l'envoyer, ou annuler."
    ),
    "Say confirm bug to send it, or cancel.": "Dites confirmer le bug pour l'envoyer, ou annuler.",
    "Say confirm send to send it, or cancel.": (
        "Dites confirmer l'envoi pour l'envoyer, ou annuler."
    ),
    "Say more detail for more.": "Dites plus de détails pour en savoir plus.",
    "Say more, or set and a number or name.": "Dites suite, ou sélectionne et un numéro ou un nom.",
    "Say more, or which number?": "Dites suite, ou quel numéro ?",
    "Say more.": "Dites suite.",
    "Say option and a number, my answer, more detail, or next question.": (
        "Dites option et un numéro, ma réponse, plus de détails ou question suivante."
    ),
    "Say plans or automations, choose one, then say automata.": (
        "Dites plans ou automatisations, choisissez un élément, puis dites automates."
    ),
    "Say why, or tasks.": "Dites pourquoi, ou tâches.",
    "Sending to a session is not turned on yet. It is waiting for datawatch's access "
    "controls. Nothing was sent.": (
        "L'envoi à une session n'est pas encore activé. Il attend les contrôles d'accès de "
        "datawatch. Rien n'a été envoyé."
    ),
    "Sent to the {item}.": "Envoyé à : {item}.",
    "Session named {name}: {state}.": "Session nommée {name} : {state}.",
    "Sessions, automations and running work are listed by name. Say most recent first to switch.": (
        "Les sessions, les automatisations et les travaux en cours sont classés par nom. Pour "
        "changer, dites les plus récents d'abord."
    ),
    "Sessions, automations and running work are listed most recent first. Say sort by name "
    "to switch.": (
        "Les sessions, les automatisations et les travaux en cours sont listés avec les plus "
        "récents d'abord. Pour changer, dites trier par nom."
    ),
    "Set a plan or an automaton first, then set the task.": (
        "Sélectionnez d'abord un plan ou un automate, puis la tâche."
    ),
    "Set a project first: say list projects, or set and a project name.": (
        "Sélectionnez d'abord un projet : dites liste des projets, ou sélectionne et un nom de "
        "projet."
    ),
    "Something went wrong in datawatch mode. Closing datawatch.": (
        "Un problème est survenu en mode datawatch. Fermeture de datawatch."
    ),
    "Sorry, I didn't get that. Say help.": "Désolé, je n'ai pas compris. Dites aide.",
    "Still there?": "Vous êtes toujours là ?",
    "Task {number}, {title}: {state}.": "Tâche {number}, {title} : {state}.",
    "Task {title}: {state}.": "Tâche {title} : {state}.",
    "Tasks are listed for a plan or an automaton.": (
        "Les tâches sont listées pour un plan ou un automate."
    ),
    "That is a session. I can only say what is in the list and its details.": (
        "C'est une session. Je peux seulement dire ce qui figure dans la liste et ses détails."
    ),
    "That is all.": "C'est tout.",
    "That is the end of the list.": "C'est la fin de la liste.",
    "That is the last question.": "C'est la dernière question.",
    "That question was already answered or withdrawn. Nothing was sent.": (
        "Cette question a déjà reçu une réponse ou a été retirée. Rien n'a été envoyé."
    ),
    "That session is {state} now, not waiting for input. Nothing was sent.": (
        "L'état de cette session est maintenant {state} ; elle n'attend pas de saisie. Rien "
        "n'a été envoyé."
    ),
    "The asker recommends option {number}.": "La réponse recommandée est l'option {number}.",
    "The automation {title}": "L'automatisation {title}",
    "The automaton {title}": "L'automate {title}",
    "The datawatch certificate has changed. Check it in Home Assistant. Closing datawatch.": (
        "Le certificat de datawatch a changé. Vérifiez-le dans Home Assistant. Fermeture de "
        "datawatch."
    ),
    "The most recently updated come first, which may not be the order they finished.": (
        "Les derniers mis à jour viennent en premier ; ce n'est pas forcément l'ordre dans "
        "lequel ils se sont terminés."
    ),
    "The plan {title}": "Le plan {title}",
    "The question begins: {words}": "La question commence ainsi : {words}",
    "The rest: {parts}.": "Le reste : {parts}.",
    "The {item}": "{item}",
    "There are no current plans.": "Il n'y a aucun plan actuel.",
    "There are no open questions.": "Il n'y a aucune question ouverte.",
    "There are no projects.": "Il n'y a aucun projet.",
    "There are no unread alerts.": "Il n'y a aucune alerte non lue.",
    "There are no waiting, running or failed sessions.": (
        "Il n'y a aucune session en attente, en cours ou en échec."
    ),
    "There is no answer waiting.": "Aucune réponse n'est en attente.",
    "There is no list yet. Say list projects.": (
        "Il n'y a pas encore de liste. Dites liste des projets."
    ),
    "There is no option {number}.": "Il n'y a pas d'option {number}.",
    "There is nothing to go back to.": "Il n'y a rien à quoi revenir.",
    "There is nothing waiting to be sent.": "Rien n'attend d'être envoyé.",
    "This question has no more detail.": "Cette question n'a pas d'autres détails.",
    "This voice device can't hold a datawatch conversation.": (
        "Cet appareil vocal ne peut pas tenir une conversation datawatch."
    ),
    "To read the rest, open datawatch.": "Pour lire la suite, ouvrez datawatch.",
    "To see what it said, open it in datawatch.": (
        "Pour voir ce qu'elle a dit, ouvrez-la dans datawatch."
    ),
    "What it is for": "À quoi il sert",
    "Which number?": "Quel numéro ?",
    "Why the asker recommends it: {reason}": "Pourquoi cette réponse est recommandée : {reason}",
    "You can say: questions, next question, option and a number, my answer, confirm "
    "answer, cancel, status, more detail, attention, running, held items, tell me about a "
    "number or name, why, tasks, progress, results, what finished, sessions, waiting "
    "sessions, running sessions, failed sessions, plans, overview, what's next, "
    "automations, reports or a report's name, list projects, more, set and a number or "
    "name, set it, its questions, all questions, automata, history, add automation, add "
    "bug, send to session, go back, where am I, alerts, list order, sort by name, most "
    "recent first, unset, repeat, or stop.": (
        "Vous pouvez dire : questions, question suivante, option et un numéro, ma réponse, "
        "confirmer la réponse, annuler, état, plus de détails, à traiter, en cours, éléments "
        "retenus, parle-moi d'un numéro ou d'un nom, pourquoi, tâches, progression, résultats, "
        "travaux terminés, sessions, sessions en attente, sessions en cours, sessions en "
        "échec, plans, vue d'ensemble, quelle est la suite, automatisations, rapports ou le "
        "nom d'un rapport, liste des projets, suite, sélectionne et un numéro ou un nom, "
        "sélectionne-le, ses questions, toutes les questions, automates, historique, nouvelle "
        "automatisation, signaler un bug, envoyer à la session, retour, où suis-je, alertes, "
        "ordre des listes, trier par nom, les plus récents d'abord, retirer le focus, répète "
        "ou stop."
    ),
    "You have no reports yet. Add one on the datawatch page in Home Assistant.": (
        "Vous n'avez pas encore de rapport. Ajoutez-en un sur la page datawatch de Home Assistant."
    ),
    "You have {number} report: {names}. Say a name.": (
        "Vous avez {number} rapport : {names}. Dites un nom."
    ),
    "You have {number} reports: {names}. Say a name.": (
        "Vous avez {number} rapports : {names}. Dites un nom."
    ),
    "Your answer was not sent.": "Votre réponse n'a pas été envoyée.",
    "Your assistant didn't answer. Try again, or say stop.": (
        "Votre assistant n'a pas répondu. Réessayez, ou dites stop."
    ),
    "Your assistant had nothing to say.": "Votre assistant n'avait rien à dire.",
    "Your automation was not sent.": "Votre automatisation n'a pas été envoyée.",
    "Your bug was not sent.": "Votre bug n'a pas été envoyé.",
    "Your choice: option {number}, {label}": "Votre choix : option {number}, {label}",
    "Your message was not sent.": "Votre message n'a pas été envoyé.",
    "Your words: {words}": "Vos paroles : {words}",
    "a bug for project {project}": "un bug pour le projet {project}",
    "a message to the {item}": "un message pour : {item}",
    "a new draft automaton in project {project}": (
        "un nouvel automate en brouillon dans le projet {project}"
    ),
    "active": "en activité",
    "active {when}": "activité {when}",
    "all new work is paused.": "tout nouveau travail est en pause.",
    "approved": "approuvé",
    "archived": "archivé",
    "at least {count}": "au moins {count}",
    "automation {title}": "automatisation {title}",
    "automaton {title}": "automate {title}",
    "awaiting approval": "en attente d'approbation",
    "blocked": "en blocage",
    "cancelled": "annulé",
    "completed": "terminé",
    "datawatch added it to an open draft bug group.": (
        "datawatch l'a ajouté à un groupe de bugs en brouillon déjà ouvert."
    ),
    "datawatch did not accept it, so nothing was sent. The session may be showing a prompt "
    "to answer in datawatch.": (
        "datawatch ne l'a pas accepté, rien n'a donc été envoyé. La session affiche peut-être "
        "une demande à laquelle répondre dans datawatch."
    ),
    "datawatch did not accept it. Nothing was sent.": (
        "datawatch ne l'a pas accepté. Rien n'a été envoyé."
    ),
    "datawatch gives no folder for project {project}. Nothing was sent.": (
        "datawatch n'indique aucun dossier pour le projet {project}. Rien n'a été envoyé."
    ),
    "datawatch gives no history for a plan.": "datawatch ne fournit pas d'historique pour un plan.",
    "datawatch gives no reason.": "datawatch ne donne aucune raison.",
    "datawatch has no change record for it.": (
        "datawatch n'a aucun relevé des modifications à ce sujet."
    ),
    "datawatch has no history for {title}.": "datawatch n'a aucun historique pour {title}.",
    "datawatch links no open questions to the {item}. There are {number} open questions in "
    "all. Say all questions.": (
        "datawatch ne relie aucune question ouverte à : {item}. Il y a {number} questions "
        "ouvertes au total. Dites toutes les questions."
    ),
    "datawatch links no open questions to the {item}. There is {number} open question in "
    "all. Say all questions.": (
        "datawatch ne relie aucune question ouverte à : {item}. Il y a {number} question "
        "ouverte au total. Dites toutes les questions."
    ),
    "datawatch links no unread alerts to the {item}. There are {number} unread alerts in "
    "all. Say unset, then alerts.": (
        "datawatch ne relie aucune alerte non lue à : {item}. Il y a {number} alertes non lues "
        "au total. Dites retirer le focus, puis alertes."
    ),
    "datawatch links no unread alerts to the {item}. There is {number} unread alert in "
    "all. Say unset, then alerts.": (
        "datawatch ne relie aucune alerte non lue à : {item}. Il y a {number} alerte non lue "
        "au total. Dites retirer le focus, puis alertes."
    ),
    "datawatch made a new draft bug group for it.": (
        "datawatch a créé pour lui un nouveau groupe de bugs en brouillon."
    ),
    "datawatch made a one-task draft for it.": (
        "datawatch a créé pour lui un brouillon d'une seule tâche."
    ),
    "datawatch no longer has that session. Nothing was sent.": (
        "datawatch n'a plus cette session. Rien n'a été envoyé."
    ),
    "datawatch no longer has the project {project}. Nothing was sent.": (
        "datawatch n'a plus le projet {project}. Rien n'a été envoyé."
    ),
    "datawatch no longer has the {item}, so I moved your focus up.": (
        "datawatch n'a plus ceci : {item}. J'ai remonté votre focus d'un niveau."
    ),
    "datawatch no longer has the {item}.": "datawatch n'a plus ceci : {item}.",
    "datawatch records history for an automaton, not for one task. Choose its automaton to "
    "hear it.": (
        "datawatch garde l'historique d'un automate, pas d'une seule tâche. Choisissez son "
        "automate pour l'entendre."
    ),
    "datawatch refused access. Check the token in Home Assistant. Closing datawatch.": (
        "datawatch a refusé l'accès. Vérifiez le jeton dans Home Assistant. Fermeture de datawatch."
    ),
    "datawatch refused that answer because it looks like it holds a secret. Nothing was sent.": (
        "datawatch a refusé cette réponse car elle semble contenir un secret. Rien n'a été envoyé."
    ),
    "datawatch refused that answer. Nothing was sent.": (
        "datawatch a refusé cette réponse. Rien n'a été envoyé."
    ),
    "datawatch says: {reason}": "datawatch indique : {reason}",
    "datawatch's bug intake is turned off for project {project}. Nothing was sent.": (
        "La collecte de bugs de datawatch est désactivée pour le projet {project}. Rien n'a "
        "été envoyé."
    ),
    "done": "fait",
    "draft": "en brouillon",
    "error": "erreur",
    "failed": "en échec",
    "held": "en rétention",
    "in progress": "en traitement",
    "just now": "à l'instant",
    "not shipped": "non livré",
    "not started": "non commencé",
    "paused": "en pause",
    "plan {title}": "plan {title}",
    "planning": "en planification",
    "project {project}": "projet {project}",
    "queued": "en file d'attente",
    "review needed": "à relire",
    "running": "en cours",
    "session {title}": "session {title}",
    "shipped": "livré",
    "shipped in {release}": "livré dans {release}",
    "task {title}": "tâche {title}",
    "unknown": "inconnu",
    "unnamed": "sans nom",
    "untitled": "sans titre",
    "waiting decision": "en attente de décision",
    "waiting for input": "en attente de saisie",
    "waiting for review": "en attente de relecture",
    "warning": "avertissement",
    "{counts} across all projects.": "{counts} dans l'ensemble des projets.",
    "{done} of {number} task completed.": "Tâches terminées : {done} sur {number}.",
    "{done} of {number} tasks completed.": "Tâches terminées : {done} sur {number}.",
    "{done} of {total} automata done": "automates terminés : {done} sur {total}",
    "{done} of {total} automata done.": "Automates terminés : {done} sur {total}.",
    "{done} of {total} tasks completed": "tâches terminées : {done} sur {total}",
    "{first} and {last}": "{first} et {last}",
    "{found} among the newest {number}": "{found} parmi les {number} plus récentes",
    "{kind} from {when}": "{kind}, {when}",
    "{lead}{counts}.": "{lead}{counts}.",
    "{name} has no automata.": "{name} n'a aucun automate.",
    "{name} has no tasks.": "{name} n'a aucune tâche.",
    "{name} has nothing in it. Change it on the datawatch page in Home Assistant.": (
        "{name} ne contient rien. Modifiez-le sur la page datawatch de Home Assistant."
    ),
    "{name} has {number} automata.": "{name} a {number} automates.",
    "{name} has {number} automaton.": "{name} a {number} automate.",
    "{name} has {number} task.": "{name} a {number} tâche.",
    "{name} has {number} tasks.": "{name} a {number} tâches.",
    "{number} automata are running across all projects.": (
        "{number} automates sont en cours dans l'ensemble des projets."
    ),
    "{number} automata are running in project {project}.": (
        "{number} automates sont en cours dans le projet {project}."
    ),
    "{number} automata have completed across all projects.": (
        "{number} automates sont terminés dans l'ensemble des projets."
    ),
    "{number} automata have completed in project {project}.": (
        "{number} automates sont terminés dans le projet {project}."
    ),
    "{number} automata need attention, across all projects: {parts}.": (
        "{number} automates sont à traiter, tous projets confondus : {parts}."
    ),
    "{number} automaton has completed across all projects.": (
        "{number} automate est terminé dans l'ensemble des projets."
    ),
    "{number} automaton has completed in project {project}.": (
        "{number} automate est terminé dans le projet {project}."
    ),
    "{number} automaton is running across all projects.": (
        "{number} automate est en cours dans l'ensemble des projets."
    ),
    "{number} automaton is running in project {project}.": (
        "{number} automate est en cours dans le projet {project}."
    ),
    "{number} automaton needs attention, across all projects: {parts}.": (
        "{number} automate est à traiter, tous projets confondus : {parts}."
    ),
    "{number} current plan": "{number} plan actuel",
    "{number} current plans": "{number} plans actuels",
    "{number} day ago": "il y a {number} jour",
    "{number} days ago": "il y a {number} jours",
    "{number} failed or blocked automata": "{number} automates échoués ou bloqués",
    "{number} failed or blocked automaton": "{number} automate échoué ou bloqué",
    "{number} failed session": "{number} session en échec",
    "{number} failed sessions": "{number} sessions en échec",
    "{number} file": "{number} fichier",
    "{number} files": "{number} fichiers",
    "{number} finished or set aside with tasks held for review": (
        "{number} terminés ou mis de côté avec des tâches retenues pour relecture"
    ),
    "{number} held item": "{number} élément retenu",
    "{number} held items": "{number} éléments retenus",
    "{number} hour ago": "il y a {number} heure",
    "{number} hours ago": "il y a {number} heures",
    "{number} item is on hold, across all projects.": (
        "{number} élément est retenu, tous projets confondus."
    ),
    "{number} items are on hold, across all projects.": (
        "{number} éléments sont retenus, tous projets confondus."
    ),
    "{number} member": "{number} membre",
    "{number} members": "{number} membres",
    "{number} minute ago": "il y a {number} minute",
    "{number} minutes ago": "il y a {number} minutes",
    "{number} not started": "{number} non commencé",
    "{number} open question": "{number} question ouverte",
    "{number} open question, across all projects.": (
        "{number} question ouverte, tous projets confondus."
    ),
    "{number} open questions": "{number} questions ouvertes",
    "{number} open questions, across all projects.": (
        "{number} questions ouvertes, tous projets confondus."
    ),
    "{number} package": "{number} paquet",
    "{number} packages": "{number} paquets",
    "{number} plan": "{number} plan",
    "{number} plans": "{number} plans",
    "{number} plans archived.": "Plans archivés : {number}.",
    "{number} project": "{number} projet",
    "{number} project has something next.": "{number} projet a quelque chose à suivre.",
    "{number} projects": "{number} projets",
    "{number} projects have something next.": "{number} projets ont quelque chose à suivre.",
    "{number} running": "{number} en cours",
    "{number} session waiting for input": "{number} session en attente de saisie",
    "{number} sessions waiting for input": "{number} sessions en attente de saisie",
    "{number} task held for review": "{number} tâche retenue pour relecture",
    "{number} task is stuck. First: {title}, {state}.": (
        "{number} tâche est coincée. La première : {title}, {state}."
    ),
    "{number} tasks are stuck. First: {title}, {state}.": (
        "{number} tâches sont coincées. La première : {title}, {state}."
    ),
    "{number} tasks held for review": "{number} tâches retenues pour relecture",
    "{number} test": "{number} test",
    "{number} tests": "{number} tests",
    "{number} unread alert, across all projects, newest first.": (
        "{number} alerte non lue, tous projets confondus, la plus récente d'abord."
    ),
    "{number} unread alerts, across all projects, newest first.": (
        "{number} alertes non lues, tous projets confondus, les plus récentes d'abord."
    ),
    "{number} warning or error": "{number} avertissement ou erreur",
    "{number} warnings or errors": "{number} avertissements ou erreurs",
    "{number} {state}": "{number} {state}",
    "{number}, session named {name}, {state}": "{number}, session nommée {name}, {state}",
    "{plans} in {projects}.": "{plans} dans {projects}.",
    "{start}, and more": "{start}, et la suite",
    "{start}, and more. See datawatch for the rest.": (
        "{start}, et ce n'est pas tout. Consultez datawatch pour le reste."
    ),
    "{title} has no tasks.": "{title} n'a aucune tâche.",
    "{title} has {number} entries. The latest: {lines}": (
        "{title} a {number} entrées. Les dernières : {lines}"
    ),
    "{title} has {number} entry. The latest: {lines}": (
        "{title} a {number} entrée. La dernière : {lines}"
    ),
    "{title} is {state}.": "{title} : {state}.",
    "{what}, by {actor}": "{what}, par {actor}",
    "{where}: no automations.": "{where} : aucune automatisation.",
    "{where}: sessions, {counts}.": "{where} : sessions, {counts}.",
    "{where}: {number} automation, {parts}.": "{where} : {number} automatisation, {parts}.",
    "{where}: {number} automations, {parts}.": "{where} : {number} automatisations, {parts}.",
}
