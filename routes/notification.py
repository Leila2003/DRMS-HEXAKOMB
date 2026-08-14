from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import service.notification as notification_service
from database.database import get_db
from models import User
from schemas.notification import NotificationRead
from utils.security import get_current_user

router = APIRouter(prefix="/notifications", tags=["Admin", "Staff"])


@router.get("", response_model=List[NotificationRead])
def list_notifications(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return notification_service.list_notifications(db)


@router.post("/{notification_id}/read", response_model=NotificationRead)
def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    notification = notification_service.mark_read(db, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification
