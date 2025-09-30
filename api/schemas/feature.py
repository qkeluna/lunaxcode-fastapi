"""Feature schemas"""

from pydantic import BaseModel, Field
from datetime import datetime


class FeatureBase(BaseModel):
    """Base feature schema"""

    icon: str = Field(..., min_length=1, max_length=10)
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    display_order: int | None = Field(None, ge=0)


class FeatureCreate(FeatureBase):
    """Schema for creating feature"""

    pass


class FeatureUpdate(BaseModel):
    """Schema for updating feature"""

    icon: str | None = Field(None, min_length=1, max_length=10)
    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1)
    display_order: int | None = Field(None, ge=0)


class FeatureResponse(FeatureBase):
    """Schema for feature response"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True