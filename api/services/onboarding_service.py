"""Onboarding submission service layer"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID

from api.models.onboarding_submission import OnboardingSubmission
from api.schemas.onboarding_submission import (
    OnboardingSubmissionCreate,
    AdminSubmissionUpdate
)


async def create_onboarding_submission(
    submission_data: OnboardingSubmissionCreate,
    db: AsyncSession
) -> OnboardingSubmission:
    """
    Create new onboarding submission
    
    - Extracts customer info from answers
    - Stores full answers as JSONB
    - Returns submission with ID for payment flow
    """
    answers = submission_data.answers
    
    # Extract customer info from answers
    customer_email = answers.get("email", "")
    customer_name = answers.get("fullName", "")
    customer_company = answers.get("company")
    customer_phone = answers.get("phone")
    
    # Create submission
    submission = OnboardingSubmission(
        service_type=submission_data.service_type,
        customer_email=customer_email,
        customer_name=customer_name,
        customer_company=customer_company,
        customer_phone=customer_phone,
        answers=answers,
        status="pending",
        payment_status="unpaid",
        submission_metadata=submission_data.metadata.dict() if submission_data.metadata else None
    )
    
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    
    return submission


async def get_submission_by_id(
    submission_id: UUID,
    db: AsyncSession
) -> Optional[OnboardingSubmission]:
    """Get submission by ID"""
    result = await db.execute(
        select(OnboardingSubmission).filter(OnboardingSubmission.id == submission_id)
    )
    return result.scalar_one_or_none()


async def get_submissions(
    db: AsyncSession,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[OnboardingSubmission]:
    """Get submissions with optional filtering"""
    query = select(OnboardingSubmission).order_by(OnboardingSubmission.created_at.desc())
    
    if status:
        query = query.filter(OnboardingSubmission.status == status)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def update_submission_status(
    submission_id: UUID,
    update_data: AdminSubmissionUpdate,
    db: AsyncSession
) -> Optional[OnboardingSubmission]:
    """Update submission status (admin only)"""
    result = await db.execute(
        select(OnboardingSubmission).filter(OnboardingSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    
    if not submission:
        return None
    
    if update_data.status:
        submission.status = update_data.status
    
    # Store notes in submission_metadata
    if update_data.notes:
        if not submission.submission_metadata:
            submission.submission_metadata = {}
        if "admin_notes" not in submission.submission_metadata:
            submission.submission_metadata["admin_notes"] = []
        submission.submission_metadata["admin_notes"].append({
            "note": update_data.notes,
            "timestamp": str(submission.updated_at)
        })
    
    await db.commit()
    await db.refresh(submission)
    
    return submission


async def update_payment_status(
    submission_id: UUID,
    payment_intent_id: str,
    payment_status: str,
    db: AsyncSession
) -> Optional[OnboardingSubmission]:
    """Update payment status from Stripe webhook"""
    result = await db.execute(
        select(OnboardingSubmission).filter(OnboardingSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    
    if not submission:
        return None
    
    submission.payment_intent_id = payment_intent_id
    submission.payment_status = payment_status
    
    # Auto-update status to in-progress when paid
    if payment_status == "paid":
        submission.status = "in-progress"
    
    await db.commit()
    await db.refresh(submission)
    
    return submission
