"""Lead model"""

from sqlalchemy import Column, String, Text, Integer, JSON, TIMESTAMP, ForeignKey, Index
from sqlalchemy.sql import func
from api.database import Base


class Lead(Base):
    """Customer lead submissions with dual data storage"""

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_type = Column(String, ForeignKey("services.id"), nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    company = Column(String)
    project_description = Column(Text)
    answers = Column(JSON, nullable=False)  # Structured data for queries
    ai_prompt = Column(Text, nullable=False)  # AI-formatted prompt
    status = Column(String, default="new")  # 'new', 'contacted', 'converted', 'rejected'
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_leads_status", "status"),
        Index("idx_leads_created_at", "created_at"),
        Index("idx_leads_email", "email"),
    )