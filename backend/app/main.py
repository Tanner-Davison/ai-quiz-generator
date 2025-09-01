from contextlib import asynccontextmanager
from fastapi import FastAPI
from .middleware.cors import add_cors_middleware
from .middleware.logging import add_logging_middleware
from .routes import quiz, health
from .config import settings
from .database import init_db, close_db
import os
import logging

# Configure logging based on environment
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    logger.info(f"Starting up in {settings.ENVIRONMENT} mode")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Port: {settings.PORT}")
    logger.info(f"Database URL: {'***' if settings.DATABASE_URL else 'None'}")
    
    if settings.SKIP_DB_INIT:
        logger.info("Skipping database initialization (SKIP_DB_INIT=true)")
    else:
        try:
            # Only initialize database if DATABASE_URL is set and not the default
            if settings.DATABASE_URL and not settings.DATABASE_URL.endswith("quiz_db"):
                await init_db()
                logger.info("Database initialized successfully")
            else:
                logger.warning("No production database configured - skipping database initialization")
                if settings.ENVIRONMENT == "development":
                    logger.info("In development mode - you can set DATABASE_URL to connect to a local database")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            if settings.ENVIRONMENT == "production":
                logger.error("Database initialization failed in production - app may not function properly")
            else:
                logger.info("App will start without database functionality in development mode")
    
    yield
    
    # Shutdown
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="AI Quiz Generator",
        version="1.0.0",
        description="An AI-powered quiz generation service using Groq",
        debug=settings.DEBUG,
        lifespan=lifespan
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
    logger.info(f"Starting server with settings: {settings}")
    
    # Use environment variables for host and port
    port = settings.PORT
    host = settings.HOST
    
    logger.info(f"AI Quiz Generator server running at http://{host}:{port}")
    logger.info(f"API Documentation: http://{host}:{port}/docs")
    
    uvicorn.run(
        "app.main:app", 
        host=host, 
        port=port,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG
    )
