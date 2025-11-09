from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import PasswordChangeRequest, Token

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db),
) -> Token:
    """Authenticate a user and return an access token."""

    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    access_token = create_access_token(
        user.username,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, token_type="bearer", role=user.role)


@router.post("/change-password")
def change_password(
    payload: PasswordChangeRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> dict:
    """Allow any logged-in user to update their password."""

    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")
    current_user.password_hash = get_password_hash(payload.new_password)
    db.add(current_user)
    db.commit()
    return {"detail": "Password updated successfully"}
