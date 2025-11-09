from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class QrCodeCreate(BaseModel):
    expire_minutes: int = 15
    note: Optional[str] = ""
    use_limit: Optional[int] = 0


class QrCodeRead(BaseModel):
    id: int
    session_id: int
    token: str
    expires_at: datetime
    created_at: datetime
    note: str
    use_limit: int
    use_count: int
    qr_url: str
    session_location: str
    session_start: str

    model_config = ConfigDict(from_attributes=True)


class QrCheckinRequest(BaseModel):
    token: str
    device_info: Optional[str] = ""


class QrCheckinInfo(BaseModel):
    session_location: str
    session_start: str
    expires_at: datetime
    note: str = ""
