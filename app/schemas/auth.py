"""Authentication related schemas."""

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str


class TokenPayload(BaseModel):
    sub: str | None = None


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str
