"""Pydantic schemas for training content."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TrainingContentBase(BaseModel):
    """Base schema for training content."""

    title: str = Field(..., min_length=1, max_length=100, description="训练标题")
    content: str = Field(..., min_length=1, description="训练内容详情")
    category: Optional[str] = Field(default="", max_length=50, description="训练类别")
    target_group: Optional[str] = Field(default="", max_length=50, description="目标训练组")
    duration: Optional[int] = Field(default=60, ge=1, le=300, description="预计时长(分钟)")
    intensity: Optional[str] = Field(default="medium", pattern="^(low|medium|high)$", description="强度等级")


class TrainingContentCreate(TrainingContentBase):
    """Schema for creating training content."""

    pass


class TrainingContentUpdate(BaseModel):
    """Schema for updating training content."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    content: Optional[str] = Field(default=None, min_length=1)
    category: Optional[str] = Field(default=None, max_length=50)
    target_group: Optional[str] = Field(default=None, max_length=50)
    duration: Optional[int] = Field(default=None, ge=1, le=300)
    intensity: Optional[str] = Field(default=None, pattern="^(low|medium|high)$")


class TrainingContentRead(TrainingContentBase):
    """Schema for reading training content."""

    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TrainingContentFilter(BaseModel):
    """Filter schema for training content."""

    category: Optional[str] = None
    target_group: Optional[str] = None
    intensity: Optional[str] = None
    keyword: Optional[str] = None
