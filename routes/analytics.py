from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import service.analytics as analytics_service
from database.database import get_db
from models import User
from schemas.analytics import AnalyticsSummary
from utils.security import require_admin

router = APIRouter(prefix="/analytics", tags=["Admin"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary(db: Session = Depends(get_db), _user: User = Depends(require_admin)):
    return analytics_service.get_summary(db)
