from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.athlete import Athlete
from app.models.rating import Rating
from app.models.user import User
from app.schemas.rating import RatingCreate, RatingRead

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.post("", response_model=RatingRead)
def create_rating(
    data: RatingCreate,
    db: Session = Depends(deps.get_db),
    coach: User = Depends(deps.require_admin),
) -> RatingRead:
    """Create a coaching rating entry."""

    payload = data.model_dump()
    payload["coach_id"] = coach.id
    rating = Rating(**payload)
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating


@router.get("", response_model=List[RatingRead])
def list_ratings(
    athlete_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> List[RatingRead]:
    """List ratings optionally filtered by athlete."""

    query = db.query(Rating)
    if athlete_id:
        query = query.filter(Rating.athlete_id == athlete_id)
    return query.order_by(Rating.date.desc()).all()


@router.get("/me", response_model=List[RatingRead])
def my_ratings(
    athlete: Athlete = Depends(deps.get_current_athlete),
    db: Session = Depends(deps.get_db),
) -> List[RatingRead]:
    """Return current athlete's ratings."""

    return (
        db.query(Rating)
        .filter(Rating.athlete_id == athlete.id)
        .order_by(Rating.date.desc())
        .all()
    )
