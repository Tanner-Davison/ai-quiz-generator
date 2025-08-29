from fastapi import FastAPI
from .middleware.cors import add_cors_middleware
from .middleware.logging import add_logging_middleware
from .routes import quiz, health
from .config import settings
from .database import init_db, close_db

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="AI Quiz Generator",
        version="1.0.0",
        description="An AI-powered quiz generation service using Groq"
    )
    
    # middleware
    add_cors_middleware(app)
    add_logging_middleware(app)
    
    # routers
    app.include_router(health.router, tags=["Health"])
    app.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])
    
    # Database lifecycle events
    @app.on_event("startup")
    async def startup_event():
        """Initialize database on startup"""
        await init_db()
        print("✅ Database initialized successfully")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Close database connections on shutdown"""
        await close_db()
        print("🔌 Database connections closed")
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    port = settings.PORT
    print(f"🚀 AI Quiz Generator server running at http://localhost:{port}")
    print(f" API Documentation: http://localhost:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port)
