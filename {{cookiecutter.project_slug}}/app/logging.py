"""Canonical log line setup — one structured event per request.

This is the FLOOR. It gives you queryable JSON logs with request metadata
and (when OpenTelemetry is enabled) trace correlation. To get real debugging
power, enrich the request context with business fields (user_id, plan,
feature_flags, downstream timings) and emit them in this single line.

See https://loggingsucks.com/ for the wide-events philosophy.
"""

import logging
import logging.config

LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "rename_fields": {"asctime": "timestamp", "levelname": "level"},
            "reserved_attrs": ["color_message"],
        },
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        # Silence uvicorn's default access log — RequestLoggingMiddleware
        # emits the canonical line and we don't want duplicates.
        "uvicorn.access": {"handlers": [], "propagate": False, "level": "WARNING"},
        "uvicorn.error": {"handlers": ["stdout"], "propagate": False, "level": "INFO"},
    },
    "root": {"handlers": ["stdout"], "level": "INFO"},
}


def configure_logging() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
