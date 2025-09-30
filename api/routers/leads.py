"""Lead routes with dual data storage"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from api.database import get_db
from api.schemas.lead import LeadCreate, LeadUpdate, LeadResponse
from api.services.lead_service import create_lead, get_lead, get_leads, update_lead, delete_lead
from api.utils.auth import verify_api_key

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadResponse, status_code=201)
async def submit_lead(lead: LeadCreate, db: AsyncSession = Depends(get_db)):
    """
    Submit new lead (public endpoint).

    This endpoint implements dual data storage:
    - Stores structured answers (JSONB) for queries
    - Auto-generates AI-formatted prompt (TEXT) for LLM processing
    """
    try:
        return await create_lead(lead, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[LeadResponse])
async def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None, pattern="^(new|contacted|converted|rejected)$"),
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get all leads with optional filtering (admin only)"""
    return await get_leads(db, skip=skip, limit=limit, status=status)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead_by_id(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get specific lead (admin only)"""
    try:
        return await get_lead(lead_id, db)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead_status(
    lead_id: int,
    lead_update: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update lead status (admin only)"""
    try:
        return await update_lead(lead_id, lead_update, db)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{lead_id}", status_code=204)
async def delete_lead_by_id(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete lead (admin only)"""
    try:
        await delete_lead(lead_id, db)
        return None
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))