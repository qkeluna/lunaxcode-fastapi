"""Contact submission service layer"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID

from api.models.contact_submission import ContactSubmission
from api.schemas.contact_submission import ContactSubmissionCreate


async def create_contact_submission(
    contact_data: ContactSubmissionCreate,
    db: AsyncSession
) -> ContactSubmission:
    """Create new contact submission"""
    submission = ContactSubmission(
        name=contact_data.name,
        email=contact_data.email,
        subject=contact_data.subject,
        message=contact_data.message,
        status="new",
        submission_metadata=contact_data.metadata.dict() if contact_data.metadata else None
    )
    
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    
    return submission


async def get_contact_by_id(
    contact_id: UUID,
    db: AsyncSession
) -> Optional[ContactSubmission]:
    """Get contact submission by ID"""
    result = await db.execute(
        select(ContactSubmission).filter(ContactSubmission.id == contact_id)
    )
    return result.scalar_one_or_none()


async def get_contacts(
    db: AsyncSession,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[ContactSubmission]:
    """Get contact submissions with optional filtering"""
    query = select(ContactSubmission).order_by(ContactSubmission.created_at.desc())
    
    if status:
        query = query.filter(ContactSubmission.status == status)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def update_contact_status(
    contact_id: UUID,
    status: str,
    db: AsyncSession
) -> Optional[ContactSubmission]:
    """Update contact status"""
    result = await db.execute(
        select(ContactSubmission).filter(ContactSubmission.id == contact_id)
    )
    contact = result.scalar_one_or_none()
    
    if not contact:
        return None
    
    contact.status = status
    
    await db.commit()
    await db.refresh(contact)
    
    return contact
