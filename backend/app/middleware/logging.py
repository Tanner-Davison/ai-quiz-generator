"""Logging middleware for FastAPI application."""

import logging
import time

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info("Request: %s %s", request.method, request.url)

        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info("Response: %s - %.4fs", response.status_code, process_time)

        return response


def add_logging_middleware(app: FastAPI):
    """Add logging middleware to the application"""
    app.add_middleware(LoggingMiddleware)
