"""Pricing plan schemas"""
from typing import Optional

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PricingPlanBase(BaseModel):
    """Base pricing plan schema"""

    name: str = Field(..., min_length=1, max_length=100)
    price: int = Field(..., ge=0)
    currency: str = Field(default="PHP", max_length=10)
    timeline: str = Field(..., min_length=1, max_length=100)
    features: List[str] = Field(..., min_items=1)
    popular: bool = Field(default=False)


class PricingPlanCreate(PricingPlanBase):
    """Schema for creating pricing plan"""

    id: str = Field(..., min_length=1, max_length=50)


class PricingPlanUpdate(BaseModel):
    """Schema for updating pricing plan"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[int] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    timeline: Optional[str] = Field(None, min_length=1, max_length=100)
    features: List[str] | None = Field(None, min_items=1)
    popular: Optional[bool] = None


class PricingPlanResponse(PricingPlanBase):
    """Schema for pricing plan response"""

    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True