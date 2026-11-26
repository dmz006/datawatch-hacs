"""Print what the voice parts of the installed Home Assistant need, for the tests.

Home Assistant installs these itself when it runs. The versions come from the installed
Home Assistant, so tests always match whichever release they run against.
"""

from __future__ import annotations

import json
from importlib.util import find_spec
from pathlib import Path

NEEDED = ("assist_satellite", "conversation")


def main() -> None:
    spec = find_spec("homeassistant")
    assert spec and spec.origin
    components = Path(spec.origin).parent / "components"
    seen: set[str] = set()
    requirements: set[str] = set()
    pending = list(NEEDED)
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        manifest = json.loads((components / name / "manifest.json").read_text())
        requirements.update(manifest.get("requirements", []))
        pending.extend(manifest.get("dependencies", []))
    print("\n".join(sorted(requirements)))


if __name__ == "__main__":
    main()
