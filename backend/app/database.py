from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .config import settings

# Create async engine for async operations
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Set to False in production
    future=True
)

# Create sync engine for migrations and sync operations
sync_engine = create_engine(
    settings.DATABASE_SYNC_URL,
    echo=True,  # Set to False in production
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
