"""Post-generation hook: removes files for unselected optional features."""
import os
import shutil

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


if __name__ == "__main__":
    # Feature removal will be implemented in Phase 6
    pass
