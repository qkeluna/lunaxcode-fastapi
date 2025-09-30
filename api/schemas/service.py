"""Service schemas"""

from pydantic import BaseModel, Field
from datetime import datetime


class ServiceBase(BaseModel):
    """Base service schema"""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    details: str = Field(..., min_length=1)
    icon: str = Field(..., min_length=1, max_length=10)
    timeline: str = Field(..., min_length=1, max_length=100)


class ServiceCreate(ServiceBase):
    """Schema for creating service"""

    id: str = Field(..., min_length=1, max_length=50)


class ServiceUpdate(BaseModel):
    """Schema for updating service"""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1, max_length=500)
    details: str | None = Field(None, min_length=1)
    icon: str | None = Field(None, min_length=1, max_length=10)
    timeline: str | None = Field(None, min_length=1, max_length=100)


class ServiceResponse(ServiceBase):
    """Schema for service response"""

    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True