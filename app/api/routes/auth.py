from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, PasswordChangeRequest, Token

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def _do_login(username: str, password: str, db: Session) -> Token:
    """Shared login logic for both JSON and form-data endpoints."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    access_token = create_access_token(
        user.username,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, token_type="bearer", role=user.role)


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db: Session = Depends(deps.get_db),
) -> Token:
    """Authenticate a user and return an access token.

    Supports both JSON body ``{"username": ..., "password": ...}`` and
    standard OAuth2 form-data for backward compatibility.
    """
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        login_req = LoginRequest(**body)
        return _do_login(login_req.username, login_req.password, db)
    # Fall back to form-data (OAuth2 spec)
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing credentials")
    return _do_login(str(username), str(password), db)


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
