"""Tests for the pre-publish leak checker.

Sample "private" values are assembled at run time so this file stays clean when the
checker scans the repository itself. All of them are made up.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import check_leaks
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_leaks.py"


def ip(*parts: int) -> str:
    return ".".join(str(p) for p in parts)


MAC = ":".join(["aa", "bb", "cc", "dd", "ee", "ff"])
EMAIL = "someone" + "@" + "mail.invalid-domain.io"


@pytest.mark.parametrize(
    ("kind", "sample"),
    [
        ("private-ipv4", "url = http://" + ip(192, 168, 7, 9) + ":8443"),
        ("private-ipv4", "host " + ip(10, 1, 2, 3)),
        ("private-ipv4", "host " + ip(172, 20, 0, 4)),
        ("private-ipv4", "tailnet " + ip(100, 101, 5, 6)),
        ("private-ipv6", "addr " + "fe80" + "::1a2b:3c4d"),
        ("mac-address", "mac " + MAC),
        ("email", "mail " + EMAIL),
        ("home-path", "see /ho" + "me/alice/project"),
        ("tailnet-name", "host box.tail1234" + ".ts.net"),
        ("private-key", "-----BEGIN " + "OPENSSH PRIVATE KEY-----"),
        ("github-token", "gh" + "p_" + "a1" * 18),
        ("bearer-token", "Authorization: Bear" + "er " + "abc123DEF456ghi789"),
        ("base64-key", "key " + "Qm9" * 14 + "x="),
        ("secret-assignment", "pass" + 'word = "hunter2hunter2"'),
    ],
)
def test_generic_patterns_are_found(kind: str, sample: str) -> None:
    findings = check_leaks.scan_text(sample, denylist=[])
    assert kind in {f.kind for f in findings}


@pytest.mark.parametrize(
    "sample",
    [
        "server 192.0.2.10 and 198.51.100.7 and 203.0.113.5",
        "listen on 127.0.0.1 or 0.0.0.0",
        "version 2026.11.1",
        "git@github.com:owner/repo.git",
        "committer GitHub <noreply@github.com>",
        "user@example.com and 12345+someone@users.noreply.github.com",
        "Co-Authored-By: Someone <noreply@anthropic.com>",
        'token = "fake-token-value"',
        'password: "<your password>"',
    ],
)
def test_safe_examples_are_allowed(sample: str) -> None:
    assert check_leaks.scan_text(sample, denylist=[]) == []


def test_denylist_is_case_insensitive_and_does_not_echo_the_term() -> None:
    findings = check_leaks.scan_text("connect to MyBoxName now", denylist=["myboxname"])
    assert [f.kind for f in findings] == ["denylist"]
    assert "myboxname" not in str(findings).lower()


def test_findings_never_contain_the_full_value() -> None:
    token = "gh" + "p_" + "z9" * 18
    findings = check_leaks.scan_text(token, denylist=[])
    assert findings
    assert token not in str(findings)


def test_line_numbers_are_reported() -> None:
    findings = check_leaks.scan_text("ok\nok\n" + MAC, denylist=[])
    assert findings[0].line == 3


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.name", "Tester")
    git(tmp_path, "config", "user.email", "1+tester@users.noreply.github.com")
    git(tmp_path, "config", "core.hooksPath", "no-hooks")
    return tmp_path


def run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], cwd=repo, capture_output=True, text=True, check=False
    )


def commit(repo: Path, name: str, content: str, message: str = "chore: change") -> None:
    (repo / name).write_text(content)
    git(repo, "add", name)
    git(repo, "commit", "-q", "-m", message)


def test_missing_denylist_fails_closed(repo: Path) -> None:
    result = run(repo, "--denylist", str(repo / "absent.txt"), "tree")
    assert result.returncode == 2


def test_empty_denylist_fails_closed(repo: Path, tmp_path_factory: pytest.TempPathFactory) -> None:
    empty = tmp_path_factory.mktemp("deny") / "deny.txt"
    empty.write_text("# nothing yet\n")
    assert run(repo, "--denylist", str(empty), "tree").returncode == 2


def test_tree_scans_staged_content(repo: Path) -> None:
    (repo / "a.txt").write_text("host " + ip(10, 9, 8, 7))
    git(repo, "add", "a.txt")
    (repo / "a.txt").write_text("clean now, but the staged copy is not")
    result = run(repo, "--no-denylist", "tree")
    assert result.returncode == 1
    assert "a.txt" in result.stdout


def test_tree_scans_file_names(repo: Path) -> None:
    commit(repo, "notes-myboxname.txt", "clean")
    deny = repo.parent / (repo.name + "-deny.txt")
    deny.write_text("myboxname\n")
    assert run(repo, "--denylist", str(deny), "tree").returncode == 1


def test_history_finds_a_leak_removed_later(repo: Path) -> None:
    commit(repo, "a.txt", "mac " + MAC)
    commit(repo, "a.txt", "removed")
    assert run(repo, "--no-denylist", "tree").returncode == 0
    assert run(repo, "--no-denylist", "history").returncode == 1


def test_history_checks_commit_messages_and_author_email(repo: Path) -> None:
    commit(repo, "a.txt", "clean", message="fix: talk to " + ip(192, 168, 3, 4))
    assert run(repo, "--no-denylist", "history").returncode == 1


def test_history_rejects_a_regular_author_email(repo: Path) -> None:
    git(repo, "config", "user.email", EMAIL)
    commit(repo, "a.txt", "clean")
    assert run(repo, "--no-denylist", "history").returncode == 1


def test_clean_repository_passes(repo: Path) -> None:
    commit(repo, "a.txt", "nothing private here")
    assert run(repo, "--no-denylist", "tree").returncode == 0
    assert run(repo, "--no-denylist", "history").returncode == 0


def test_message_mode(repo: Path) -> None:
    message = repo / "MSG"
    message.write_text("feat: use /ho" + "me/alice/file")
    assert run(repo, "--no-denylist", "message", str(message)).returncode == 1
