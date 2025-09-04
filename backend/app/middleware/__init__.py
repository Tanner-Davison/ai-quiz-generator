# middleware/__init__.py
"""Middleware package for the AI Quiz Generator."""

from .cors import add_cors_middleware
from .logging import add_logging_middleware

# Optional: Define what gets imported with "from app.middleware import *"
__all__ = ["add_cors_middleware", "add_logging_middleware"]
