"""The integration's metadata is consistent and the versions move together."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from custom_components.datawatch.const import DOMAIN

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "custom_components" / "datawatch" / "manifest.json").read_text())


def test_domain_matches_folder_and_manifest() -> None:
    assert DOMAIN == "datawatch" == MANIFEST["domain"]


def test_manifest_has_what_hacs_needs() -> None:
    for key in ("documentation", "issue_tracker", "codeowners", "name", "version"):
        assert MANIFEST[key], key


def test_versions_are_in_lockstep() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    changelog = (ROOT / "CHANGELOG.md").read_text()
    newest = re.search(r"^## (\d+\.\d+\.\d+)", changelog, re.M)
    assert newest
    assert MANIFEST["version"] == project["version"] == newest.group(1)


def test_hacs_file_names_the_integration() -> None:
    hacs = json.loads((ROOT / "hacs.json").read_text())
    assert hacs["name"] == "datawatch"
    assert hacs["content_in_root"] is False


def test_license_matches_datawatch_terms() -> None:
    assert (ROOT / "LICENSE").read_text().startswith("Polyform Noncommercial License 1.0.0")
