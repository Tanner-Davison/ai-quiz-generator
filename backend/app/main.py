"""Main application module for AI Quiz Generator."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import close_db, init_db
from app.middleware.cors import add_cors_middleware
from app.middleware.logging import add_logging_middleware
from app.routes import health, quiz

# Configure logging based on environment
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Manage application lifespan events"""
    logger.info("Starting up in %s mode", settings.ENVIRONMENT)
    logger.info("Debug mode: %s", settings.DEBUG)
    logger.info("Port: %s", settings.PORT)
    logger.info("Database URL: %s", "***" if settings.DATABASE_URL else "None")

    if settings.SKIP_DB_INIT:
        logger.info("Skipping database initialization (SKIP_DB_INIT=true)")
    else:
        try:
            # Only initialize database if DATABASE_URL is set and not the default
            if settings.DATABASE_URL and not settings.DATABASE_URL.endswith("quiz_db"):
                await init_db()
                logger.info("Database initialized successfully")
            else:
                logger.warning(
                    "No production database configured - skipping database initialization"
                )
                if settings.ENVIRONMENT == "development":
                    logger.info(
                        "In development mode - you can set DATABASE_URL to connect to a local database"
                    )
        except Exception as e:
            logger.error("Database initialization failed: %s", e)
            if settings.ENVIRONMENT == "production":
                logger.error(
                    "Database initialization failed in production - app may not function properly"
                )
            else:
                logger.info(
                    "App will start without database functionality in development mode"
                )

    yield

    # Shutdown
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error("Error closing database connections: %s", e)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="AI Quiz Generator",
        version="1.0.0",
        description="An AI-powered quiz generation service using Groq",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # middleware
    add_cors_middleware(app)
    add_logging_middleware(app)

    # routers
    app.include_router(health.router, tags=["Health"])
    app.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting server with settings: %s", settings)

    # Use environment variables for host and port
    port = settings.PORT
    host = settings.HOST

    logger.info("AI Quiz Generator server running at http://%s:%s", host, port)
    logger.info("API Documentation: http://%s:%s/docs", host, port)

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG,
    )
