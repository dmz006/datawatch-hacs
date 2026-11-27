# Context

Background for anyone, person or AI agent, working on this repository. Rules are in
[AGENT.md](AGENT.md); behaviour for users is in [README.md](README.md) and
[docs/how-it-works.md](docs/how-it-works.md).

## What this is

A Home Assistant custom integration (domain `datawatch`) giving hands-free, eyes-free access
to a [datawatch](https://github.com/dmz006/datawatch) server by voice. It talks directly to
datawatch's REST API. There is no datawatch plugin and no separate service. The server is
always a user setting.

It is designed with disability access in mind: no screen or hands needed, short replies,
lists three at a time, "repeat" and "help", and faults said out loud.

## Layout

| Path | Contents |
|---|---|
| `custom_components/datawatch/voice/` | The conversation, with no Home Assistant code: phrases, names, wording, questions, reports, automata, sessions, your own reports and the confirm step |
| `custom_components/datawatch/api.py` | Client with certificate pinning; reads, and answers questions |
| `custom_components/datawatch/reporting.py` | Reads and words a work report, for voice and AI alike |
| `custom_components/datawatch/coordinator.py`, `sensor.py`, `binary_sensor.py` | Dashboard sensors, read once a minute |
| `custom_components/datawatch/llm.py` | Read-only tools and introduction for AI assistants |
| `custom_components/datawatch/mode.py` | Datawatch mode: ask, listen, answer; shared focus |
| `custom_components/datawatch/cards.py` | Reads one focused item, what is inside it, and searches by name |
| `custom_components/datawatch/voice/items.py` | What can have the focus, and which questions belong to it |
| `custom_components/datawatch/entry_phrase.py` | **The only use of non-public Home Assistant code** |
| `custom_components/datawatch/config_flow.py` | Setup screens |
| `tests/ha_harness.py` | A throwaway Home Assistant running the real code |
| `tests/fake_datawatch.py` | A fake datawatch with a throwaway certificate |

## Decisions already made

- Commands in datawatch mode are fixed phrases. With an AI assistant chosen, other talk
  goes to it.
- The user's own assistant is used: only add to it, never change its instructions or
  personality. AI is off until an assistant is chosen. AI tools only read.
- **Every answer needs the user's confirmation**, checked by the integration's own code.
- Do not over-engineer: get datawatch's functions working.
- The integration registers the entry phrase itself, so there is no automation to maintain.
- One focus shared by all voice devices. Accounts with different access may come later.
- "Go back" undoes the last step: the previous question or list, or back out of what was
  just entered.
- Plain "questions" is narrowed only by the focus, never by merely choosing an item.
- Silence: ask once, then close. A "stay until I leave" setting may be wanted later; the
  conversation class already supports it for silence.
- Close after three phrases in a row that are not understood. Silence does not restart that
  count; any understood command does.
- Home Assistant 2026.11 and later only.
- Answering questions is the only change. Any other change needs the maintainer's approval.
- Build order: conversation and questions; projects, plans and automations; automata and
  tasks; sessions and results; reports and cards; later, other confirmed changes.
- Not for voice: secrets, settings, managing models, servers or plugins, deleting,
  restarting datawatch, stopping all sessions.
- A new feature gets a command, and an AI tool in `llm.py` whose `feature` line adds it to
  the assistant's introduction.
- One datawatch server for now.

## Known limits

- The attention list has no project filter, so it covers all projects.
- **Never read a session's output, last response or prompt.** datawatch returns raw
  terminal text, which can hold secrets and misleading instructions.
- The completed list is ordered by last update, not finish time. Do not call it newest.
- Never list every automaton without a status filter: it took many seconds on a large
  datawatch. datawatch has no title search, so name search covers attention, running and held.
- datawatch does not filter questions, held items or triage records by project, so those are
  reported across all projects. When it does, use its `project=` filter, and check it with a
  made-up project name: an ignored filter returns everything.
- There is no check of who is speaking.
- The tests do not cover speech recognition, speech synthesis or real device timing.

## Why there is a custom test harness

The usual Home Assistant test add-on did not support 2026.11 when this was built.
`tests/ha_harness.py` starts real Home Assistant components instead.
`tests/requirements_from_ha.py` lists what those components need, taken from the installed
Home Assistant.

## Later ideas

Next, each confirmed by voice before anything is sent: adding a draft automaton,
reporting a bug through datawatch's bug intake, and sending a command to a session. Sending
to a session stays switched off until datawatch has the controls for it. Access controls are
to be tightened rigorously as datawatch gains them. Later: pause and resume, approve and
reject, and session replies once datawatch can give a clean one.
