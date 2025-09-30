"""Onboarding question schemas"""
from typing import Optional

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class OnboardingQuestionBase(BaseModel):
    """Base onboarding question schema"""

    service_type: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=200)
    questions: List[Dict[str, Any]] = Field(..., min_items=1)


class OnboardingQuestionCreate(OnboardingQuestionBase):
    """Schema for creating onboarding questions"""

    pass


class OnboardingQuestionUpdate(BaseModel):
    """Schema for updating onboarding questions"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    questions: List[Dict[str, Any]] | None = Field(None, min_items=1)


class OnboardingQuestionResponse(OnboardingQuestionBase):
    """Schema for onboarding question response"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True