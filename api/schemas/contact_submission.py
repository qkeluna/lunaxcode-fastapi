"""Contact submission schemas"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID


class ContactMetadata(BaseModel):
    """Metadata for contact submission"""
    timestamp: Optional[int] = None
    source: Optional[str] = None  # "homepage", "footer", etc.
    user_agent: Optional[str] = None


class ContactSubmissionCreate(BaseModel):
    """Schema for creating contact submission"""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    subject: Optional[str] = Field(None, max_length=255)
    message: str = Field(..., min_length=1)
    metadata: Optional[ContactMetadata] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "subject": "Project Inquiry",
                "message": "I'm interested in building a web application...",
                "metadata": {
                    "source": "homepage",
                    "timestamp": 1234567890
                }
            }
        }


class ContactSubmissionResponse(BaseModel):
    """Response after successful contact submission"""
    success: bool = True
    message_id: UUID
    message: str = "Thank you! We'll get back to you soon."

    class Config:
        from_attributes = True


class ContactSubmissionDetail(BaseModel):
    """Full contact submission details"""
    id: UUID
    name: str
    email: str
    subject: Optional[str] = None
    message: str
    status: str
    replied_at: Optional[datetime] = None
    created_at: datetime
    submission_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
