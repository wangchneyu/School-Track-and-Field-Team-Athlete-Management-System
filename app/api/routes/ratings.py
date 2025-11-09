from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.athlete import Athlete
from app.models.rating import Rating
from app.models.user import User
from app.schemas.rating import RatingCreate, RatingRead, RatingUpdate

router = APIRouter(prefix="/ratings", tags=["ratings"])


def _enrich_ratings(ratings: list, db: Session) -> List[dict]:
    """Add athlete_name to rating records."""
    athlete_ids = {r.athlete_id for r in ratings}
    athletes = {a.id: a.name for a in db.query(Athlete).filter(Athlete.id.in_(athlete_ids)).all()} if athlete_ids else {}
    result = []
    for r in ratings:
        d = RatingRead.model_validate(r).model_dump()
        d["athlete_name"] = athletes.get(r.athlete_id, "")
        result.append(d)
    return result


@router.post("", response_model=RatingRead)
def create_rating(
    data: RatingCreate,
    db: Session = Depends(deps.get_db),
    coach: User = Depends(deps.require_admin),
) -> RatingRead:
    """Create a coaching rating entry."""

    from datetime import date as date_module
    
    payload = data.model_dump()
    payload["coach_id"] = coach.id
    
    # Convert string date to date object if provided
    date_str = payload.pop("date", None)
    if date_str:
        try:
            payload["date"] = date_module.fromisoformat(date_str)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid date format: {date_str}. Expected YYYY-MM-DD")
    else:
        payload["date"] = date_module.today()
    
    rating = Rating(**payload)
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating


@router.get("")
def list_ratings(
    athlete_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> List[dict]:
    """List ratings optionally filtered by athlete."""

    query = db.query(Rating)
    if athlete_id:
        query = query.filter(Rating.athlete_id == athlete_id)
    ratings = query.order_by(Rating.date.desc()).all()
    return _enrich_ratings(ratings, db)


@router.get("/me")
def my_ratings(
    athlete: Athlete = Depends(deps.get_current_athlete),
    db: Session = Depends(deps.get_db),
) -> List[dict]:
    """Return current athlete's ratings."""

    ratings = (
        db.query(Rating)
        .filter(Rating.athlete_id == athlete.id)
        .order_by(Rating.date.desc())
        .all()
    )
    return _enrich_ratings(ratings, db)


@router.put("/{rating_id}", response_model=RatingRead)
def update_rating(
    rating_id: int,
    data: RatingUpdate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> RatingRead:
    """Update a rating entry."""

    from datetime import date as date_module
    
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    update_data = data.model_dump(exclude_unset=True)
    
    # Convert string date to date object if provided
    if "date" in update_data and update_data["date"]:
        try:
            update_data["date"] = date_module.fromisoformat(update_data["date"])
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid date format: {update_data['date']}. Expected YYYY-MM-DD")
    
    for field, value in update_data.items():
        setattr(rating, field, value)
    db.commit()
    db.refresh(rating)
    return rating


@router.delete("/{rating_id}", status_code=204)
def delete_rating(
    rating_id: int,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> None:
    """Delete a rating entry."""

    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    db.delete(rating)
    db.commit()
    return None
