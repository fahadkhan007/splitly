from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


# Sync engine — used by Alembic migrations
sync_engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)

# Async engine — used by FastAPI at runtime
async_engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=settings.DEBUG)

# Session factories
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


# FastAPI dependency — yields an async DB session per request
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
