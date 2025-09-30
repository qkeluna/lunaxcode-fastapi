"""Pricing plan routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from api.database import get_db
from api.models.pricing import PricingPlan
from api.schemas.pricing import PricingPlanCreate, PricingPlanUpdate, PricingPlanResponse
from api.utils.auth import verify_api_key

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("", response_model=List[PricingPlanResponse])
async def get_pricing_plans(db: AsyncSession = Depends(get_db)):
    """Get all pricing plans (public)"""
    result = await db.execute(select(PricingPlan))
    return result.scalars().all()


@router.get("/{plan_id}", response_model=PricingPlanResponse)
async def get_pricing_plan(plan_id: str, db: AsyncSession = Depends(get_db)):
    """Get specific pricing plan (public)"""
    result = await db.execute(select(PricingPlan).filter(PricingPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Pricing plan not found")
    return plan


@router.post("", response_model=PricingPlanResponse, status_code=201)
async def create_pricing_plan(
    plan: PricingPlanCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create pricing plan (admin)"""
    # Check if ID already exists
    result = await db.execute(select(PricingPlan).filter(PricingPlan.id == plan.id))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Pricing plan with this ID already exists")

    db_plan = PricingPlan(**plan.model_dump())
    db.add(db_plan)
    await db.commit()
    await db.refresh(db_plan)
    return db_plan


@router.put("/{plan_id}", response_model=PricingPlanResponse)
async def update_pricing_plan(
    plan_id: str,
    plan: PricingPlanUpdate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update pricing plan (admin)"""
    result = await db.execute(select(PricingPlan).filter(PricingPlan.id == plan_id))
    db_plan = result.scalar_one_or_none()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Pricing plan not found")

    # Update fields
    for key, value in plan.model_dump(exclude_unset=True).items():
        setattr(db_plan, key, value)

    await db.commit()
    await db.refresh(db_plan)
    return db_plan


@router.delete("/{plan_id}", status_code=204)
async def delete_pricing_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete pricing plan (admin)"""
    result = await db.execute(select(PricingPlan).filter(PricingPlan.id == plan_id))
    db_plan = result.scalar_one_or_none()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Pricing plan not found")

    await db.delete(db_plan)
    await db.commit()
    return None