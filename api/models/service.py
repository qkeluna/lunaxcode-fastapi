"""Service model"""

from sqlalchemy import Column, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from api.database import Base


class Service(Base):
    """Services offered by Lunaxcode"""

    __tablename__ = "services"

    id = Column(String, primary_key=True)  # e.g., 'landing_page'
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    details = Column(Text, nullable=False)
    icon = Column(String, nullable=False)  # Emoji or icon identifier
    timeline = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )