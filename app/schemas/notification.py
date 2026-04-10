"""Pydantic schemas for the notification system."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class NotificationBase(BaseModel):
    """Shared notification fields."""

    title: str = Field(..., min_length=1, max_length=200, description="通知标题")
    content: str = Field(..., min_length=1, description="通知内容")
    type: str = Field(
        default="general",
        pattern="^(training|announcement|general)$",
        description="通知类型",
    )
    priority: str = Field(
        default="normal",
        pattern="^(low|normal|high|urgent)$",
        description="优先级",
    )
    target_group: Optional[str] = Field(
        default="", max_length=50, description="目标分组, 空表示全部"
    )
    session_id: Optional[int] = Field(
        default=None, description="关联的训练课程ID"
    )


class NotificationCreate(NotificationBase):
    """Payload for creating a notification."""

    pass


class NotificationUpdate(BaseModel):
    """Payload for updating a notification."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    content: Optional[str] = Field(default=None, min_length=1)
    type: Optional[str] = Field(
        default=None, pattern="^(training|announcement|general)$"
    )
    priority: Optional[str] = Field(
        default=None, pattern="^(low|normal|high|urgent)$"
    )
    target_group: Optional[str] = Field(default=None, max_length=50)
    is_active: Optional[bool] = None


class NotificationReadStatus(BaseModel):
    """Schema representing a read status entry."""

    user_id: int
    username: str
    read_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationRead(NotificationBase):
    """Notification data returned to clients."""

    id: int
    created_by: int
    created_at: datetime
    is_active: bool
    creator_name: Optional[str] = None
    session_date: Optional[str] = None
    session_location: Optional[str] = None
    session_time: Optional[str] = None
    # Read status info
    is_read: bool = False
    read_at: Optional[datetime] = None
    read_count: int = 0
    total_target: int = 0

    model_config = ConfigDict(from_attributes=True)


class NotificationReadDetail(NotificationRead):
    """Notification with detailed read status list (for admin)."""

    read_users: List[NotificationReadStatus] = []
    unread_users: List[dict] = []
