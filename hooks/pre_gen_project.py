"""Pre-generation hook: validates cookiecutter variables before project creation."""
import sys

project_slug = "{{ cookiecutter.project_slug }}"


def validate_project_slug():
    if not project_slug.isidentifier():
        print(f"ERROR: '{project_slug}' is not a valid Python identifier.")
        sys.exit(1)


if __name__ == "__main__":
    validate_project_slug()
