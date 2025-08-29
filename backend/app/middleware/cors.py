from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..config import settings

def add_cors_middleware(app: FastAPI):
    """Add CORS middleware to the FastAPI application"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


