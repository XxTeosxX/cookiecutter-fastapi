import os

# Disable OpenTelemetry SDK in tests — prevents network calls to OTLP collector
# and silences exporter warnings. Safe even when OTel is not installed
# (env var is a no-op without the SDK present).
os.environ.setdefault("OTEL_SDK_DISABLED", "true")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
