"""Feature routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from api.database import get_db
from api.models.feature import Feature
from api.schemas.feature import FeatureCreate, FeatureUpdate, FeatureResponse
from api.utils.auth import verify_api_key

router = APIRouter(prefix="/features", tags=["features"])


@router.get("", response_model=List[FeatureResponse])
async def get_features(db: AsyncSession = Depends(get_db)):
    """Get all features ordered by display_order (public)"""
    result = await db.execute(select(Feature).order_by(Feature.display_order))
    return result.scalars().all()


@router.get("/{feature_id}", response_model=FeatureResponse)
async def get_feature(feature_id: int, db: AsyncSession = Depends(get_db)):
    """Get specific feature (public)"""
    result = await db.execute(select(Feature).filter(Feature.id == feature_id))
    feature = result.scalar_one_or_none()
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature


@router.post("", response_model=FeatureResponse, status_code=201)
async def create_feature(
    feature: FeatureCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create feature (admin)"""
    db_feature = Feature(**feature.model_dump())
    db.add(db_feature)
    await db.commit()
    await db.refresh(db_feature)
    return db_feature


@router.put("/{feature_id}", response_model=FeatureResponse)
async def update_feature(
    feature_id: int,
    feature: FeatureUpdate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update feature (admin)"""
    result = await db.execute(select(Feature).filter(Feature.id == feature_id))
    db_feature = result.scalar_one_or_none()
    if not db_feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    for field, value in feature.model_dump(exclude_unset=True).items():
        setattr(db_feature, field, value)

    await db.commit()
    await db.refresh(db_feature)
    return db_feature


@router.delete("/{feature_id}", status_code=204)
async def delete_feature(
    feature_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete feature (admin)"""
    result = await db.execute(select(Feature).filter(Feature.id == feature_id))
    db_feature = result.scalar_one_or_none()
    if not db_feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    await db.delete(db_feature)
    await db.commit()
    return None