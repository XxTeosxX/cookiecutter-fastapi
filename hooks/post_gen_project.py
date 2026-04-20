"""Post-generation hook: removes files for unselected optional features."""

import os
import secrets
import shutil
import subprocess

# Feature flags from cookiecutter context
USE_DOCKER = "{{ cookiecutter.use_docker }}" == "y"
USE_POSTGRESQL = "{{ cookiecutter.use_postgresql }}" == "y"
USE_OPENTELEMETRY = "{{ cookiecutter.use_opentelemetry }}" == "y"
CI_TOOL = "{{ cookiecutter.ci_tool }}"


def remove_path(path: str) -> None:
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)


def cleanup_docker() -> None:
    """Remove Docker-related files when use_docker == 'n'."""
    remove_path("compose")
    remove_path("docker-compose.local.yml")
    remove_path("docker-compose.production.yml")
    remove_path(".dockerignore")
    remove_path(".python-version")


def cleanup_postgresql_docker_assets() -> None:
    """Remove Postgres-only Docker assets when use_postgresql == 'n' but use_docker == 'y'."""
    remove_path(os.path.join("compose", "local", "fastapi", "entrypoint"))
    remove_path(os.path.join("compose", "production", "fastapi", "entrypoint"))
    remove_path(os.path.join("compose", "production", "postgres"))


def cleanup_postgresql_app_assets() -> None:
    """Remove PostgreSQL app-layer assets when use_postgresql == 'n'."""
    remove_path(os.path.join("app", "database.py"))
    remove_path(os.path.join("app", "models"))
    remove_path("migrations")
    remove_path("alembic.ini")


def cleanup_ci_tool() -> None:
    """Remove .github/ when ci_tool != 'GitHub'."""
    remove_path(".github")


def generate_env_file() -> None:
    """Generate .env with a fresh SECRET_KEY.

    .env is gitignored (see .gitignore). Users add a SECRET_KEY field to
    app/config.py when they need it (JWT signing, session cookies, etc.).
    Convention mirrors cookiecutter-django's SECRET_KEY generation.
    """
    with open(".env", "w", encoding="utf-8") as f:
        f.write(f"SECRET_KEY={secrets.token_urlsafe(50)}\n")


def generate_uv_lock() -> None:
    """Generate uv.lock reflecting selected Jinja-conditional dependencies.

    Template pyproject.toml is Jinja-conditional (asyncpg, alembic, aiosqlite
    appear only when use_postgresql='y'), so a pre-committed lockfile would
    mismatch. Generate it at scaffold time instead.
    """
    try:
        subprocess.run(
            ["uv", "lock"],
            check=True,
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise SystemExit(
            "ERROR: 'uv' not found on PATH. Install uv before generating a project "
            "(https://docs.astral.sh/uv/getting-started/installation/)."
        )
    except subprocess.CalledProcessError as e:
        raise SystemExit(
            f"ERROR: 'uv lock' failed with exit {e.returncode}:\n{e.stderr}"
        )


if __name__ == "__main__":
    if not USE_DOCKER:
        cleanup_docker()
    elif not USE_POSTGRESQL:
        cleanup_postgresql_docker_assets()

    if not USE_POSTGRESQL:
        cleanup_postgresql_app_assets()

    if CI_TOOL != "GitHub":
        cleanup_ci_tool()

    generate_env_file()
    generate_uv_lock()
