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
| `custom_components/datawatch/voice/` | The conversation, with no Home Assistant code: phrases, names, wording |
| `custom_components/datawatch/api.py` | Read-only client with certificate pinning |
| `custom_components/datawatch/mode.py` | Datawatch mode: ask, listen, answer; shared focus |
| `custom_components/datawatch/entry_phrase.py` | **The only use of non-public Home Assistant code** |
| `custom_components/datawatch/config_flow.py` | Setup screens |
| `tests/ha_harness.py` | A throwaway Home Assistant running the real code |
| `tests/fake_datawatch.py` | A fake datawatch with a throwaway certificate |

## Decisions already made

- Fixed phrases in datawatch mode, not AI interpretation. That may be revisited.
- The integration registers the entry phrase itself, so there is no automation to maintain.
- One focus shared by all voice devices. Accounts with different access may come later.
- Silence: ask once, then close. A "stay until I leave" setting may be wanted later; the
  conversation class already supports it.
- Home Assistant 2026.11 and later only.
- Read only for now. Anything that changes datawatch needs its own design.
- One datawatch server for now.

## Known limits

- datawatch does not filter questions, held items or triage records by project, so those are
  reported across all projects. When it does, use its `project=` filter, and check it with a
  made-up project name: an ignored filter returns everything.
- Any heard words restart the silence count.
- There is no check of who is speaking.
- The tests do not cover speech recognition, speech synthesis or real device timing.

## Why there is a custom test harness

The usual Home Assistant test add-on did not support 2026.11 when this was built.
`tests/ha_harness.py` starts real Home Assistant components instead.
`tests/requirements_from_ha.py` lists what those components need, taken from the installed
Home Assistant.

## Later ideas

Browsing plans, automations, automata, tasks and sessions; answering questions one at a
time; sending a command to a session; adding an automation or a bug report; reports you
define yourself; dashboard cards; AI tools for the user's assistant. Any AI context must
**only add to** a user's assistant, never change its personality or instructions, and should
be off until the user turns it on.
