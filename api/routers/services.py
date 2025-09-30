"""Service routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from api.database import get_db
from api.models.service import Service
from api.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from api.utils.auth import verify_api_key

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=List[ServiceResponse])
async def get_services(db: AsyncSession = Depends(get_db)):
    """Get all services (public)"""
    result = await db.execute(select(Service))
    return result.scalars().all()


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: str, db: AsyncSession = Depends(get_db)):
    """Get specific service (public)"""
    result = await db.execute(select(Service).filter(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("", response_model=ServiceResponse, status_code=201)
async def create_service(
    service: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create service (admin)"""
    result = await db.execute(select(Service).filter(Service.id == service.id))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Service with this ID already exists")

    db_service = Service(**service.model_dump())
    db.add(db_service)
    await db.commit()
    await db.refresh(db_service)
    return db_service


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: str,
    service: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update service (admin)"""
    result = await db.execute(select(Service).filter(Service.id == service_id))
    db_service = result.scalar_one_or_none()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")

    for field, value in service.model_dump(exclude_unset=True).items():
        setattr(db_service, field, value)

    await db.commit()
    await db.refresh(db_service)
    return db_service


@router.delete("/{service_id}", status_code=204)
async def delete_service(
    service_id: str,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete service (admin)"""
    result = await db.execute(select(Service).filter(Service.id == service_id))
    db_service = result.scalar_one_or_none()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")

    await db.delete(db_service)
    await db.commit()
    return None