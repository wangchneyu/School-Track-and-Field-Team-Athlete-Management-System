from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.core.security import get_password_hash
from app.models.athlete import Athlete
from app.models.user import User
from app.schemas.athlete import AthleteCreate, AthleteRead, AthleteUpdate

router = APIRouter(prefix="/athletes", tags=["athletes"])


@router.post("", response_model=AthleteRead)
def create_athlete(
    data: AthleteCreate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> AthleteRead:
    """Create a new athlete and linked user account."""

    username = data.student_id
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Student ID already registered as username")
    if db.query(Athlete).filter(Athlete.student_id == data.student_id).first():
        raise HTTPException(status_code=400, detail="Student ID already exists")
    password = data.password or "123456"
    user = User(username=username, password_hash=get_password_hash(password), role="athlete")
    db.add(user)
    db.flush()
    athlete = Athlete(
        user_id=user.id,
        name=data.name,
        student_id=data.student_id,
        gender=data.gender,
        group=data.group or "",
        main_event=data.main_event or "",
        phone=data.phone or "",
    )
    db.add(athlete)
    db.commit()
    db.refresh(athlete)
    return athlete


@router.get("", response_model=List[AthleteRead])
def list_athletes(
    skip: int = 0,
    limit: int = Query(50, le=200),
    group: Optional[str] = None,
    name: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> List[AthleteRead]:
    """List athletes with optional filters."""

    query = db.query(Athlete)
    if group:
        query = query.filter(Athlete.group == group)
    if name:
        query = query.filter(Athlete.name.contains(name))
    return query.offset(skip).limit(limit).all()


@router.get("/me", response_model=AthleteRead)
def get_me(athlete: Athlete = Depends(deps.get_current_athlete)) -> AthleteRead:
    """Return the current athlete profile."""

    return athlete


@router.get("/{athlete_id}", response_model=AthleteRead)
def get_athlete(
    athlete_id: int,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> AthleteRead:
    """Return details for a single athlete."""

    athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete


@router.put("/{athlete_id}", response_model=AthleteRead)
def update_athlete(
    athlete_id: int,
    data: AthleteUpdate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> AthleteRead:
    """Update athlete information."""

    athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(athlete, field, value)
    db.commit()
    db.refresh(athlete)
    return athlete
