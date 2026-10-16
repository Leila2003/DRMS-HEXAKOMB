from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import service.notification as notification_service
from database.database import get_db
from models import User
from schemas.notification import NotificationRead
from utils.security import require_business_member

router = APIRouter(prefix="/notifications", tags=["Business Admin", "Staff"])


@router.get("", response_model=List[NotificationRead])
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(require_business_member)):
    return notification_service.list_notifications(db, current_user.business_id)


@router.post("/{notification_id}/read", response_model=NotificationRead)
def mark_notification_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_member),
):
    notification = notification_service.mark_read(db, notification_id, current_user.business_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification
