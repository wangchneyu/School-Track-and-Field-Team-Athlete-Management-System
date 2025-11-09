"""FastAPI routers grouped by domain."""

from fastapi import APIRouter

from app.api.routes import (
    attendance,
    athletes,
    auth,
    events,
    featured_event,
    rankings,
    ratings,
    scores,
    sessions,
    stats,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(athletes.router)
api_router.include_router(events.router)
api_router.include_router(featured_event.router)
api_router.include_router(sessions.router)
api_router.include_router(attendance.router)
api_router.include_router(scores.router)
api_router.include_router(ratings.router)
api_router.include_router(rankings.router)
api_router.include_router(stats.router)
