"""Company information routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.database import get_db
from api.models.company import CompanyInfo
from api.schemas.company import CompanyInfoUpdate, CompanyInfoResponse
from api.utils.auth import verify_api_key

router = APIRouter(prefix="/company", tags=["company"])


@router.get("", response_model=CompanyInfoResponse)
async def get_company_info(db: AsyncSession = Depends(get_db)):
    """Get company information (public)"""
    result = await db.execute(select(CompanyInfo).filter(CompanyInfo.id == 1))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company information not found")
    return company


@router.put("", response_model=CompanyInfoResponse)
async def update_company_info(
    company: CompanyInfoUpdate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update company information (admin)"""
    result = await db.execute(select(CompanyInfo).filter(CompanyInfo.id == 1))
    db_company = result.scalar_one_or_none()
    if not db_company:
        raise HTTPException(status_code=404, detail="Company information not found")

    for field, value in company.model_dump(exclude_unset=True).items():
        setattr(db_company, field, value)

    await db.commit()
    await db.refresh(db_company)
    return db_company