"""Onboarding submission schemas"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID


class OnboardingMetadata(BaseModel):
    """Metadata for tracking submission source"""
    timestamp: Optional[int] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None


class OnboardingSubmissionCreate(BaseModel):
    """Schema for creating onboarding submission"""
    service_type: str = Field(..., min_length=1, max_length=50)
    answers: Dict[str, Any] = Field(...)  # Includes fullName, email, phone, company, and service-specific answers
    metadata: Optional[OnboardingMetadata] = None

    class Config:
        json_schema_extra = {
            "example": {
                "service_type": "website",
                "answers": {
                    "fullName": "John Doe",
                    "email": "john@example.com",
                    "company": "Acme Inc",
                    "phone": "+1234567890",
                    "websiteType": "e-commerce",
                    "pages": ["Home", "Shop", "About"],
                    "timeline": "2-4 weeks"
                },
                "metadata": {
                    "timestamp": 1234567890,
                    "referrer": "https://google.com"
                }
            }
        }


class OnboardingSubmissionResponse(BaseModel):
    """Response after successful submission"""
    success: bool = True
    submission_id: UUID
    payment_url: Optional[str] = None
    message: str = "Submission received successfully"

    class Config:
        from_attributes = True


class OnboardingSubmissionDetail(BaseModel):
    """Full submission details"""
    id: UUID
    service_type: str
    customer_email: str
    customer_name: str
    customer_company: Optional[str] = None
    customer_phone: Optional[str] = None
    answers: Dict[str, Any]
    status: str
    payment_status: str
    payment_intent_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    submission_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class SubmissionStatusResponse(BaseModel):
    """Submission status check response"""
    submission_id: UUID
    status: str
    payment_status: str
    created_at: datetime
    estimated_completion: Optional[datetime] = None
    updates: list[Dict[str, Any]] = []

    class Config:
        from_attributes = True


class AdminSubmissionUpdate(BaseModel):
    """Admin update for submission"""
    status: Optional[str] = Field(None, pattern="^(pending|paid|in-progress|completed|cancelled)$")
    notes: Optional[str] = None
