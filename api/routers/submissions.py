"""Submission status check routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from api.database import get_db
from api.schemas.onboarding_submission import SubmissionStatusResponse
from api.services.onboarding_service import get_submission_by_id

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.get("/{submission_id}/status", response_model=SubmissionStatusResponse)
async def get_submission_status(
    submission_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Check submission status (public endpoint)
    
    Allows customers to check their submission status without authentication
    """
    submission = await get_submission_by_id(submission_id, db)
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Build status updates timeline from submission_metadata
    updates = []
    if submission.submission_metadata and "admin_notes" in submission.submission_metadata:
        for note in submission.submission_metadata["admin_notes"]:
            updates.append({
                "timestamp": note.get("timestamp"),
                "status": submission.status,
                "message": note.get("note")
            })
    
    return SubmissionStatusResponse(
        submission_id=submission.id,
        status=submission.status,
        payment_status=submission.payment_status,
        created_at=submission.created_at,
        estimated_completion=None,  # Calculate based on service type and timeline
        updates=updates
    )
