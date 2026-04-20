import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.config import settings
from app.logging import configure_logging
from app.routers import health

configure_logging()
logger = logging.getLogger("app.request")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="{{ cookiecutter.description }}",
    lifespan=lifespan,
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)

    extra = {
        "event": "request",
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": duration_ms,
        "request_id": request_id,
    }

    try:
        from opentelemetry.trace import get_current_span

        span_context = get_current_span().get_span_context()
        if span_context.is_valid:
            extra["trace_id"] = format(span_context.trace_id, "032x")
            extra["span_id"] = format(span_context.span_id, "016x")
    except ImportError:
        pass

    response.headers["x-request-id"] = request_id
    logger.info("request", extra=extra)
    return response


app.include_router(health.router)
