# cookiecutter-fastapi

> A [Cookiecutter](https://cookiecutter.readthedocs.io/) template for production-ready FastAPI projects.

Optional features: Docker, PostgreSQL + SQLAlchemy + Alembic, OpenTelemetry, GitHub Actions CI.

## Quick-start

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (recommended) or `pip install cookiecutter`
- Docker + Docker Compose (if you select `use_docker=y`)

### Scaffold a project

```bash
uvx cookiecutter gh:cookiecutter/cookiecutter-fastapi
```

Answer the prompts, then:

```bash
cd <your-project-slug>

# With Docker (default):
docker compose -f docker-compose.local.yml up

# Without Docker:
uv sync
uv run uvicorn app.main:app --reload
```

Your API is now running at `http://localhost:8000`. Check the health endpoint:

```bash
curl http://localhost:8000/health
```

## Features

- **FastAPI app** with lifespan, pydantic-settings, structured JSON logging
- **Canonical log line floor** — one JSON event per request with trace correlation (method, path, status, duration, request_id)
- **Optional PostgreSQL** — SQLAlchemy 2.0 async + Alembic migrations, removed cleanly when not selected
- **Optional OpenTelemetry** — zero-code instrumentation via `opentelemetry-instrument` CLI (no SDK code in your app)
- **Optional Docker stack** — local dev with hot-reload + production multi-stage image
- **Optional GitHub Actions CI** — ruff lint + pytest + alembic check on pull requests
- **`uv.lock` committed** for reproducible installs (`uv sync --frozen` in CI)
- **Post-generation hooks** remove all unused feature files — scaffold stays clean

## Template variables

| Variable | Default | Options | Description |
|---|---|---|---|
| `project_name` | `My FastAPI Project` | any string | Human-readable project name |
| `project_slug` | *(auto)* | — | Python package name, auto-derived from `project_name` |
| `description` | `A production-ready FastAPI project` | any string | Short project description |
| `author_name` | `Your Name` | any string | Author's full name |
| `email` | *(auto)* | — | Author email, auto-derived from `author_name` |
| `version` | `0.1.0` | PEP 440 | Initial project version |
| `python_version` | `3.12` | `3.12`, `3.13` | Minimum Python version |
| `use_docker` | `y` | `y`, `n` | Include Docker + docker-compose stacks |
| `use_postgresql` | `n` | `n`, `y` | Include PostgreSQL + SQLAlchemy + Alembic |
| `postgresql_version` | `18` | `18`, `17`, `16` | PostgreSQL image version *(only used when `use_postgresql=y`)* |
| `use_opentelemetry` | `n` | `n`, `y` | Include OpenTelemetry tracing + structured logging |
| `ci_tool` | `GitHub` | `GitHub`, `None` | CI/CD platform (creates `.github/workflows/ci.yml`) |
| `open_source_license` | `MIT` | `MIT`, `BSD`, `GPLv3`, `Apache Software License 2.0`, `Not open source` | Project license |

## OpenTelemetry

When `use_opentelemetry=y`, the generated project uses **zero-code instrumentation** via the
`opentelemetry-instrument` CLI. No Python code is added to your app — the CLI wraps uvicorn
at startup and patches FastAPI, httpx, and SQLAlchemy automatically.

Configure via environment variables in `.env`:

```bash
OTEL_SERVICE_NAME=my-service
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
OTEL_SDK_DISABLED=false
```

The canonical log line (always-on) emits one JSON event per request including `trace_id` and
`span_id` when OpenTelemetry is active, so your logs and traces are correlated out of the box.

### ⚠️ Multi-worker production caveat

Running `opentelemetry-instrument uvicorn app.main:app --workers N` **only instruments worker 0**.
Uvicorn spawns workers via `os.fork()` but does not call a post-fork hook, so the OTel SDK
initialised in the parent is not re-initialised in child workers.

**Solution for multi-worker production:** Migrate from uvicorn to
[gunicorn with the uvicorn worker class](https://docs.gunicorn.org/en/stable/settings.html#worker-class)
and configure the OTel SDK in gunicorn's `post_fork` hook:

```python
# gunicorn.conf.py
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

def post_fork(server, worker):
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    # register provider ...
```

Single-worker deployments (the default Docker stack) are unaffected.

## Development

### Setup

```bash
git clone https://github.com/cookiecutter/cookiecutter-fastapi
cd cookiecutter-fastapi
uv sync
pre-commit install
```

### Run tests

```bash
# Render-matrix tests (fast — 24 combos × 9 assertions, ~9s):
uv run pytest tests/test_render_matrix.py -v

# Smoke tests (uv sync + ruff + pytest inside each rendered combo, ~12s):
uv run pytest tests/test_smoke.py -v

# Full suite with parallelization (-n auto):
uv run pytest
```

### Add or modify template variables

1. Edit `cookiecutter.json` (first value in each array = default).
2. Update `hooks/pre_gen_project.py` if the new variable needs validation.
3. Update `hooks/post_gen_project.py` if unused files need cleanup.
4. Add render assertions to `tests/test_render_matrix.py`.
5. Run the full test suite to verify all 24 matrix combos still pass.

## License

MIT License. See [LICENSE](LICENSE).
