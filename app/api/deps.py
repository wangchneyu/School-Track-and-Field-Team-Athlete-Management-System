from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import ALGORITHM
from app.db.session import SessionLocal
from app.models.athlete import Athlete
from app.models.user import User
from app.schemas.auth import TokenPayload

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for FastAPI dependencies."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Validate the JWT token and return the current user."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except JWTError as exc:  # pragma: no cover - FastAPI handles response
        raise credentials_exception from exc
    if not token_data.sub:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.sub).first()
    if not user:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user is active."""

    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Allow access only to admin users."""

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privilege required")
    return current_user


def get_current_athlete(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Athlete:
    """Return the athlete profile associated with the current user."""

    athlete = db.query(Athlete).filter(Athlete.user_id == current_user.id).first()
    if not athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete profile not found")
    return athlete
