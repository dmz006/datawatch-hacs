# Voice testing guide

A checklist for trying **every feature** of datawatch for Home Assistant, with examples to
start from. Work from top to bottom the first time. Copy the tables, or print them, and mark
each row **pass** or **fail**.

The examples use **made-up** names: a project called `oak`, and made-up work inside it. Use
your own names. Your counts and wording will differ, so check that each reply has the right
**shape** and matches what datawatch itself shows.

## Read this first

> **Three commands change your datawatch:** `confirm answer`, `confirm automation` and
> `confirm bug`. Everything else only reads. While testing, say them only for things you
> really want, or use a project made for testing. A confirmed answer can let work go ahead.
> A confirmed automaton or bug creates a **real draft**.

- **The integration does not check who is speaking.** Test where only you can be heard.
- **Wait for the voice device to finish talking** before you answer. A spoken turn can be
  about 15 seconds.
- In the tables, a command in `this style` is said as written. Words in *italics* are your
  own words.
- Marks: ⚠️ means the row changes datawatch.

## Before you start

| # | Check | Expect | Pass? |
|---|---|---|---|
| 0.1 | Say your wake word, then *what time is it* | Your usual assistant answers, as before | ☐ |
| 0.2 | In Home Assistant, open **Settings → Devices & services → datawatch** | It is set up, with no repair warning | ☐ |
| 0.3 | Look at the sensor **datawatch Open questions** | The same number datawatch shows (read once a minute) | ☐ |

If speech-to-text does not understand "datawatch", see
[Troubleshooting](troubleshooting.md#speech-to-text-does-not-understand-datawatch).

## 1. Opening, help and leaving

Say your wake word, then the opening words. After that, **no wake word** is needed until
datawatch mode closes.

| # | Say | Expect | Pass? |
|---|---|---|---|
| 1.1 | `open datawatch` | "Datawatch activated." then it listens | ☐ |
| 1.2 | `help` | A list of what you can say | ☐ |
| 1.3 | `repeat` | The same reply again | ☐ |
| 1.4 | `stop` | "Closing datawatch." | ☐ |
| 1.5 | `use datawatch`, then `exit` | Opens, then closes | ☐ |
| 1.6 | `datawatch`, then `done` | Opens, then closes | ☐ |
| 1.7 | `open datawatch`, then `close datawatch` | Opens, then closes | ☐ |
| 1.8 | `open datawatch`, then stay silent twice | "Still there?" once, then "Closing datawatch." | ☐ |
| 1.9 | `open datawatch`, then three things like *purple monkey* (with the AI assistant **off**) | "Sorry, I didn't get that. Say help." twice, then "I didn't understand three times. Closing datawatch." | ☐ |

## 2. Status and projects

| # | Say | Expect | Pass? |
|---|---|---|---|
| 2.1 | `status` | Whether new work is paused, open questions, sessions waiting and running | ☐ |
| 2.2 | `more detail` | Failed or blocked automata, held items, failed sessions | ☐ |
| 2.3 | `list projects` | The count first, then three at a time, A to Z, numbered | ☐ |
| 2.4 | `more` | The next three, numbers carrying on, or "That is the end of the list." | ☐ |

Example:

> **You:** "Status."
> **It:** "New work is paused. 4 open questions, 3 sessions waiting for input and 2 running.
> Say more detail for more."

## 3. Focus, and going back

| # | Say | Expect | Pass? |
|---|---|---|---|
| 3.1 | `set oak` (use a project of yours; part of a name works) | "Focus: project oak." | ☐ |
| 3.2 | `where am i` | The focus | ☐ |
| 3.3 | `status` | The focused project's numbers, then what is elsewhere | ☐ |
| 3.4 | `unset` | "Focus cleared. Now showing everything." | ☐ |
| 3.5 | `list projects`, then `set two` | Focus on the second project you heard | ☐ |
| 3.6 | `set project oak`, then `go back` | "Back." and the focus you had before | ☐ |
| 3.7 | `stop`, then `open datawatch` again | The focus is **still set** and is said on opening | ☐ |
| 3.8 | With a second voice device: set a focus on one, open datawatch on the other | The same focus (all voice devices share it) | ☐ |

## 4. Questions, and answering them

Needs at least one open question in datawatch.

| # | Say | Expect | Pass? |
|---|---|---|---|
| 4.1 | `questions` | "Question 1 of ...", who asks, the question, its options and any recommendation | ☐ |
| 4.2 | `more detail` | More about that question | ☐ |
| 4.3 | `next question` | The next one. Nothing is sent | ☐ |
| 4.4 | `option one` | "**Not sent yet.**" and your choice read back | ☐ |
| 4.5 | `cancel` | "Cancelled. Nothing was sent." | ☐ |
| 4.6 | `my answer is` *use the small one* | "Not sent yet." and your words read back. Say all of it in one turn, starting "my answer is" | ☐ |
| 4.7 | *yes* | **Nothing is sent:** "Not sent yet. Say confirm answer, or cancel." | ☐ |
| 4.8 | `cancel` | "Cancelled. Nothing was sent." | ☐ |
| 4.9 | `option one`, then `stop` | "Your answer was not sent. Closing datawatch." | ☐ |
| 4.10 ⚠️ | An answer you mean, then `confirm answer` | "Answer sent." Check it arrived in datawatch | ☐ |
| 4.11 | With a focus: `questions`, then `all questions` | First only those linked to the focus, then all | ☐ |

Example:

> **You:** "Questions."
> **It:** "Question 1 of 4, from datawatch. Should the made-up thing happen? Option 1: Yes,
> do it. Option 2: No, leave it. The asker recommends option 2. Say option and a number, my
> answer, more detail, or next question."
> **You:** "My answer is use the small one."
> **It:** "Not sent yet. The question begins: Should the made-up thing happen? Your words:
> use the small one. Say confirm answer to send it, or cancel."

## 5. What needs you, and one automaton

| # | Say | Expect | Pass? |
|---|---|---|---|
| 5.1 | `attention` | How many need you, across all projects, blocked first | ☐ |
| 5.2 | `one` | That automaton: state, project, tasks done | ☐ |
| 5.3 | `why` | datawatch's own reason, or that it gives none | ☐ |
| 5.4 | `tasks` | Its tasks, three at a time | ☐ |
| 5.5 | `progress` | Tasks done and what is left | ☐ |
| 5.6 | `history` | What datawatch recorded, or that it has none | ☐ |
| 5.7 | `its questions` | Questions linked to it, or that there are none | ☐ |
| 5.8 | `running` | What is running now | ☐ |
| 5.9 | `held`, then `why is one blocked` | Items on hold with reasons, then one in full | ☐ |
| 5.10 | `tell me about` *part of an automaton's name* | That automaton, or a short numbered choice | ☐ |
| 5.11 | `set it`, then `tasks` | Its tasks, without choosing again | ☐ |
| 5.12 | `unset`, `attention`, then `tell me about two` | The second automaton you heard | ☐ |

Name search looks among automata that need attention, are running or on hold, or finished
recently. It does not search everything.

Example:

> **You:** "Why."
> **It:** "Paint the made-up fence is blocked. datawatch says: the made-up paint ran out.
> 1 task is stuck. First: Paint it, blocked."

## 6. Plans and automations

Plans need datawatch's plan records turned on.

| # | Say | Expect | Pass? |
|---|---|---|---|
| 6.1 | `plans` | Current plans per project, with progress | ☐ |
| 6.2 | With a project focus: `plans`, then `one` | That plan's progress and goal | ☐ |
| 6.3 | `set it`, then `automata` | The automata inside the plan, in datawatch's order | ☐ |
| 6.4 | `go back` | Back to the plan | ☐ |
| 6.5 | `overview` (with a project focus) | Plans, progress and what is next | ☐ |
| 6.6 | `what's next` | What datawatch marks as next | ☐ |
| 6.7 | `automations` | Counts by state, then the unfinished ones | ☐ |
| 6.8 | `one`, then `set it`, then `automata` | The automation's members | ☐ |
| 6.9 | `unset` | "Focus cleared. Now showing everything." | ☐ |

## 7. Sessions and finished work

| # | Say | Expect | Pass? |
|---|---|---|---|
| 7.1 | `sessions` | Counts waiting, running and failed, then the **waiting** ones | ☐ |
| 7.2 | `one` | State, project, AI backend, last activity. **Never what it said** | ☐ |
| 7.3 | `waiting sessions`, `running sessions`, `failed sessions` | Those sessions | ☐ |
| 7.4 | `what finished` | Completed automata, most recently updated first | ☐ |
| 7.5 | `one`, then `results` | What it delivered, if datawatch has a record | ☐ |
| 7.6 | Choose a session, `set it`, then `send to session` *carry on* | "Sending to a session is **not turned on yet** ... Nothing was sent." | ☐ |
| 7.7 | `confirm send` | Nothing is sent: "There is nothing waiting to be sent." | ☐ |

## 8. Alerts

| # | Say | Expect | Pass? |
|---|---|---|---|
| 8.1 | `alerts` | How many are unread, then their **titles**, newest first | ☐ |
| 8.2 | `two` | That alert's title and age. "To read the rest, open datawatch." | ☐ |
| 8.3 | Check datawatch | The alert is **still unread** | ☐ |
| 8.4 | With a session focused: `alerts` | Only that session's alerts | ☐ |

## 9. List order

For sessions, automations and running work. See [List order](../README.md#list-order).

| # | Say | Expect | Pass? |
|---|---|---|---|
| 9.1 | `list order` | They are listed by name (unless you changed it) | ☐ |
| 9.2 | `automations` | A to Z | ☐ |
| 9.3 | `most recent first`, then `automations` | Recently updated first | ☐ |
| 9.4 | `stop`, open datawatch again, `list order` | Still most recent first | ☐ |
| 9.5 | Look at datawatch's **Configure** screen in Home Assistant | It shows **Most recent first** | ☐ |
| 9.6 | `sort by name` | Back to by name | ☐ |
| 9.7 | `plans` | The same order as before: plans are not re-sorted | ☐ |

## 10. Adding a bug or an automation

Set a **test project** first. The names below are made up.

| # | Say | Expect | Pass? |
|---|---|---|---|
| 10.1 | `unset`, then `add bug` | "Set a project first ..." | ☐ |
| 10.2 | `set oak`, then `add bug` | "Go ahead. Describe the bug, or cancel." | ☐ |
| 10.3 | *The gate latch is broken* | "**Not sent yet.**" and your words read back | ☐ |
| 10.4 | *yes* | **Nothing is sent:** "Not sent yet. Say confirm bug, or cancel." | ☐ |
| 10.5 | `confirm automation` | Still nothing sent: each thing has its own words | ☐ |
| 10.6 | `cancel` | "Cancelled. Nothing was sent." | ☐ |
| 10.7 | `add automation` *paint the shed*, then `cancel` | Read back, then cancelled | ☐ |
| 10.8 ⚠️ | `add bug` *a test bug you will delete*, then `confirm bug` | "Bug reported for project ..." Check datawatch | ☐ |
| 10.9 ⚠️ | `add automation` *a test you will delete*, then `confirm automation` | "Added a draft automaton ... I did not ask datawatch to plan or start it." Check datawatch | ☐ |

If you hear **"I don't know whether it was sent"**, look in datawatch **before** saying it
again.

Example:

> **You:** "Add bug the gate latch is broken."
> **It:** "Not sent yet. This is a bug for project oak. Your words: the gate latch is broken.
> Say confirm bug to send it, or cancel."
> **You:** "Confirm bug."
> **It:** "Bug reported for project oak. datawatch made a new draft bug group for it."

## 11. Your own reports

First add one in Home Assistant: see [Your own reports](../README.md#your-own-reports). For
example, a report named **morning** with status, attention and questions.

| # | Say | Expect | Pass? |
|---|---|---|---|
| 11.1 | `reports` | The names of your reports | ☐ |
| 11.2 | *morning* (your report's name) | A short sentence for each part | ☐ |
| 11.3 | *give me my morning report* | The same | ☐ |

## 12. With your AI assistant (optional)

Turn it on first: see [Use your AI assistant](../README.md#use-your-ai-assistant-optional).
An assistant words things its own way, so check the **facts** against datawatch.

**In normal use** (wake word, no "open datawatch"; the assistant needs device control):

| # | Say | Expect | Pass? |
|---|---|---|---|
| 12.1 | *Any datawatch questions?* | The real open questions | ☐ |
| 12.2 | *What needs my attention in datawatch?* | The same things datawatch shows | ☐ |
| 12.3 | *Why is* (an automaton's name) *blocked?* | datawatch's reason, not a guess | ☐ |
| 12.4 | *Which datawatch sessions are waiting?* | Names and states, never what they said | ☐ |
| 12.5 | *What does "held" mean in datawatch?* | An answer from datawatch's documentation | ☐ |
| 12.6 | *Answer that question with option one* | It says it **cannot**, and tells you how: open datawatch | ☐ |
| 12.7 | *Turn on* (a light of yours) | It still does its usual jobs, in its usual manner | ☐ |
| 12.8 | First set a project focus in datawatch mode and `stop`. Then ask *Is anything in datawatch stuck?* | If the list it reads covers **every** project, it says so | ☐ |

**Inside datawatch mode** (talk that is not a command goes to the assistant):

| # | Say | Expect | Pass? |
|---|---|---|---|
| 12.9 | `questions`, then *which would you pick and why?* | It discusses **that** question | ☐ |
| 12.10 | `option one`, then *go ahead and send it* | The assistant is not given this: "Not sent yet. Say confirm answer, or cancel." | ☐ |
| 12.11 | `cancel`, then *can you file a bug report for me?* | It does not file one. It tells you the command | ☐ |
| 12.12 | `stop` | datawatch mode closes | ☐ |

In datawatch mode, anything that **is** a command runs as a command. For example, *add a bug
for me* starts a bug, with "for me" as its words: say `cancel`.

## 13. When something is wrong

| # | Try | Expect | Pass? |
|---|---|---|---|
| 13.1 | With datawatch stopped or unreachable: `open datawatch`, `status` | "I can't reach datawatch ..." No made-up numbers | ☐ |
| 13.2 | At the same time, look at the sensors | **Unavailable**, not zero | ☐ |
| 13.3 | Start datawatch again, `status` | Works again, with no restart of Home Assistant | ☐ |
| 13.4 | Type "open datawatch" in the Assist chat window | "Datawatch mode works from a voice device." | ☐ |

Only stop datawatch if that will not disturb your work.

## 14. Dashboard cards and sensors

Not voice, but part of a full test. See
[datawatch's dashboard cards](../README.md#datawatchs-dashboard-cards). Try them on a
**phone** as well as a computer.

| # | Do | Expect | Pass? |
|---|---|---|---|
| 14.1 | **Add card**, search **datawatch** | A project Gantt and a lane activity card | ☐ |
| 14.2 | Gantt: choose a project | Its automations with done and total counts | ☐ |
| 14.3 | Gantt: tap a row | Its automata, with states and dates | ☐ |
| 14.4 | Gantt: **7**, **30**, **90 days**, **All** | The range changes; open work stays | ☐ |
| 14.5 | Compare one row's counts with datawatch | They agree | ☐ |
| 14.6 | Lane card | One line per busy lane; idle lanes named | ☐ |
| 14.7 | Tap a lane's name | Its line stands out | ☐ |
| 14.8 | Wait 5 minutes | The "up to" time moves on | ☐ |
| 14.9 | Enable a number sensor and wait | It has a value, or **unknown**, and builds history | ☐ |
| 14.10 | Set your Home Assistant profile language to German, Spanish, French or Japanese, then open a dashboard with the cards | Card text, dates and the names in **Add card** are in that language; datawatch's own names are unchanged | ☐ |
| 14.11 | With that language, open the datawatch setup and settings screens | Their text is in that language; the spoken commands they quote stay in English | ☐ |
| 14.12 | Set the language back to English | Everything is in English again | ☐ |

## 15. Not available yet

Asking for these should **not** do anything: starting, approving, pausing, stopping or
deleting work; sending to a session (switched off); a queue view; a Kanban board; reading
what a session said.

## Reporting what you find

[Open an issue](https://github.com/dmz006/datawatch-hacs/issues) with the row number, what
you said, what you heard, and your Home Assistant, datawatch and integration versions.
**Remove names, addresses and anything private first.** For a security problem, follow
[SECURITY.md](../SECURITY.md) instead.
