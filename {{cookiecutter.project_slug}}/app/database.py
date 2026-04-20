from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

# Fallback to in-memory SQLite when DATABASE_URL is not configured.
# SQLAlchemy validates the URL at engine construction, so an empty string
# raises ArgumentError at import. aiosqlite is already a dev dependency and
# lets smoke tests run without a running Postgres.
_DATABASE_URL = settings.DATABASE_URL or "sqlite+aiosqlite:///:memory:"

engine: AsyncEngine = create_async_engine(
    _DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
