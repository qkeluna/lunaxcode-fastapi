"""Lead schemas"""
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Dict, Any, Optional
from datetime import datetime


class LeadBase(BaseModel):
    """Base lead schema"""

    service_type: str = Field(..., min_length=1, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=100)
    project_description: Optional[str] = None
    answers: Dict[str, Any] = Field(...)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> str | None:
        """Validate Philippine phone number format"""
        if v and not v.startswith("+63"):
            raise ValueError("Phone must be Philippine number starting with +63")
        return v


class LeadCreate(LeadBase):
    """Schema for creating lead (public endpoint)"""

    pass


class LeadUpdate(BaseModel):
    """Schema for updating lead (admin only)"""

    status: Optional[str] = Field(None, pattern="^(new|contacted|converted|rejected)$")


class LeadResponse(LeadBase):
    """Schema for lead response"""

    id: int
    ai_prompt: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True