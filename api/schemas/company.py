"""Company information schemas"""

from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime


class CompanyInfoBase(BaseModel):
    """Base company info schema"""

    name: str = Field(..., min_length=1, max_length=100)
    tagline: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    contact: Dict[str, Any] = Field(...)  # {email, phone, location}
    payment_terms: Dict[str, Any] = Field(...)  # {deposit, balance, methods[]}


class CompanyInfoUpdate(BaseModel):
    """Schema for updating company info"""

    name: str | None = Field(None, min_length=1, max_length=100)
    tagline: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, min_length=1)
    contact: Dict[str, Any] | None = None
    payment_terms: Dict[str, Any] | None = None


class CompanyInfoResponse(CompanyInfoBase):
    """Schema for company info response"""

    id: int
    updated_at: datetime

    class Config:
        from_attributes = True