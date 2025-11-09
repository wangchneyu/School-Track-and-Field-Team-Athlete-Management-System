"""ASGI entrypoint for deployment (uvicorn main:app)."""

from app.main import app

__all__ = ("app",)
