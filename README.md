# datawatch for Home Assistant

A Home Assistant integration for [datawatch](https://github.com/dmz006/datawatch), installable
through HACS.

> **In development. Nothing is usable yet.** There is no release, and installing it now does
> nothing.

## First goal

Hands-free, eyes-free use of datawatch by voice:

- ask for status
- list projects, and set or clear a focus so later questions do not need a name

This first step only reads from datawatch. The datawatch server will be entered in the
integration's setup screens; no server is built in.

## Development

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[test,lint]"
.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy
.venv/bin/pytest --cov
```

### Before you commit or push

This repository is public. Enable the hooks once per clone:

```bash
git config core.hooksPath .githooks
```

The hooks need [gitleaks](https://github.com/gitleaks/gitleaks) and a private deny list at
`~/.config/datawatch-hacs/leak-denylist.txt` (or `LEAK_DENYLIST=/path`): one term per line,
such as your own host names, addresses and device names. Keep that file out of the
repository. The hooks refuse to run without it.

Use made-up data in code, tests and documentation. Automated checks can miss things, so read
what you are about to publish.

## License

[PolyForm Noncommercial 1.0.0](LICENSE).
