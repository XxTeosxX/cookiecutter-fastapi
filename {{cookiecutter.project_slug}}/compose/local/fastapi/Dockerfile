FROM ghcr.io/astral-sh/uv:python{{ cookiecutter.python_version }}-trixie

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

ARG APP_HOME=/app
WORKDIR ${APP_HOME}

{%- if cookiecutter.use_postgresql == 'y' %}
# Runtime deps: wait-for-it for entrypoint orchestration.
# asyncpg does NOT need libpq-dev (pure-python binding).
RUN apt-get update && apt-get install --no-install-recommends -y \
      wait-for-it \
    && rm -rf /var/lib/apt/lists/*
{%- endif %}

# Install project dependencies (cached across rebuilds)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project

{%- if cookiecutter.use_postgresql == 'y' %}
COPY ./compose/local/fastapi/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint && chmod +x /entrypoint
{%- endif %}

COPY ./compose/local/fastapi/start /start
RUN sed -i 's/\r$//g' /start && chmod +x /start

ENV PATH="/opt/venv/bin:$PATH"

{%- if cookiecutter.use_postgresql == 'y' %}
ENTRYPOINT ["/entrypoint"]
{%- endif %}
