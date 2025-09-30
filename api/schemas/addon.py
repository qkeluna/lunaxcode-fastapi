"""Add-on schemas"""

from pydantic import BaseModel, Field
from datetime import datetime


class AddonBase(BaseModel):
    """Base add-on schema"""

    name: str = Field(..., min_length=1, max_length=100)
    price_range: str = Field(..., pattern=r"^\d+-\d+$")  # e.g., "1500-2000"
    currency: str = Field(default="PHP", max_length=10)
    unit: str = Field(..., min_length=1, max_length=50)


class AddonCreate(AddonBase):
    """Schema for creating add-on"""

    pass


class AddonUpdate(BaseModel):
    """Schema for updating add-on"""

    name: str | None = Field(None, min_length=1, max_length=100)
    price_range: str | None = Field(None, pattern=r"^\d+-\d+$")
    currency: str | None = Field(None, max_length=10)
    unit: str | None = Field(None, min_length=1, max_length=50)


class AddonResponse(AddonBase):
    """Schema for add-on response"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True