#!/usr/bin/env python3
"""Stop private details from reaching this public repository.

Checks for generic leak patterns (private addresses, hardware addresses, emails, home
folder paths, keys and tokens) plus a private deny list of this installation's own names.
The deny list lives outside the repository and is never printed.

Modes:
  tree          everything staged or committed in the index, including file names
  history       every commit: author, committer, message and patch, on all refs
  message FILE  one commit message

Exit status: 0 clean, 1 something found, 2 the check could not run.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DENYLIST = Path.home() / ".config" / "datawatch-hacs" / "leak-denylist.txt"

_OCTET = r"(?:25[0-5]|2[0-4]\d|1?\d?\d)"
_PRIVATE_IPV4 = (
    rf"(?<![\d.])(?:10\.{_OCTET}|192\.168|172\.(?:1[6-9]|2\d|3[01])|169\.254"
    rf"|100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7]))\.{_OCTET}\.{_OCTET}(?![\d.]\d)"
)

PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private-ipv4", re.compile(_PRIVATE_IPV4)),
    (
        "private-ipv6",
        re.compile(r"(?<![\w:])(?:fe80|f[cd][0-9a-f]{2}):[0-9a-f]{0,4}:[0-9a-f:]*", re.I),
    ),
    ("mac-address", re.compile(r"(?<![\w:-])(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}(?![\w:-])", re.I)),
    ("email", re.compile(r"[A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("home-path", re.compile(r"/(?:home|Users)/(?!runner\b|user\b|example\b)[A-Za-z0-9._-]+")),
    ("tailnet-name", re.compile(r"[a-z0-9-]+\.ts\.net\b", re.I)),
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("github-token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}")),
    ("bearer-token", re.compile(r"[Bb]earer\s+(?=[A-Za-z0-9._~+/-]*\d)[A-Za-z0-9._~+/-]{16,}")),
    ("base64-key", re.compile(r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{43}=(?![A-Za-z0-9+/=])")),
    (
        "secret-assignment",
        re.compile(
            r"""(?:password|passwd|token|api_?key|secret|psk)["']?\s*[:=]\s*"""
            r"""["'](?!fake|example|<)[^"'\s]{8,}["']""",
            re.I,
        ),
    ),
)

_ALLOWED_EMAIL = re.compile(
    r"(?:@users\.noreply\.github\.com|@example\.(?:com|org|net))$"
    r"|^(?:noreply@anthropic\.com|noreply@github\.com|git@github\.com)$",
    re.I,
)


@dataclass(frozen=True)
class Finding:
    """One suspected leak. Holds only a masked form of what matched."""

    kind: str
    line: int
    masked: str


def scan_text(text: str, denylist: Sequence[str]) -> list[Finding]:
    """Return every suspected leak in text."""
    findings: list[Finding] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for kind, pattern in PATTERNS:
            for match in pattern.finditer(line):
                value = match.group(0)
                if kind == "email" and _ALLOWED_EMAIL.search(value):
                    continue
                findings.append(Finding(kind, number, value[:3] + "..."))
        lowered = line.lower()
        for index, term in enumerate(denylist, start=1):
            if term.lower() in lowered:
                findings.append(Finding("denylist", number, f"private term #{index}"))
    return findings


def load_denylist(path: Path) -> list[str]:
    """Read the private deny list: one term per line, # starts a comment."""
    if not path.is_file():
        raise SystemExit(_cannot_run(f"private deny list not found: {path}"))
    terms = [
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not terms:
        raise SystemExit(_cannot_run("private deny list is empty"))
    return terms


def _cannot_run(reason: str) -> int:
    print(f"leak check could not run: {reason}", file=sys.stderr)
    return 2


def _git(*args: str) -> bytes:
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout


def _tree_sources() -> list[tuple[str, str]]:
    names = [n for n in _git("ls-files", "-z", "--cached").decode().split("\0") if n]
    sources = [("file names", "\n".join(names))]
    for name in names:
        sources.append((name, _git("show", f":{name}").decode("utf-8", errors="replace")))
    return sources


def _history_sources() -> list[tuple[str, str]]:
    log = _git(
        "log",
        "--all",
        "--patch",
        "--no-color",
        "--no-ext-diff",
        "--no-textconv",
        "--decorate=full",
        "--format=commit %H %D%nauthor %an <%ae>%ncommitter %cn <%ce>%n%B",
    )
    tags = _git("for-each-ref", "--format=%(refname) %(taggeremail) %(contents)", "refs/tags")
    return [
        ("git history", log.decode("utf-8", errors="replace")),
        ("tags", tags.decode("utf-8", errors="replace")),
    ]


def main(argv: Sequence[str] | None = None) -> int:
    """Run one check and report findings."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument(
        "--denylist", type=Path, default=Path(os.environ.get("LEAK_DENYLIST", DEFAULT_DENYLIST))
    )
    parser.add_argument(
        "--no-denylist", action="store_true", help="generic patterns only (for public CI)"
    )
    parser.add_argument("mode", choices=("tree", "history", "message"))
    parser.add_argument("file", nargs="?", type=Path)
    options = parser.parse_args(argv)

    denylist = [] if options.no_denylist else load_denylist(options.denylist)
    try:
        if options.mode == "tree":
            sources = _tree_sources()
        elif options.mode == "history":
            sources = _history_sources()
        elif options.file is None:
            return _cannot_run("message mode needs a file")
        else:
            sources = [("commit message", options.file.read_text())]
    except (OSError, subprocess.CalledProcessError) as error:
        return _cannot_run(str(error))

    total = 0
    for label, text in sources:
        for finding in scan_text(text, denylist):
            total += 1
            print(f"{label}:{finding.line}: {finding.kind} ({finding.masked})")
    if total:
        print(f"leak check FAILED: {total} suspected leak(s)")
        return 1
    print(f"leak check passed ({options.mode}, {len(denylist)} private terms)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
