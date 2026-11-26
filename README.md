# datawatch for Home Assistant

Ask [datawatch](https://github.com/dmz006/datawatch) how your work is going, what needs you,
why something is stuck and what is next, hear its questions and answer them, by voice and without touching a screen.

datawatch is a program you run yourself. It starts AI coding assistants, watches them, plans
bigger jobs, and tells you when they need you. This integration lets you check on it from a
Home Assistant voice device.

> **Early release (0.4.0).** The only thing it can change in datawatch is **answering a
> question**, and only after you say **"confirm answer"**. Opening datawatch mode has been
> tried on a real Voice PE. The AI tools have been tried with typed requests to a real AI
> assistant. Reading and answering questions and the AI conversation have **not yet been
> tried by voice**. Sending an answer has been tested only against a pretend datawatch.

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
             reads; sends an answer only after "confirm answer"
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

Numbers work for the lists from "attention", "what's running" and "held items", and only for
lines you have heard. A reason is what datawatch recorded, so it can be long and technical.
It is never guessed; if there is none, you hear that. Finding by name searches only automata
that need attention, are running or are on hold: datawatch has no title search, and listing
every automaton is too slow for voice.

### Status and projects

| In datawatch mode, say | What you hear |
|---|---|
| "status" | Whether new work is paused, open questions, sessions waiting for you and running |
| "more detail" (after status) | Failed or blocked automata, items on hold, and failed sessions |
| "list projects", then "more" | Your projects three at a time, in alphabetical order, numbered |
| "set two" or "set project *name*" | Focus on a project. Part of a name works; if several match, you are asked which number |
| "where am I" | The current focus |
| "unset" | Clear the focus |
| "repeat" | The last reply again |
| "help" | The list of commands |
| "close datawatch", "stop", "exit" or "done" | Leave datawatch mode |

**Focus** saves you from naming a project every time. All your voice devices share it, and it
stays until you say "unset", even after you leave. With a focus, session counts are given
for that project and for everything else. datawatch cannot yet filter questions, items on
hold, or failed and blocked automata by project, so you hear those **across all projects**,
and the reply says so.

**You don't have to say "close".** If it hears nothing it asks "Still there?" once, and
after a second silence it closes. It also closes after three phrases in a row that it does
not understand. Saying "close datawatch" ends it straight away.

## Use your AI assistant (optional)

This is **off** until you turn it on. Go to **Settings → Devices & services → datawatch →
Configure** and choose an **AI assistant**. Leave it empty to turn it off again. Your
assistant's own instructions, personality and settings are not edited. datawatch only adds a
short introduction and these tools while it is on:

- status, projects and open questions
- what needs attention, what is running or on hold, plans and plan counts, what is next,
  and automations. When it answers for your focused project only, it is told to say so
- one automaton: progress, why it is stuck, and its tasks
- searching and reading datawatch's own documentation and how-tos

The introduction names only the features that work now.

- **In normal use**, ask your assistant, for example "any datawatch questions?". It must have
  **device control** turned on in its own settings; Home Assistant gives datawatch's tools to
  **every** assistant that has it, not only the chosen one.
- **In datawatch mode**, anything that is not a command goes to the chosen assistant, so you
  can talk it through without the wake word. Say "option two" or "my answer" when you are
  ready.
- **No assistant can send an answer.** It has no tool for that, and it never hears your
  "confirm answer" while an answer is waiting.

**Check the context size.** The added text and what the tools return take room in your
model's context window. If the window is too small, the model may lose older text,
including parts of its instructions. For a local model, check its context window setting.

## Privacy and safety

- **One kind of change.** It reads datawatch. The only thing it can send is your answer to a
  question, after you say "confirm answer".
- **No check of who is speaking.** Anyone who can talk to one of your voice devices can hear
  your datawatch questions, counts and project names, **and can answer questions**. Typed
  chat cannot start datawatch mode. An answer can let work go ahead, so think about where
  your voice devices are.
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
- The address, certificate fingerprint and any token are kept in Home Assistant's
  integration settings. The focus (a project name) is kept in Home Assistant's storage.

To report a security problem, see [SECURITY.md](SECURITY.md).

## Good to know

- **Background talk.** With the AI assistant off, it closes after three phrases in a row
  that it does not understand, even with silences between them. With the assistant **on**,
  other talk goes to the assistant instead, so this limit does not apply to it. Silence
  still closes it, and so does "stop".
- **Commands are fixed phrases.** With the AI assistant on, other wording goes to the
  assistant, which can talk about datawatch but cannot run the commands for you.
- **Not here yet:** sessions and results beyond the counts, and any change other than
  answering a question.
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
