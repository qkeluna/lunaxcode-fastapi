"""Onboarding question routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from api.database import get_db
from api.models.onboarding import OnboardingQuestion
from api.schemas.onboarding import OnboardingQuestionCreate, OnboardingQuestionUpdate, OnboardingQuestionResponse
from api.utils.auth import verify_api_key

router = APIRouter(prefix="/onboarding/questions", tags=["onboarding"])


@router.get("", response_model=List[OnboardingQuestionResponse])
async def get_all_questions(db: AsyncSession = Depends(get_db)):
    """Get all onboarding question sets (public)"""
    result = await db.execute(select(OnboardingQuestion))
    return result.scalars().all()


@router.get("/{service_type}", response_model=OnboardingQuestionResponse)
async def get_questions_for_service(service_type: str, db: AsyncSession = Depends(get_db)):
    """Get onboarding questions for specific service type (public)"""
    result = await db.execute(
        select(OnboardingQuestion).filter(OnboardingQuestion.service_type == service_type)
    )
    questions = result.scalar_one_or_none()

    if not questions:
        raise HTTPException(
            status_code=404,
            detail=f"No onboarding questions found for service type: {service_type}"
        )

    return questions


@router.post("", response_model=OnboardingQuestionResponse, status_code=201)
async def create_questions(
    questions: OnboardingQuestionCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create onboarding questions (admin)"""
    result = await db.execute(
        select(OnboardingQuestion).filter(OnboardingQuestion.service_type == questions.service_type)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Questions for service type {questions.service_type} already exist"
        )

    db_questions = OnboardingQuestion(**questions.model_dump())
    db.add(db_questions)
    await db.commit()
    await db.refresh(db_questions)
    return db_questions


@router.put("/{service_type}", response_model=OnboardingQuestionResponse)
async def update_questions(
    service_type: str,
    questions: OnboardingQuestionUpdate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update onboarding questions (admin)"""
    result = await db.execute(
        select(OnboardingQuestion).filter(OnboardingQuestion.service_type == service_type)
    )
    db_questions = result.scalar_one_or_none()

    if not db_questions:
        raise HTTPException(status_code=404, detail="Questions not found")

    for field, value in questions.model_dump(exclude_unset=True).items():
        setattr(db_questions, field, value)

    await db.commit()
    await db.refresh(db_questions)
    return db_questions


@router.delete("/{service_type}", status_code=204)
async def delete_questions(
    service_type: str,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete onboarding questions (admin)"""
    result = await db.execute(
        select(OnboardingQuestion).filter(OnboardingQuestion.service_type == service_type)
    )
    db_questions = result.scalar_one_or_none()

    if not db_questions:
        raise HTTPException(status_code=404, detail="Questions not found")

    await db.delete(db_questions)
    await db.commit()
    return None