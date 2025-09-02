import os

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings


def get_async_database_url():
    """Convert sync DATABASE_URL to async format"""
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return db_url


def get_sync_database_url():
    """Get sync DATABASE_URL"""
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql+asyncpg://"):
        return db_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return db_url


async_engine = create_async_engine(get_async_database_url(), echo=False, future=True)

sync_engine = create_engine(
    get_sync_database_url(),
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()


async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    async with async_engine.begin() as conn:
        from .models.database_models import Quiz, QuizQuestion, QuizSubmission

        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    await async_engine.dispose()
