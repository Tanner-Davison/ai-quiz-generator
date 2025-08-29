from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .config import settings
import os

# Convert DATABASE_URL to async format if needed
def get_async_database_url():
    """Convert sync DATABASE_URL to async format"""
    db_url = settings.DATABASE_URL
    if db_url.startswith('postgresql://'):
        # Convert to async format
        return db_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
    return db_url

def get_sync_database_url():
    """Get sync DATABASE_URL"""
    db_url = settings.DATABASE_URL
    if db_url.startswith('postgresql+asyncpg://'):
        # Convert back to sync format
        return db_url.replace('postgresql+asyncpg://', 'postgresql://', 1)
    return db_url

# Create async engine for async operations
async_engine = create_async_engine(
    get_async_database_url(),
    echo=False,  # Set to False in production
    future=True
)

# Create sync engine for migrations and sync operations
sync_engine = create_engine(
    get_sync_database_url(),
    echo=False,  # Set to False in production
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create sync session factory
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

# Base class for models
Base = declarative_base()

# Dependency to get async database session
async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Dependency to get sync database session
def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database (create tables)
async def init_db():
    async with async_engine.begin() as conn:
        # Import all database models here to ensure they are registered with Base
        from .models.database_models import Quiz, QuizQuestion, QuizSubmission, QuizAnswer, ChatSession, ChatMessage
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

# Close database connections
async def close_db():
    await async_engine.dispose()
