"""Onboarding submission routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from api.database import get_db
from api.schemas.onboarding_submission import (
    OnboardingSubmissionCreate,
    OnboardingSubmissionResponse,
    OnboardingSubmissionDetail,
    AdminSubmissionUpdate
)
from api.services.onboarding_service import (
    create_onboarding_submission,
    get_submission_by_id,
    get_submissions,
    update_submission_status
)
from api.utils.auth import verify_api_key

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("/submit", response_model=OnboardingSubmissionResponse, status_code=201)
async def submit_onboarding(
    submission: OnboardingSubmissionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit onboarding form (public endpoint)
    
    This endpoint:
    1. Validates submission data
    2. Saves to database with status 'pending'
    3. Returns submission ID for tracking
    4. TODO: Create Stripe checkout session and return payment URL
    5. TODO: Send email notifications
    """
    try:
        db_submission = await create_onboarding_submission(submission, db)
        
        # TODO: Create Stripe checkout session
        # payment_url = await create_stripe_checkout(db_submission)
        
        # TODO: Send email notifications
        # await send_customer_confirmation(db_submission)
        # await send_admin_notification(db_submission)
        
        return OnboardingSubmissionResponse(
            success=True,
            submission_id=db_submission.id,
            payment_url=None,  # Will be Stripe checkout URL
            message="Submission received successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/submissions", response_model=List[OnboardingSubmissionDetail])
async def list_submissions(
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """List all onboarding submissions (admin only)"""
    submissions = await get_submissions(db, status=status, skip=skip, limit=limit)
    return submissions


@router.get("/submissions/{submission_id}", response_model=OnboardingSubmissionDetail)
async def get_submission(
    submission_id: UUID,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get submission details (admin only)"""
    submission = await get_submission_by_id(submission_id, db)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@router.patch("/submissions/{submission_id}/status", response_model=OnboardingSubmissionDetail)
async def update_submission(
    submission_id: UUID,
    update_data: AdminSubmissionUpdate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update submission status (admin only)"""
    submission = await update_submission_status(submission_id, update_data, db)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission
