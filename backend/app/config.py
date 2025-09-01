import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Settings:
    # Environment Configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true" if os.getenv("DEBUG") else ENVIRONMENT == "development"
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/ai_quiz_dev")
    
    # CORS Configuration - parse from comma-separated string or use defaults
    _cors_origins = os.getenv("ALLOWED_ORIGINS", "")
    if _cors_origins:
        ALLOWED_ORIGINS: List[str] = [origin.strip() for origin in _cors_origins.split(",")]
    else:
        # Default CORS origins based on environment
        if ENVIRONMENT == "development":
            ALLOWED_ORIGINS: List[str] = [
                "http://localhost:3000",
                "http://localhost:5173", 
                "http://localhost:4173",
                "http://localhost:8080"
            ]
        else:
            ALLOWED_ORIGINS: List[str] = [
                "https://your-frontend-domain.vercel.app"
            ]
    
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Development-specific settings
    SKIP_DB_INIT: bool = os.getenv("SKIP_DB_INIT", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG" if DEBUG else "INFO")
    
    def __str__(self):
        return f"Settings(ENV={self.ENVIRONMENT}, DEBUG={self.DEBUG}, PORT={self.PORT}, DB_URL={'***' if self.DATABASE_URL else 'None'})"

settings = Settings()
