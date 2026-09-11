from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models import ItemCategory, Notification, NotificationGroup, NotificationType


def create_notification(
    db: Session,
    business_id: UUID,
    type: NotificationType,
    group: NotificationGroup,
    title: str,
    body: str,
    booking_id: Optional[UUID] = None,
    category_id: Optional[UUID] = None,
) -> Notification:
    notification = Notification(
        business_id=business_id,
        type=type,
        group=group,
        title=title,
        body=body,
        booking_id=booking_id,
        category_id=category_id,
    )
    db.add(notification)
    db.flush()
    return notification


def notify_low_stock(db: Session, category: ItemCategory) -> Notification:
    return create_notification(
        db,
        business_id=category.business_id,
        type=NotificationType.WARN,
        group=NotificationGroup.LOW_STOCK,
        title=f"Low stock: {category.item_name}",
        body=f"Only {category.quantity_available} available (threshold: 3).",
        category_id=category.category_id,
    )


def list_notifications(db: Session, business_id: UUID) -> List[Notification]:
    return (
        db.query(Notification)
        .filter(Notification.business_id == business_id, Notification.is_deleted.is_(False))
        .order_by(Notification.created_at.desc())
        .all()
    )


def get_notification(db: Session, notification_id: UUID, business_id: UUID) -> Optional[Notification]:
    notification = db.get(Notification, notification_id)
    if notification is None or notification.is_deleted or notification.business_id != business_id:
        return None
    return notification


def mark_read(db: Session, notification_id: UUID, business_id: UUID) -> Optional[Notification]:
    notification = get_notification(db, notification_id, business_id)
    if notification is None:
        return None
    notification.read = True
    db.commit()
    db.refresh(notification)
    return notification
