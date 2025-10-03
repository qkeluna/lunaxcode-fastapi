"""Onboarding submission model"""

from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from api.database import Base


class OnboardingSubmission(Base):
    """Customer onboarding submissions with payment tracking"""

    __tablename__ = "onboarding_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_type = Column(String(50), nullable=False, index=True)
    customer_email = Column(String(255), nullable=False, index=True)
    customer_name = Column(String(255), nullable=False)
    customer_company = Column(String(255))
    customer_phone = Column(String(50))
    answers = Column(JSONB, nullable=False)  # All onboarding answers
    status = Column(String(20), default="pending", index=True)  # pending, paid, in-progress, completed, cancelled
    payment_status = Column(String(20), default="unpaid")  # unpaid, paid, refunded
    payment_intent_id = Column(String(255))  # Stripe payment intent ID
    payment_url = Column(Text)  # Stripe checkout URL
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    submission_metadata = Column(JSONB)  # Additional tracking data (UTM, referrer, etc.)
