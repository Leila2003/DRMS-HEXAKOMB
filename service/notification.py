from typing import List, Optional

from sqlalchemy.orm import Session

from models import ItemCategory, Notification, NotificationGroup, NotificationType


def create_notification(
    db: Session,
    type: NotificationType,
    group: NotificationGroup,
    title: str,
    body: str,
    booking_id: Optional[int] = None,
    category_id: Optional[int] = None,
) -> Notification:
    notification = Notification(
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
        type=NotificationType.WARN,
        group=NotificationGroup.LOW_STOCK,
        title=f"Low stock: {category.item_name}",
        body=f"Only {category.quantity_available} available (threshold: 3).",
        category_id=category.category_id,
    )


def list_notifications(db: Session) -> List[Notification]:
    return (
        db.query(Notification)
        .filter(Notification.is_deleted.is_(False))
        .order_by(Notification.created_at.desc())
        .all()
    )


def get_notification(db: Session, notification_id: int) -> Optional[Notification]:
    notification = db.get(Notification, notification_id)
    if notification is None or notification.is_deleted:
        return None
    return notification


def mark_read(db: Session, notification_id: int) -> Optional[Notification]:
    notification = get_notification(db, notification_id)
    if notification is None:
        return None
    notification.read = True
    db.commit()
    db.refresh(notification)
    return notification
