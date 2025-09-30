"""Onboarding questions model"""

from sqlalchemy import Column, String, Integer, JSON, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from api.database import Base


class OnboardingQuestion(Base):
    """Dynamic onboarding questions for each service type"""

    __tablename__ = "onboarding_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_type = Column(
        String, ForeignKey("services.id"), nullable=False, unique=True
    )
    title = Column(String, nullable=False)
    questions = Column(JSON, nullable=False)  # Array of question objects
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )