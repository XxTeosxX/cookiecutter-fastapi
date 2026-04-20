from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.logging import configure_logging
from app.middlewares import request_logging_middleware
from app.routers import health

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="{{ cookiecutter.description }}",
    lifespan=lifespan,
)

app.middleware("http")(request_logging_middleware)
app.include_router(health.router)
