"""Contact form submission model"""

from sqlalchemy import Column, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from api.database import Base


class ContactSubmission(Base):
    """Contact form submissions from homepage"""

    __tablename__ = "contact_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    subject = Column(String(255))
    message = Column(Text, nullable=False)
    status = Column(String(20), default="new", index=True)  # new, read, replied, archived
    replied_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    submission_metadata = Column(JSONB)  # Source, UTM params, etc.
