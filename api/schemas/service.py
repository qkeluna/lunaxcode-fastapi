"""Service schemas"""

from typing import Optional
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

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    details: Optional[str] = Field(None, min_length=1)
    icon: Optional[str] = Field(None, min_length=1, max_length=10)
    timeline: Optional[str] = Field(None, min_length=1, max_length=100)


class ServiceResponse(ServiceBase):
    """Schema for service response"""

    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True