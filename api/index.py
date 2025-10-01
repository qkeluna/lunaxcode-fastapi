"""Vercel serverless handler - exports FastAPI app for ASGI runtime"""

# Vercel's Python runtime auto-detects ASGI apps
# Simply import and export the FastAPI app - no wrapper needed
from api.main import app

# This is the entry point Vercel will use
__all__ = ["app"]