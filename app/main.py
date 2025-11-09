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

# Serve Vue frontend build output
PROJECT_ROOT = Path(__file__).resolve().parent.parent
vue_dist = PROJECT_ROOT / "vue-frontend" / "dist"

if vue_dist.exists():
    if (vue_dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=vue_dist / "assets"), name="vue-assets")
    if (vue_dist / "images").exists():
        app.mount("/images", StaticFiles(directory=vue_dist / "images"), name="vue-images")


@app.get("/", include_in_schema=False)
async def root_redirect() -> RedirectResponse:
    """Send browsers to the Vue frontend or API docs."""
    if vue_dist.exists():
        return RedirectResponse(url="/app")
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")


@app.get("/login", include_in_schema=False)
@app.get("/admin/{rest:path}", include_in_schema=False)
@app.get("/athlete/{rest:path}", include_in_schema=False)
@app.get("/app", include_in_schema=False)
async def serve_vue_spa() -> "Response":
    """Serve the Vue SPA index.html for all frontend routes."""
    from fastapi.responses import FileResponse

    if vue_dist.exists():
        return FileResponse(vue_dist / "index.html")
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")
