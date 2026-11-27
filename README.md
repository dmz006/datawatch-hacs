# datawatch for Home Assistant

Ask [datawatch](https://github.com/dmz006/datawatch) how your work is going, what needs you,
why something is stuck, what your sessions are doing and what is next, hear its questions and
answer them, hear its alerts, add an automation or report a bug, by voice and without
touching a screen. It can also bring datawatch's numbers into Home Assistant for your own
dashboards, with a live Gantt card of its own.

datawatch is a program you run yourself. It starts AI coding assistants, watches them, plans
bigger jobs, and tells you when they need you. This integration lets you check on it from a
Home Assistant voice device.

> **Early release (0.10.0).** It can change datawatch in three ways: **answer a question**,
> **add a draft automaton** and **report a bug**. Each is sent only after you confirm it
> aloud. Opening datawatch mode has been
> tried on a real Voice PE. The AI tools have been tried with typed requests to a real AI
> assistant. Reading and answering questions and the AI conversation have **not yet been
> tried by voice**. Sending an answer has been tested only against a pretend datawatch.
> Focus and "go back" have been tried against a real datawatch with a pretend voice device,
> **not yet by voice**. Adding an automaton and reporting a bug have been tested only against
> a pretend datawatch. Alerts and the dashboard data sensors have been tried against a real
> datawatch from a test copy of Home Assistant; alerts **not yet by voice**. The Gantt card
> has been tested in a headless Chrome, **not yet inside a Home Assistant dashboard**.

## How it works

```text
You  <-- speak and listen -->  Voice device
                                    |
                     Home Assistant |
                     your speech-to-text and text-to-speech
                                    |
                     Did you say "open datawatch"?
                       |                           |
                      no                          yes
                       |                           |
              your usual assistant          datawatch mode
              (may read datawatch,            |          |
               if you turn that on)       commands    other talk
                       |                      |      (to your chosen AI,
                       |                      |       if you turn it on)
                       +----------+-----------+
                                  |
                  HTTPS, only the certificate you approved
                                  |
                        Your datawatch server
               reads; changes only what you confirm aloud
```

Say your wake word and **"open datawatch"**. From then on you are in **datawatch mode**: it
answers, keeps listening, and you give short commands without the wake word. When you
leave, your usual assistant is back, unchanged.

More diagrams and detail: [How it works](docs/how-it-works.md).

## What a conversation sounds like

The counts and the question are made up.

> **You:** "Hey Jarvis, open datawatch." *(use your own wake word)*
> **It:** "Datawatch activated."
> **You:** "Questions."
> **It:** "Question 1 of 4, from the supervisor. May the nightly job start. Option 1: Yes.
> Option 2: Wait until morning. The asker recommends option 2. Say option and a number, my
> answer, more detail, or next question."
> **You:** "Option two."
> **It:** "Not sent yet. The question begins: May the nightly job start. Your choice: option
> 2, Wait until morning. Say confirm answer to send it, or cancel."
> **You:** "Confirm answer."
> **It:** "Answer sent. Say next question."
> **You:** "Close datawatch."
> **It:** "Closing datawatch."

## What you need

- **Home Assistant 2026.11 or later.** Older versions are not supported.
- **datawatch**, reachable from Home Assistant over HTTPS. Developed against datawatch
  9.187.
- **A voice device that can hold a conversation**, such as Home Assistant Voice PE.
- **An assistant with speech-to-text and text-to-speech** set up for that device. It works
  whether the assistant is Home Assistant's own or an AI model.

## Install

1. In Home Assistant, open the **Marketplace** and add `dmz006/datawatch-hacs` as a custom
   repository of the type *integration*. Home Assistant asks you to connect a GitHub account
   to add custom repositories.
2. Download **datawatch**, then restart Home Assistant when it suits you.
3. Go to **Settings → Devices & services → Add integration → datawatch**.

## Set up

1. Enter your datawatch server's address, starting with `https://`, including the port if it
   needs one. Use an address that **Home Assistant** can reach. Add a token only if your
   datawatch uses one.
2. The next screen shows the server certificate's fingerprint. **Check it** against the
   certificate on the datawatch server. On that server run:

   ```bash
   openssl x509 -in ~/.datawatch/tls/server/cert.pem -noout -fingerprint -sha256
   ```

   That is where datawatch keeps the certificate it makes itself. If you use your own
   certificate, give that file instead.
3. Submit only if the two match. From then on only that certificate is accepted. Nothing,
   including your token, is sent before you approve it.

To change the address or token, or to approve a replaced certificate, choose
**Reconfigure** on the integration. One datawatch server is supported for now.

**Recommended if you use the Whisper app:** give it a hint so it recognises the word
"datawatch". See
[Speech-to-text does not understand "datawatch"](docs/troubleshooting.md#speech-to-text-does-not-understand-datawatch).

## What you can say

To start: your wake word, then **"open datawatch"**, **"use datawatch"** or just
**"datawatch"**.

### Questions and answers

| In datawatch mode, say | What happens |
|---|---|
| "questions" or "what's the first question" | Reads the first open question in full, with its options and the asker's recommendation |
| "next question" (or "next") | Reads the next one |
| "go back" | The previous question |
| "more detail" | What each option costs or gives, and why one is recommended |
| "option two" (or "answer two", "two") | Chooses an option and reads it back. **Not sent yet** |
| "my answer is …" | Answers in your own words, and reads them back. **Not sent yet** |
| "my answer", then speak | The same, with your whole next turn as the answer |
| "confirm answer" | **Sends** the answer that was just read back |
| "cancel" | Drops it |

The supervisor's questions come first, and in each group the ones blocking work come first.
A spoken turn can be about 15 seconds long.

**Nothing is sent until you say "confirm answer".** No shorter word such as "yes" does it.
Before sending, it checks that the question is still open. It never replaces an answer. Your
own words are saved as speech-to-text wrote them, so **listen to the read-back**. You can
give an option and your own words together: say one, then the other. If you leave first, you
hear that your answer was not sent. If the connection fails while sending, it tells you that
it does not know whether the answer arrived, and does not try again by itself. datawatch
marks these answers as coming from voice. To correct a sent answer, use datawatch.

### Work: attention, plans and automations

| In datawatch mode, say | What you hear |
|---|---|
| "what needs my attention" or "attention" | How many automata datawatch says need you, then the blocked ones first |
| "how many plans do we have" or "plans" | Current plans per project. With a focus, that project's plans in datawatch's order, with progress |
| "overview" | With a focus: that project's plans, progress and what is next |
| "what's next" | What datawatch marks as next, for your focus or for every project |
| "automations" | Counts by status, then the unfinished ones, in datawatch's order. With a focus, only that project's |

Long lists are read **three at a time**: say "more". "What needs my attention" always covers
all projects, because datawatch cannot filter that list by project. Like datawatch's own web
app, it includes finished or cancelled automata that still have a task held for review.
Plans need datawatch's plan records to be turned on.

### One automaton: why it is stuck, and its tasks

| In datawatch mode, say | What you hear |
|---|---|
| "what's running" | The automata running now, numbered. With a focus, only that project's |
| "what's on hold" or "held items" | What is on hold, numbered, with the start of each reason. Covers all projects |
| "two" or "tell me about two" | That line of the list: its status, project and task progress |
| "tell me about *part of a title*" | Finds it by name. If several match, they are numbered |
| "why" or "why is two blocked" | datawatch's own reason: why it is blocked or held, and any stuck or waiting task |
| "tasks" or "tasks for two" | Its tasks and their statuses, three at a time |
| "progress" | How many tasks are done and what the rest are doing |

Numbers work for lines you have heard in the lists of automata, plans, automations, tasks
and sessions. A reason is what datawatch recorded, so it can be long and technical.
It is never guessed; if there is none, you hear that. Finding by name searches only automata
that need attention, are running or are on hold, then recently updated completed ones: datawatch has no title search, and listing
every automaton is too slow for voice.

### Sessions and finished work

| In datawatch mode, say | What you hear |
|---|---|
| "sessions" | How many are waiting for input, running and failed, then the waiting ones, numbered |
| "waiting sessions", "running sessions", "failed sessions" | Those sessions, numbered. With a focus, only that project's |
| "two" after a session list | That session: state, project, AI backend and when it was last active |
| "what finished" | Completed automata with the release each shipped in, if datawatch recorded one |
| "results" or "results for two" | What a chosen automaton delivered: tasks completed, and counts of changed files, packages and added tests if datawatch has a change record |

**What a session said is not read out.** datawatch returns recent terminal screen text
rather than just the last reply: long, cluttered, and able to hold secrets. Open the session
in datawatch to read it. "What finished" lists the **most recently updated** first, because
datawatch orders it that way. That may not be the order things finished. It can take several
seconds on a large datawatch.

### Alerts

| In datawatch mode, say | What you hear |
|---|---|
| "alerts" or "any alerts" | How many are unread, how many of those listed are warnings or errors, then their titles, newest first |
| "two" | That alert's title, whether it is a warning, and how long ago |
| "alerts" with a **session** focused | Only the alerts datawatch links to that session |

**Only titles are read.** The text of an alert can be raw terminal screen text, which can
hold secrets, so it is never read out or given to an AI assistant. Open datawatch to read
it. Hearing an alert does not mark it read. A project, plan or automaton focus does not
narrow alerts, because datawatch links an alert only to a session. datawatch sends its
newest alerts only, so a long backlog is not all listed.

### Status and projects

| In datawatch mode, say | What you hear |
|---|---|
| "status" | Whether new work is paused, open questions, sessions waiting for you and running |
| "more detail" (after status) | Failed or blocked automata, items on hold, and failed sessions |
| "list projects", then "more" | Your projects three at a time, in alphabetical order, numbered |
| "set two" or "set project *name*" | Focus on a project. Part of a name works; if several match, you are asked which number |
| "where am I" | The current focus |
| "unset" | Clear the whole focus |
| "repeat" | The last reply again |
| "help" | The list of commands |
| "close datawatch", "stop", "exit" or "done" | Leave datawatch mode |

### Focus: stop repeating yourself

You can **focus** on a project, and then on a **plan, automation, automaton, task or
session** inside it. After that you do not have to name it again.

| In datawatch mode, say | What happens |
|---|---|
| "set two" | Focus on line 2 of the list you are hearing |
| "set it" | Focus on the one you just chose |
| "set plan *name*" (or automation, automaton, task, session) | Focus by part of a name. If several fit, you are asked which number |
| "status", "more detail" | About the focused item |
| "why", "progress", "results" | About the focused item (results are for automata) |
| "history" | What datawatch recorded: for an automaton or an automation |
| "automata" | What is inside a focused or chosen plan or automation |
| "tasks" | The tasks of a plan or an automaton |
| "questions" | With an item focused, only the open questions datawatch links to it |
| "its questions" or "questions for two" | The questions for the item you chose, without focusing on it |
| "all questions" | Every open question, whatever the focus |
| "go back" | Undo your last step: the previous question or list, or back out of what you just went into. With no earlier step, the focus moves up one level |
| "where am I" | The whole focus, for example "project oak, plan Roots, task Paint it" |
| "unset" | Clear the whole focus |

For example (the names, counts and question are made up):

> **You:** "Set project oak." **It:** "Focus: project oak."
> **You:** "Plans." **It:** "Project oak has 2 current plans. Also 3 archived. Plan 1,
> Roots: in progress, 2 of 5 automata done. Plan 2, Leaves: planned. That is all."
> **You:** "Set one." **It:** "Focus: project oak, plan Roots."
> **You:** "Status." **It:** "Plan Roots: in progress. 2 of 5 automata done. Say more detail
> for more."
> **You:** "Questions." **It:** "For the plan Roots. Question 1 of 1, from datawatch. May the
> fence be painted? Option 1: Yes, do it. Option 2: No, leave it. The asker recommends
> option 2. Say option and a number, my answer, more detail, or next question."
> **You:** "Go back." **It:** "Back. Focus: project oak, plan Roots."
> **You:** "Unset." **It:** "Focus cleared. Now showing everything."

All your voice devices share the focus, and it stays until you change it, even after you
leave. "Go back" remembers the steps of the visit you are in. It never undoes an answer you
sent, and it drops one that is still waiting for "confirm answer".

What a focus can and cannot narrow:

- **Questions** are narrowed only when datawatch records a link to the item. A question that
  names no automaton does not show under a plan, an automation or an automaton, and few
  questions name a task or a session. You hear how many are open in all.
- A **project** focus does not narrow questions, items on hold, or failed and blocked
  automata, because datawatch cannot filter those by project yet. The reply says "across all
  projects". With a project focus, session counts are given for that project and for
  everything else.
- **Sessions** are narrowed to a focused automation or automaton.
- Inside a large plan, you can hear its first 50 automata or tasks, in datawatch's order.
  That can start with finished ones.
- datawatch gives **no history** for a plan or a single task, and history for a session is
  not read.

**You don't have to say "close".** If it hears nothing it asks "Still there?" once, and
after a second silence it closes. It also closes after three phrases in a row that it does
not understand. Saying "close datawatch" ends it straight away.

## Add an automation or report a bug

Set a **project** first. Then say what you want, and your words, either in one go or in two
turns. A spoken turn can be about 15 seconds long.

| In datawatch mode, say | What happens |
|---|---|
| "add automation" or "new automation" | Asks what it should do, then reads it back. **Not sent yet** |
| "add automation: *what it should do*" | The same, in one go |
| "confirm automation" | **Adds a draft automaton** to the project |
| "add bug" or "report bug" | Asks you to describe it, then reads it back. **Not sent yet** |
| "add bug: *what is wrong*" | The same, in one go |
| "confirm bug" | **Reports the bug** to datawatch's bug intake |
| the same command again | Replaces your words |
| "cancel" or "go back" | Drops it |

For example (the project and words are made up):

> **You:** "Set project oak." **It:** "Focus: project oak."
> **You:** "Add bug." **It:** "Go ahead. Describe the bug, or cancel."
> **You:** "The gate latch is broken." **It:** "Not sent yet. This is a bug for project oak.
> Your words: The gate latch is broken. Say confirm bug to send it, or cancel."
> **You:** "Confirm bug." **It:** "Bug reported for project oak. datawatch made a new draft
> bug group for it."

- **Each thing has its own words.** "Confirm bug" cannot send an automaton or an answer, and
  "yes" sends nothing.
- **Your words are sent as speech-to-text wrote them,** so listen to the read-back. While it
  waits for your words, your whole next turn is taken as them, even if it sounds like a
  command. Say "cancel" to stop.
- **The name** given to it is the first sentence of your words, up to 80 characters.
- **An automaton is added as a draft.** The integration does not ask datawatch to plan or
  start it. It needs datawatch to give a folder for the project.
- **A bug goes to datawatch's bug intake,** which adds it to a draft bug group or makes one.
  If the intake is turned off for that project, you are told.
- **Sent once.** If the connection fails, you hear that it is not known whether it arrived.
  **Check datawatch before saying it again,** or you may add it twice.
- **datawatch's "Automation"** (a chain of automata) is not what "add automation" makes: it
  adds one new automaton.

**Sending to a session** ("send to session", then "confirm send") is built but **switched
off**. It is waiting for datawatch's access controls, and says so if you try.

## Your own reports

Make a spoken report of just what you care about.

1. Go to **Settings → Devices & services → datawatch** and choose **Add report**.
2. Name it, for example "Daily report", and choose what goes in it: status, more detail,
   attention, questions, what's next, plans, running automata, held items, sessions or
   automations.
3. In datawatch mode, say its name: **"daily report"** (or just "daily"). Say **"reports"**
   to hear the names.

Each part is a sentence or two, mostly counts, in the order the screen lists them, so it
stays short. To hear a list afterwards, say the command for it, such as "attention". With a
focus, parts that can cover one project do. Change or delete a report on the same page. A
name cannot be words datawatch mode already uses, such as "status".

## Dashboard sensors

datawatch adds a **datawatch** service with these entities, for dashboards and your own
automations:

| Entity | Shows |
|---|---|
| `binary_sensor.datawatch_new_work_paused` | On while new work is paused |
| `sensor.datawatch_open_questions` | Open questions |
| `sensor.datawatch_automata_needing_attention` | Automata that need you |
| `sensor.datawatch_sessions_waiting_for_input` | Sessions waiting for input |
| `sensor.datawatch_sessions_running` | Running sessions |
| `sensor.datawatch_sessions_failed` | Failed sessions |
| `sensor.datawatch_automata_failed_or_blocked` | Failed or blocked automata |
| `sensor.datawatch_items_on_hold` | Items on hold |

They cover all projects, are **read from datawatch once a minute**, and show
*unavailable*, never zero, when datawatch cannot be read. Home Assistant keeps their history
like any other sensor. The names above are the defaults, and yours may differ if you rename
them. To stop the reading, turn off **polling** in the integration's system options.

Your dashboards are not changed. To add a card, choose **Add card → Manual** and paste:

```yaml
type: entities
title: datawatch
entities:
  - binary_sensor.datawatch_new_work_paused
  - sensor.datawatch_open_questions
  - sensor.datawatch_automata_needing_attention
  - sensor.datawatch_sessions_waiting_for_input
  - sensor.datawatch_sessions_running
  - sensor.datawatch_automata_failed_or_blocked
  - sensor.datawatch_items_on_hold
```

## Data for your own cards (optional)

The integration can also bring datawatch's smaller dashboard data into Home Assistant, so
you can build your own cards and graph numbers over time. **All of these sensors start
disabled.** To enable one: **Settings → Devices & services → datawatch**, open its device or
entity list, choose the disabled entity, and turn **Enabled** on. Home Assistant starts it
after a short reload. They are read every **5 minutes**.

> **History starts when you enable a sensor.** Home Assistant cannot fill in earlier values,
> so enable the numbers you may want to graph as soon as you can.

**Data sensors.** Each shows one headline number and holds its data in an attribute named
`data`:

| Sensor (`sensor.datawatch_...`) | Headline number | `data` holds |
|---|---|---|
| `dashboard_data_overview` | Open questions | Summaries of questions, stuck work, lanes, usage, CI and release |
| `dashboard_data_lane_activity` | Lanes in the last 6 hours | When each lane was busy, waiting or idle, and usage readings |
| `dashboard_data_lane_use` | Lanes in the last 24 hours | How busy each lane was, hour by hour |
| `dashboard_data_bugs` | Bugs taken in, last 14 days | Bugs per day. datawatch's "fixed" counts bugs it made a one-task fix for, not finished fixes |
| `dashboard_data_review_backlog` | Automata waiting for a decision | Their titles and how long they have waited (50 at most) |
| `dashboard_data_forecast` | Automata finished per day | The forecast over the last 30 days |
| `dashboard_data_live_work` | Task bars in the last 6 hours | What the [Gantt card](#the-gantt-card-live-work) draws |

**The `data` attribute is not saved in history.** It is current data only, in the shape
datawatch sends it, which can change with datawatch versions. The one free-text note in the
overview is left out. It includes titles, lane names, repository names and links.

**Number sensors.** These keep history and long-term statistics:

| Sensor (`sensor.datawatch_...`) | Number |
|---|---|
| `weekly_usage_used` | Weekly allowance used, in percent |
| `weekly_usage_pace_line` | Where the pace line is now, in percent |
| `weekly_usage_used_per_24_hours` | datawatch's burn rate: percent of the weekly allowance per 24 hours |
| `held_questions_awaiting_a_decision` | Held questions waiting for you |
| `longest_wait_for_a_decision` | Hours since the longest-waiting item last changed |
| `forecast_days_to_finish_low`, `..._high` | datawatch's estimate of the days left |
| `lane_<name>_busy_last_full_hour` | One for each lane: the share of the last full clock hour it was busy |

The headline numbers above keep history too, and so do the
[count sensors](#dashboard-sensors), which are on from the start.

**"Unknown" is on purpose.** A number datawatch does not give is unknown, not zero. Usage is
unknown while datawatch calls its reading stale. The forecast is unknown when datawatch's
newest forecast point is more than a day old (by UTC date); the older points are still in
`data`. A lane sensor is unknown when datawatch reports nothing for that lane. A lane is
added when datawatch first reports it.

### The Gantt card (live work)

The integration comes with its own dashboard card. It shows **the last 6 hours**: a row for
each datawatch lane, then the tasks of work that is **running, blocked or being planned**.
It updates every **5 minutes**.

1. Enable the sensor **Dashboard data: live work** (it starts disabled, like the others).
2. Reload the page in your browser. In the mobile app, close it and open it again.
3. In a dashboard, choose **Add card**, search for **datawatch Gantt**, and add it.

You do not need an add-on or to write YAML. If you prefer YAML:

```yaml
type: custom:datawatch-gantt-card
title: datawatch live work   # optional
```

- A bar's label gives its state in words, and pointing at it, or moving to it with the
  keyboard, gives its times. A bar with a dark right edge was still running.
- A lane with nothing in the 6 hours says **idle**. When datawatch is paused, there may be
  no task bars at all.
- Work that **finished** (completed, cancelled or archived) is not listed under tasks.
- It reads at most **20** unfinished automata and says how many more there are. This follows
  the rules of datawatch's own Gantt card.
- datawatch sends whole records for this, with task instructions and history; they can be
  large (about 1 MB with six automata). **Only titles, states and times are kept.**

**A graph over time** with Home Assistant's own card. In a dashboard, add a card, choose
**Manual**, and paste this, after enabling the sensor in it:

```yaml
type: history-graph
title: datawatch
hours_to_show: 48
entities:
  - sensor.datawatch_weekly_usage_used
  - sensor.datawatch_weekly_usage_pace_line
```

Apart from the Gantt card, drawing the lists in `data` (for example a chart of bugs per day)
needs a card that can read attributes; Home Assistant's history cards cannot. datawatch's large work map and timeline
are not included.

## Use your AI assistant (optional)

This is **off** until you turn it on. Go to **Settings → Devices & services → datawatch →
Configure** and choose an **AI assistant**. Leave it empty to turn it off again. Your
assistant's own instructions, personality and settings are not edited. datawatch only adds a
short introduction and these tools while it is on:

- status, projects, what you are focused on, and open questions
- what needs attention, what is running or on hold, plans and plan counts, what is next,
  and automations. When it answers for your focused project only, it is told to say so
- one automaton: progress, why it is stuck, its tasks and what it delivered
- sessions and their states (**never what they said**), completed work, and unread alert
  titles (never an alert's text)
- your own reports
- searching and reading datawatch's own documentation and how-tos

The introduction names only the features that work now.

- **In normal use**, ask your assistant, for example "any datawatch questions?". It must have
  **device control** turned on in its own settings; Home Assistant gives datawatch's tools to
  **every** assistant that has it, not only the chosen one.
- **In datawatch mode**, anything that is not a command goes to the chosen assistant, so you
  can talk it through without the wake word. Say "option two" or "my answer" when you are
  ready.
- **No assistant can answer, add, report or send anything.** It has no tool for that, and it
  does not hear what you say while you dictate something or while it waits to be confirmed.
  It is told which commands do these, so it can tell you.

**Check the context size.** The added text and what the tools return take room in your
model's context window. If the window is too small, the model may lose older text,
including parts of its instructions. For a local model, check its context window setting.

**An AI assistant can be wrong.** It can misread a result or say something no tool told it.
The fixed commands in datawatch mode read datawatch's data directly. Check anything that
matters in datawatch.

## Privacy and safety

- **Dashboard data stays in Home Assistant**, only for sensors you enable. Anyone who can see
  those entities can read the titles in them. With no data sensor enabled, one small lane
  summary is still read every 5 minutes, to know which lanes exist.

- **Three kinds of change.** It reads datawatch. It can answer a question, add a draft
  automaton and report a bug, each only after you confirm it aloud. Sending to a session is
  switched off.
- **No check of who is speaking.** Anyone who can talk to one of your voice devices can hear
  your datawatch questions, counts and project names, **and can answer questions, add
  automata and report bugs**. Typed chat cannot start datawatch mode. An answer can let work
  go ahead, so think about where your voice devices are. Confirming words guard against
  mistakes, not against another person.
- **AI and text from datawatch.** With the AI assistant on, datawatch text goes to your AI
  model. Questions are written by programs and could contain text meant to mislead a model.
  The model is told to treat it as information only, but that is **not a guarantee**. It
  cannot send an answer, but it keeps whatever control of your home you gave it. Check that
  your assistants cannot control anything sensitive, such as locks or garage doors. While
  you are in datawatch mode, other talk in the room can reach the assistant without the wake
  word.
- **Your server only.** It connects to the address you enter, and only to a server showing
  the certificate you approved.
- **Speech** is turned into text by the speech-to-text service your assistant already uses.
  With the AI assistant off, your words in datawatch mode are not passed on to an AI model.
- **Sensors** read counts once a minute, and their history is stored by Home Assistant,
  as is the history of any number sensor you enable. Anyone who can see your Home Assistant can see them.
- The address, certificate fingerprint and any token are kept in Home Assistant's
  integration settings. The focus (the names and ids of what you focused on, which for a
  session includes your datawatch host name if datawatch puts it in the id) is kept in Home
  Assistant's storage.

To report a security problem, see [SECURITY.md](SECURITY.md).

## Good to know

- **Background talk.** With the AI assistant off, it closes after three phrases in a row
  that it does not understand, even with silences between them. With the assistant **on**,
  other talk goes to the assistant instead, so this limit does not apply to it. Silence
  still closes it, and so does "stop".
- **Commands are fixed phrases.** With the AI assistant on, other wording goes to the
  assistant, which can talk about datawatch but cannot run the commands for you.
- **Not here:** what a session said, files or other output you can open, sending to a
  session (switched off for now), and any other change, such as starting, approving,
  stopping or deleting work.
- **Home Assistant upgrades.** Home Assistant has no public way for an integration to add a
  spoken phrase, so this one uses the same internal function as Home Assistant's own
  sentence automations. An upgrade could change it. If registering the phrase fails, Home
  Assistant shows a repair warning, though not every possible change would be caught that
  way. Tests run against the newest Home Assistant on each change and weekly.

Something not working? See [Troubleshooting](docs/troubleshooting.md).

## Remove

Delete datawatch under **Settings → Devices & services**, which also forgets the focus. Then
uninstall it in the Marketplace and restart. Nothing in your assistant needs undoing.

## Development

See [CONTEXT.md](CONTEXT.md) for how the project fits together and [AGENT.md](AGENT.md) for
the working rules.

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[test,lint]"
.venv/bin/pip install $(.venv/bin/python tests/requirements_from_ha.py)
.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy
.venv/bin/pytest --cov
```

This repository is public. Turn on the hooks once per clone:

```bash
git config core.hooksPath .githooks
```

Before a push, the hooks run the leak checks, lint, type checks and tests, and refuse a
failing or half-committed tree. They need [gitleaks](https://github.com/gitleaks/gitleaks)
and a private list of words that must never be published, at
`~/.config/datawatch-hacs/leak-denylist.txt` (or `LEAK_DENYLIST=/path`): one per line, such
as your own host names, addresses and device names. Keep that file out of the repository.
Use made-up data in code, tests and documentation.

## License

[PolyForm Noncommercial 1.0.0](LICENSE).
