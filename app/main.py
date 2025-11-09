from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import api_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine

settings = get_settings()

# Create database tables on startup. Alembic should manage this in production.
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
static_dir = PROJECT_ROOT / "frontend"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")


@app.get("/", include_in_schema=False)
async def root_redirect() -> RedirectResponse:
    """Send browsers to the frontend login page."""

    if static_dir.exists():
        return RedirectResponse(url="/static/index.html")
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")
