"""Render-matrix tests: 24-combo parametrized presence/absence + content asserts.

Each test function consumes the `rendered` and `combo` fixtures from conftest.py,
which auto-parametrize over the full 24-combo MATRIX (see tests/matrix.py).

Total cases: 24 × (number of test functions in this file).
"""

from __future__ import annotations

from pathlib import Path

from tests.matrix import Combo


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _iter_rendered_files(root: Path):
    """Yield every file under the rendered project (skipping .venv if it somehow leaked)."""
    for p in root.rglob("*"):
        if p.is_file() and ".venv" not in p.parts:
            yield p


# -------------------- Always-on assertions --------------------


def test_always_on_core_files_exist(rendered, combo: Combo) -> None:
    root = Path(rendered.project_path)
    assert (root / "app" / "main.py").is_file(), f"{combo.id}: app/main.py missing"
    assert (root / "app" / "logging.py").is_file(), (
        f"{combo.id}: app/logging.py missing"
    )
    assert (root / "pyproject.toml").is_file(), f"{combo.id}: pyproject.toml missing"
    assert (root / ".env.example").is_file(), f"{combo.id}: .env.example missing"


def test_always_on_env_file_has_secret_key(rendered, combo: Combo) -> None:
    env_path = Path(rendered.project_path) / ".env"
    assert env_path.is_file(), f"{combo.id}: .env missing (generate_env_file)"
    content = _read(env_path)
    secret_lines = [
        line for line in content.splitlines() if line.startswith("SECRET_KEY=")
    ]
    assert len(secret_lines) == 1, (
        f"{combo.id}: expected exactly one SECRET_KEY= line, got {len(secret_lines)}"
    )
    value = secret_lines[0].split("=", 1)[1]
    assert len(value) >= 32, (
        f"{combo.id}: SECRET_KEY too short ({len(value)} chars) — expected token_urlsafe(50)"
    )


def test_always_on_gitignore_protects_env_and_allows_uv_lock(
    rendered, combo: Combo
) -> None:
    gi = Path(rendered.project_path) / ".gitignore"
    assert gi.is_file(), f"{combo.id}: .gitignore missing"
    content = _read(gi)
    assert ".env" in content, f"{combo.id}: .gitignore must list .env"
    assert "uv.lock" not in content, (
        f"{combo.id}: uv.lock must NOT be gitignored (committed for reproducibility)"
    )


def test_always_on_uv_lock_generated(rendered, combo: Combo) -> None:
    lock = Path(rendered.project_path) / "uv.lock"
    assert lock.is_file(), f"{combo.id}: uv.lock missing (generate_uv_lock)"
    assert lock.stat().st_size > 0, f"{combo.id}: uv.lock is empty"


def test_always_on_pyproject_has_python_json_logger(rendered, combo: Combo) -> None:
    pp = _read(Path(rendered.project_path) / "pyproject.toml")
    assert "python-json-logger" in pp, (
        f"{combo.id}: python-json-logger must be always-on dep"
    )


# -------------------- use_postgresql --------------------


def test_postgresql_assets(rendered, combo: Combo) -> None:
    root = Path(rendered.project_path)
    db_paths = [
        root / "app" / "database.py",
        root / "app" / "models" / "base.py",
        root / "app" / "models" / "__init__.py",
        root / "alembic.ini",
        root / "migrations" / "env.py",
    ]
    pyproject = _read(root / "pyproject.toml")
    env_example = _read(root / ".env.example")

    if combo.use_postgresql == "y":
        for p in db_paths:
            assert p.exists(), f"{combo.id}: {p.relative_to(root)} missing"
        assert "sqlalchemy" in pyproject, (
            f"{combo.id}: sqlalchemy must be in pyproject with use_postgresql=y"
        )
        assert "asyncpg" in pyproject, (
            f"{combo.id}: asyncpg must be in pyproject with use_postgresql=y"
        )
        assert "DATABASE_URL=" in env_example, (
            f"{combo.id}: .env.example must declare DATABASE_URL when use_postgresql=y"
        )
    else:
        for p in db_paths:
            assert not p.exists(), (
                f"{combo.id}: {p.relative_to(root)} must NOT exist when use_postgresql=n"
            )
        assert "sqlalchemy" not in pyproject.lower(), (
            f"{combo.id}: sqlalchemy leaked into pyproject with use_postgresql=n"
        )
        assert "DATABASE_URL" not in env_example, (
            f"{combo.id}: DATABASE_URL leaked into .env.example with use_postgresql=n"
        )


# -------------------- use_opentelemetry --------------------


def test_opentelemetry_assets(rendered, combo: Combo) -> None:
    root = Path(rendered.project_path)
    pyproject = _read(root / "pyproject.toml")
    env_example = _read(root / ".env.example")

    if combo.use_opentelemetry == "y":
        assert "opentelemetry-distro" in pyproject, (
            f"{combo.id}: opentelemetry-distro must be in pyproject"
        )
        assert "opentelemetry-exporter-otlp-proto-http" in pyproject, (
            f"{combo.id}: OTLP/http exporter must be in pyproject"
        )
        assert "OTEL_SERVICE_NAME=" in env_example, (
            f"{combo.id}: OTEL_SERVICE_NAME block missing from .env.example"
        )
        # Zero-code CLI reference in start scripts (docker pinned 'y' in matrix).
        start = _read(root / "compose" / "local" / "fastapi" / "start")
        assert "opentelemetry-instrument" in start, (
            f"{combo.id}: compose/local/fastapi/start must wrap uvicorn with "
            f"opentelemetry-instrument"
        )
    else:
        assert "opentelemetry" not in pyproject, (
            f"{combo.id}: opentelemetry leaked into pyproject with use_opentelemetry=n"
        )
        assert "OTEL_" not in env_example, (
            f"{combo.id}: OTEL_ block leaked into .env.example with use_opentelemetry=n"
        )


# -------------------- ci_tool --------------------


def test_ci_tool_assets(rendered, combo: Combo) -> None:
    root = Path(rendered.project_path)
    gh_dir = root / ".github"
    ci_yml = gh_dir / "workflows" / "ci.yml"
    if combo.ci_tool == "GitHub":
        assert ci_yml.is_file(), f"{combo.id}: .github/workflows/ci.yml missing"
    else:
        assert not gh_dir.exists(), (
            f"{combo.id}: .github/ must be removed when ci_tool=None"
        )


# -------------------- postgresql image presence --------------------


def test_postgresql_image_rendering(rendered, combo: Combo) -> None:
    """When use_postgresql=y, postgres:18 appears in docker-compose.
    When use_postgresql=n, no postgres image reference appears anywhere."""
    root = Path(rendered.project_path)
    token = "postgres:18"

    if combo.use_postgresql == "y":
        compose = _read(root / "docker-compose.local.yml")
        assert token in compose, (
            f"{combo.id}: docker-compose.local.yml must reference {token}"
        )
    else:
        for p in _iter_rendered_files(root):
            try:
                text = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            assert token not in text, (
                f"{combo.id}: {p.relative_to(root)} leaked '{token}' "
                f"despite use_postgresql=n"
            )
