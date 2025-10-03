"""Contact submission routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from api.database import get_db
from api.schemas.contact_submission import (
    ContactSubmissionCreate,
    ContactSubmissionResponse,
    ContactSubmissionDetail
)
from api.services.contact_service import (
    create_contact_submission,
    get_contact_by_id,
    get_contacts,
    update_contact_status
)
from api.utils.auth import verify_api_key

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("/submit", response_model=ContactSubmissionResponse, status_code=201)
async def submit_contact(
    contact: ContactSubmissionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit contact form (public endpoint)
    
    This endpoint:
    1. Validates contact data
    2. Saves to database with status 'new'
    3. TODO: Send email notification to admin
    4. TODO: Send auto-reply to customer
    """
    try:
        db_contact = await create_contact_submission(contact, db)
        
        # TODO: Send email notifications
        # await send_admin_contact_notification(db_contact)
        # await send_customer_autoreply(db_contact)
        
        return ContactSubmissionResponse(
            success=True,
            message_id=db_contact.id,
            message="Thank you! We'll get back to you soon."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/submissions", response_model=List[ContactSubmissionDetail])
async def list_contacts(
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """List all contact submissions (admin only)"""
    contacts = await get_contacts(db, status=status, skip=skip, limit=limit)
    return contacts


@router.get("/submissions/{contact_id}", response_model=ContactSubmissionDetail)
async def get_contact(
    contact_id: UUID,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get contact submission details (admin only)"""
    contact = await get_contact_by_id(contact_id, db)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.patch("/submissions/{contact_id}/status")
async def update_contact(
    contact_id: UUID,
    status: str,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update contact status (admin only)"""
    contact = await update_contact_status(contact_id, status, db)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"success": True, "message": "Status updated"}
