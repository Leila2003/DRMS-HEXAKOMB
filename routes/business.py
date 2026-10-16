from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import service.business as business_service
from database.database import get_db
from models import User
from schemas.business import BusinessAdminRead
from utils.security import require_super_admin

PLATFORM_ONLY = ["Super Admin"]

router = APIRouter(prefix="/businesses", tags=PLATFORM_ONLY)


@router.get("", response_model=List[BusinessAdminRead])
def list_businesses(db: Session = Depends(get_db), _admin: User = Depends(require_super_admin)):
    return business_service.list_businesses(db)


@router.get("/{business_id}", response_model=BusinessAdminRead)
def get_business(
    business_id: UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    business = business_service.get_business(db, business_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return business


@router.patch("/{business_id}/deactivate", response_model=BusinessAdminRead)
def deactivate_business(
    business_id: UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    
    business = business_service.deactivate_business(db, business_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return business


@router.patch("/{business_id}/reactivate", response_model=BusinessAdminRead)
def reactivate_business(
    business_id: UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    business = business_service.reactivate_business(db, business_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return business
