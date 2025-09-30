"""Company information model"""

from sqlalchemy import Column, String, Text, Integer, JSON, TIMESTAMP, CheckConstraint
from sqlalchemy.sql import func
from api.database import Base


class CompanyInfo(Base):
    """Company information (singleton table)"""

    __tablename__ = "company_info"

    id = Column(Integer, primary_key=True, default=1)  # Always 1
    name = Column(String, nullable=False)
    tagline = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    contact = Column(JSON, nullable=False)  # {email, phone, location}
    payment_terms = Column(JSON, nullable=False)  # {deposit, balance, methods[]}
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (CheckConstraint("id = 1", name="single_row_check"),)