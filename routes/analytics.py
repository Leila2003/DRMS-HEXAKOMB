from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import service.analytics as analytics_service
import service.business as business_service
from database.database import get_db
from models import User
from schemas.analytics import AnalyticsSummary, PlatformAnalyticsSummary
from utils.security import require_business_admin, require_super_admin

router = APIRouter(prefix="/analytics")


@router.get("/summary", response_model=AnalyticsSummary, tags=["Business Admin"])
def get_analytics_summary(db: Session = Depends(get_db), _user: User = Depends(require_business_admin)):
    
    if _user.business_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is not attached to a business",
        )
    return analytics_service.get_summary(db, _user.business_id)


@router.get("/platform", response_model=PlatformAnalyticsSummary, tags=["Super Admin"])
def get_platform_analytics(db: Session = Depends(get_db), _admin: User = Depends(require_super_admin)):
    
    return business_service.get_platform_summary(db)
