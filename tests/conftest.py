"""Shared fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest
from fake_datawatch import make_certificate


@pytest.fixture(scope="session")
def certificate(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path, str]:
    return make_certificate(tmp_path_factory.mktemp("tls"), "server")
