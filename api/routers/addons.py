"""Add-on routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from api.database import get_db
from api.models.addon import Addon
from api.schemas.addon import AddonCreate, AddonUpdate, AddonResponse
from api.utils.auth import verify_api_key

router = APIRouter(prefix="/addons", tags=["addons"])


@router.get("", response_model=List[AddonResponse])
async def get_addons(db: AsyncSession = Depends(get_db)):
    """Get all add-ons (public)"""
    result = await db.execute(select(Addon))
    return result.scalars().all()


@router.get("/{addon_id}", response_model=AddonResponse)
async def get_addon(addon_id: int, db: AsyncSession = Depends(get_db)):
    """Get specific add-on (public)"""
    result = await db.execute(select(Addon).filter(Addon.id == addon_id))
    addon = result.scalar_one_or_none()
    if not addon:
        raise HTTPException(status_code=404, detail="Add-on not found")
    return addon


@router.post("", response_model=AddonResponse, status_code=201)
async def create_addon(
    addon: AddonCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create add-on (admin)"""
    db_addon = Addon(**addon.model_dump())
    db.add(db_addon)
    await db.commit()
    await db.refresh(db_addon)
    return db_addon


@router.put("/{addon_id}", response_model=AddonResponse)
async def update_addon(
    addon_id: int,
    addon: AddonUpdate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update add-on (admin)"""
    result = await db.execute(select(Addon).filter(Addon.id == addon_id))
    db_addon = result.scalar_one_or_none()
    if not db_addon:
        raise HTTPException(status_code=404, detail="Add-on not found")

    for field, value in addon.model_dump(exclude_unset=True).items():
        setattr(db_addon, field, value)

    await db.commit()
    await db.refresh(db_addon)
    return db_addon


@router.delete("/{addon_id}", status_code=204)
async def delete_addon(
    addon_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete add-on (admin)"""
    result = await db.execute(select(Addon).filter(Addon.id == addon_id))
    db_addon = result.scalar_one_or_none()
    if not db_addon:
        raise HTTPException(status_code=404, detail="Add-on not found")

    await db.delete(db_addon)
    await db.commit()
    return None