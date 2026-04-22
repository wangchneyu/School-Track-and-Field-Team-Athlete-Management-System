import secrets
import string
from typing import Optional, List
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseSettings, Field
from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecuritySettings(BaseSettings):
    """安全配置"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)
    
    # JWT配置
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    
    # 密码策略
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # 安全配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # 秒
    
    # 敏感操作配置
    SESSION_TIMEOUT: int = 30 * 60  # 30分钟
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION: int = 15 * 60  # 15分钟


def generate_password(length: int = 12) -> str:
    """生成随机密码"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))


def validate_password_strength(password: str) -> tuple[bool, List[str]]:
    """验证密码强度"""
    errors = []
    
    if len(password) < SecuritySettings().PASSWORD_MIN_LENGTH:
        errors.append(f"密码长度至少需要{SecuritySettings().PASSWORD_MIN_LENGTH}个字符")
    
    if SecuritySettings().PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        errors.append("密码需要包含大写字母")
    
    if SecuritySettings().PASSWORD_REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        errors.append("密码需要包含小写字母")
    
    if SecuritySettings().PASSWORD_REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
        errors.append("密码需要包含数字")
    
    if SecuritySettings().PASSWORD_REQUIRE_SPECIAL and not any(c in "!@#$%^&*" for c in password):
        errors.append("密码需要包含特殊字符")
    
    return len(errors) == 0, errors


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> dict:
    """创建访问令牌"""
    settings = SecuritySettings()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    
    return {
        "access_token": jwt.encode(
            {"sub": subject, "exp": expire, "iat": datetime.now(timezone.utc)},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        ),
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def decode_token(token: str) -> dict:
    """解码令牌"""
    settings = SecuritySettings()
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc