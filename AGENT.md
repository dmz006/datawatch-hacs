# Agent rules

Rules for any AI agent or person working on this repository. Read [CONTEXT.md](CONTEXT.md)
too.

## 1. Before changing files
Check these rules. If a rule conflicts with a task, stop and ask the maintainer.

## 2. Decisions
The maintainer makes the decisions. When one comes up, stop and give the options, a
recommendation and why.

## 3. Safety
- Install on a Home Assistant server only the way a user would: through the Marketplace and
  the setup screens. Never copy files onto a server by hand.
- Never stop or restart a running Home Assistant without the maintainer's approval.
- Do not build or run tests on a Home Assistant server.
- Tests never talk to a live datawatch. Checks against a real one are read-only unless the
  maintainer approves a write.
- Do not disturb other sessions working on the same machine.

- The integration may change one thing: answering a question after the user says "confirm
  answer". Keep that confirmation in the integration's own code, never in an AI tool. Any
  other change to datawatch needs the maintainer's approval.
- Only add to a user's AI assistant. Never edit its instructions or settings.

## 4. Public repository: nothing private, ever
- No host names, IP or MAC addresses, network names, configuration, secrets, tokens, real
  device, entity, project or session names, or local paths: in code, tests, docs, commit
  messages, tags, issues or releases.
- Made-up data only. A datawatch server is always a user setting, never hard-coded.
- Do not publish details of anyone's own installation.
- Never use `--no-verify`. The leak check and gitleaks must pass before a push, and read the
  diff. If anything looks private, do not push.
- Commit with a GitHub no-reply address.

## 5. Code quality
- Python is typed; `mypy` (strict), `ruff check` and `ruff format --check` pass.
- Shell scripts use `set -euo pipefail`. Some agent shells ignore `set -e` for typed
  commands, so put a test-then-commit sequence in a script file.
- No TODOs on `main`: open an issue and refer to it.
- Keep every use of non-public Home Assistant code in `entry_phrase.py`.

## 6. Testing
- Write the failing test first.
- Use `tests/ha_harness.py` for Home Assistant behaviour and `tests/fake_datawatch.py` for
  datawatch. Prefer real Home Assistant code over mocks.
- Coverage at least 95%.
- Say plainly what has not been tested.

## 7. Git
- Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`, `ci:`).
- One logical change per commit.
- Never force-push `main`. Never squash without the maintainer's agreement.
- Tags are `vX.Y.Z`. Never move or reuse a released tag.

## 8. Versions and releases
- Semantic versioning, kept the same in `manifest.json`, `pyproject.toml` and
  `CHANGELOG.md`.
- Patch: docs, tests, fixes. Minor: new voice command, action or setting. Major: a breaking
  change to setup, actions or commands.
- **Every release ships with up-to-date documentation.** Before asking to publish, check
  each of these against the code being released and fix what is out of date:
  - `README.md`: what it can do, setup, voice commands, privacy and limits.
  - `docs/how-it-works.md`: text, diagrams and the list of datawatch calls.
  - `docs/troubleshooting.md` and `docs/assistant-context.md`.
  - `SECURITY.md` and `CONTEXT.md`.
  - `CHANGELOG.md`: move "Unreleased" under the new version and its date.
- When asking to publish, say which documents changed and which were checked and left as
  they are. Check that changed diagrams display. Home Assistant's Marketplace page shows
  the README but does not draw Mermaid diagrams.
- Ask the maintainer before publishing a release.

## 9. Dependencies
- Runtime dependencies go in `manifest.json` and `pyproject.toml`, with the reason in the
  commit message. Their licences must suit this project's licence.
- Support Home Assistant 2026.11 and later only.

## 10. Documentation
- Write for people, in plain words.
- Every voice command and setting is documented in `README.md`, and where Home Assistant
  shows text, in `translations/en.json`.
- Screen text is translated into every language datawatch has (en, de, es, fr, ja): change
  all five together. Use datawatch's words, including for Automaton and Automation. Keep
  spoken commands in English while voice is English only. The cards' words are in the
  `TEXT` table in `frontend/datawatch-cards.js`, never in the drawing code.
- Words listened for belong in a language's file in `voice/lang/`, never in `phrases.py`.
- Keep the diagrams in `docs/how-it-works.md` matching the code.
- All settings are in Home Assistant's setup screens; no YAML-only options.

## 11. Scope and interruptions
- If a request grows the scope, say what it adds and ask first.
- Leave the tree clean, or commit unfinished work on a `wip/<topic>` branch naming the next
  step.
