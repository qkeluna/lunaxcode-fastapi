"""Pricing plan model"""

from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, JSON
from sqlalchemy.sql import func
from api.database import Base


class PricingPlan(Base):
    """Pricing plans for services"""

    __tablename__ = "pricing_plans"

    id = Column(String, primary_key=True)  # e.g., 'landing_page'
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)  # In PHP
    currency = Column(String, nullable=False, default="PHP")
    timeline = Column(String, nullable=False)  # e.g., '48-hour delivery'
    features = Column(JSON, nullable=False)  # Array of feature strings
    popular = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )