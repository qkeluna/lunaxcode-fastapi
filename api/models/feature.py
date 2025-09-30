"""Feature model"""

from sqlalchemy import Column, String, Text, Integer, TIMESTAMP
from sqlalchemy.sql import func
from api.database import Base


class Feature(Base):
    """Marketing features displayed on website"""

    __tablename__ = "features"

    id = Column(Integer, primary_key=True, autoincrement=True)
    icon = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    display_order = Column(Integer)  # For ordering features
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )