"""Pre-generation hook: validates cookiecutter variables before project creation.

Validates free-text strings (project_slug, version), boolean y/n inputs,
and cross-variable combinations.
"""

import re
import sys

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+([.-][a-zA-Z0-9.]+)?$")

project_slug = "{{ cookiecutter.project_slug }}"
version = "{{ cookiecutter.version }}"
use_postgresql = "{{ cookiecutter.use_postgresql }}"
use_docker = "{{ cookiecutter.use_docker }}"
use_opentelemetry = "{{ cookiecutter.use_opentelemetry }}"


def validate_project_slug():
    if not project_slug.isidentifier():
        print(f"ERROR: '{project_slug}' is not a valid Python identifier.")
        sys.exit(1)


def validate_version():
    if not VERSION_RE.match(version):
        print(
            f"ERROR: 'version' must follow PEP 440 basic format "
            f"(examples: '1.0.0', '0.1.0-alpha', '2.0.0.dev1', '1.0.0-rc.1'), "
            f"got '{version}'."
        )
        sys.exit(1)


def validate_yn_flags():
    for name, value in [
        ("use_docker", use_docker),
        ("use_postgresql", use_postgresql),
        ("use_opentelemetry", use_opentelemetry),
    ]:
        if value not in ("y", "n"):
            print(f"ERROR: '{name}' must be 'y' or 'n', got '{value}'.")
            sys.exit(1)


def warn_postgres_without_docker():
    if use_postgresql == "y" and use_docker == "n":
        print(
            "WARNING: use_postgresql='y' with use_docker='n'. "
            "docker-compose.local.yml will not be generated — you must provision "
            "PostgreSQL yourself (managed service like Supabase/RDS, local install, "
            "or a separate container).",
            file=sys.stderr,
        )


if __name__ == "__main__":
    validate_project_slug()
    validate_version()
    validate_yn_flags()
    warn_postgres_without_docker()
