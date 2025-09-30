"""Add-on service model"""

from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.sql import func
from api.database import Base


class Addon(Base):
    """Additional services that can be added to packages"""

    __tablename__ = "addons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    price_range = Column(String, nullable=False)  # e.g., '1500-2000'
    currency = Column(String, nullable=False, default="PHP")
    unit = Column(String, nullable=False)  # 'each', 'project', 'monthly'
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )