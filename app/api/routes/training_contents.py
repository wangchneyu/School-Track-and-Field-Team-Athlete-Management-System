"""Training content management API routes."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api import deps
from app.models.training_content import TrainingContent
from app.models.user import User
from app.schemas.training_content import (
    TrainingContentCreate,
    TrainingContentRead,
    TrainingContentUpdate,
)

router = APIRouter(prefix="/training-contents", tags=["training-contents"])


@router.post("", response_model=TrainingContentRead)
def create_training_content(
    data: TrainingContentCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_admin),
) -> TrainingContentRead:
    """Create a new training content (admin only)."""

    content = TrainingContent(
        **data.model_dump(),
        created_by=current_user.id,
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


@router.get("", response_model=List[TrainingContentRead])
def list_training_contents(
    category: Optional[str] = Query(None, description="Filter by category"),
    target_group: Optional[str] = Query(None, description="Filter by target group"),
    intensity: Optional[str] = Query(None, description="Filter by intensity"),
    keyword: Optional[str] = Query(None, description="Search in title/content"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.get_current_active_user),
) -> List[TrainingContentRead]:
    """List training contents with optional filters."""

    query = db.query(TrainingContent)

    if category:
        query = query.filter(TrainingContent.category == category)
    if target_group:
        query = query.filter(TrainingContent.target_group == target_group)
    if intensity:
        query = query.filter(TrainingContent.intensity == intensity)
    if keyword:
        search = f"%{keyword}%"
        query = query.filter(
            or_(
                TrainingContent.title.ilike(search),
                TrainingContent.content.ilike(search),
            )
        )

    return query.order_by(TrainingContent.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{content_id}", response_model=TrainingContentRead)
def get_training_content(
    content_id: int,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.get_current_active_user),
) -> TrainingContentRead:
    """Get a single training content by ID."""

    content = db.query(TrainingContent).filter(TrainingContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Training content not found")
    return content


@router.put("/{content_id}", response_model=TrainingContentRead)
def update_training_content(
    content_id: int,
    data: TrainingContentUpdate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> TrainingContentRead:
    """Update a training content (admin only)."""

    content = db.query(TrainingContent).filter(TrainingContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Training content not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(content, field, value)

    db.commit()
    db.refresh(content)
    return content


@router.delete("/{content_id}", status_code=204)
def delete_training_content(
    content_id: int,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> None:
    """Delete a training content (admin only)."""

    content = db.query(TrainingContent).filter(TrainingContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Training content not found")

    db.delete(content)
    db.commit()
    return None


@router.get("/categories/list", response_model=List[str])
def list_categories(
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.get_current_active_user),
) -> List[str]:
    """Get all unique training content categories."""

    categories = (
        db.query(TrainingContent.category)
        .filter(TrainingContent.category != "")
        .distinct()
        .all()
    )
    return [c[0] for c in categories]


@router.get("/target-groups/list", response_model=List[str])
def list_target_groups(
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.get_current_active_user),
) -> List[str]:
    """Get all unique target groups."""

    groups = (
        db.query(TrainingContent.target_group)
        .filter(TrainingContent.target_group != "")
        .distinct()
        .all()
    )
    return [g[0] for g in groups]
