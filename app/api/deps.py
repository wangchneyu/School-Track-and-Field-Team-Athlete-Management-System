from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import SecuritySettings, decode_token
from app.core.database import db_manager
from app.core.transaction import TransactionManager
from app.models.athlete import Athlete
from app.models.user import User
from app.schemas.auth import TokenPayload

settings = get_settings()
security_settings = SecuritySettings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# 创建事务管理器
transaction_manager = TransactionManager(db_manager)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for FastAPI dependencies."""
    return db_manager.get_session_dependency()


def get_db_with_transaction() -> Generator[Session, None, None]:
    """Yield a database session with transaction management."""
    return db_manager.get_session_dependency()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Validate the JWT token and return the current user."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        # 使用新的安全配置
        payload = decode_token(token)
        token_data = TokenPayload(**payload)
    except (JWTError, ValueError) as exc:
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
