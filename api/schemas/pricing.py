"""Pricing plan schemas"""

from pydantic import BaseModel, Field
from typing import List
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

    name: str | None = Field(None, min_length=1, max_length=100)
    price: int | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=10)
    timeline: str | None = Field(None, min_length=1, max_length=100)
    features: List[str] | None = Field(None, min_items=1)
    popular: bool | None = None


class PricingPlanResponse(PricingPlanBase):
    """Schema for pricing plan response"""

    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True