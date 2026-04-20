"""Smoke pipeline: uv sync + ruff check + pytest inside each rendered combo.

One test per smoke step, each auto-parametrized over 24 combos via the
`combo` / `rendered` fixtures. Subprocesses run inside the baked project
with hard timeouts.

Alembic smoke is intentionally NOT included — `alembic upgrade head` requires
a real PostgreSQL instance, which we don't provision in CI-light. Deferred to
a future integration tier (post-v0.1) if needed.

docker build / docker compose up are also out of scope (too heavy for pytest).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tests.matrix import Combo

SMOKE_TIMEOUT_SYNC = 180   # uv sync has a network cap; 180s handles cold caches
SMOKE_TIMEOUT_CHECK = 60
SMOKE_TIMEOUT_PYTEST = 120


def _run(cmd: list[str], cwd: Path, timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(  # noqa: S603 — fixed cmd list, no shell
        cmd,
        cwd=cwd,
        timeout=timeout,
        capture_output=True,
        text=True,
        check=False,
    )


def _sync(project_path: Path) -> None:
    r = _run(["uv", "sync"], project_path, SMOKE_TIMEOUT_SYNC)
    assert r.returncode == 0, (
        f"uv sync failed in {project_path}:\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    )


@pytest.mark.smoke
def test_generated_project_syncs(rendered, combo: Combo) -> None:
    _sync(Path(rendered.project_path))


@pytest.mark.smoke
def test_generated_project_ruff_clean(rendered, combo: Combo) -> None:
    project_path = Path(rendered.project_path)
    _sync(project_path)
    r = _run(
        ["uv", "run", "ruff", "check", "."], project_path, SMOKE_TIMEOUT_CHECK
    )
    assert r.returncode == 0, (
        f"ruff check failed for {combo.id}:\n"
        f"STDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    )


@pytest.mark.smoke
def test_generated_project_tests_pass(rendered, combo: Combo) -> None:
    project_path = Path(rendered.project_path)
    _sync(project_path)
    r = _run(["uv", "run", "pytest"], project_path, SMOKE_TIMEOUT_PYTEST)
    assert r.returncode == 0, (
        f"pytest failed for {combo.id}:\n"
        f"STDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    )


@pytest.mark.smoke
def test_generated_project_without_docker_renders_and_syncs(cookies) -> None:
    """Docker='n' case (outside the matrix, which pins use_docker='y').

    Confirms a minimal no-docker scaffold renders correctly and syncs.
    """
    result = cookies.bake(
        extra_context={
            "use_postgresql": "n",
            "use_docker": "n",
            "use_opentelemetry": "n",
            "ci_tool": "None",
        }
    )
    assert result.exit_code == 0, f"bake failed: {result.exception}"
    project_path = Path(result.project_path)
    assert not (project_path / "compose").exists(), "compose/ leaked with docker=n"
    assert not (project_path / "docker-compose.local.yml").exists(), (
        "docker-compose.local.yml leaked with docker=n"
    )
    _sync(project_path)
