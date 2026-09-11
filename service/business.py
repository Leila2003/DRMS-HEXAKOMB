from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from models import Booking, BookingStatus, Business, User, UserRole


def _to_dict(db: Session, business: Business) -> dict:
    owner = (
        db.query(User)
        .filter(User.business_id == business.business_id, User.role == UserRole.BUSINESS_ADMIN)
        .first()
    )
    staff_count = (
        db.query(User)
        .filter(
            User.business_id == business.business_id,
            User.role == UserRole.STAFF,
            User.is_deleted.is_(False),
        )
        .count()
    )
    return {
        "business_id": business.business_id,
        "name": business.name,
        "phone": business.phone,
        "is_active": business.is_active,
        "created_at": business.created_at,
        "owner_name": owner.name if owner else None,
        "owner_email": owner.email if owner else None,
        "staff_count": staff_count,
    }


def list_businesses(db: Session) -> List[dict]:
    businesses = db.query(Business).order_by(Business.name).all()
    return [_to_dict(db, b) for b in businesses]


def get_business(db: Session, business_id: UUID) -> Optional[dict]:
    business = db.get(Business, business_id)
    if business is None:
        return None
    return _to_dict(db, business)


def deactivate_business(db: Session, business_id: UUID) -> Optional[dict]:
    business = db.get(Business, business_id)
    if business is None:
        return None
    business.is_deleted = True
    business.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(business)
    return _to_dict(db, business)


def reactivate_business(db: Session, business_id: UUID) -> Optional[dict]:
    business = db.get(Business, business_id)
    if business is None:
        return None
    business.is_deleted = False
    business.deleted_at = None
    db.commit()
    db.refresh(business)
    return _to_dict(db, business)


OPEN_STATUSES = [BookingStatus.ACTIVE, BookingStatus.DUE, BookingStatus.OVERDUE]


def get_platform_summary(db: Session) -> dict:
    total_businesses = db.query(Business).count()
    active_businesses = db.query(Business).filter(Business.is_deleted.is_(False)).count()
    total_staff = (
        db.query(User).filter(User.role == UserRole.STAFF, User.is_deleted.is_(False)).count()
    )
    total_bookings = db.query(Booking).filter(Booking.is_deleted.is_(False)).count()
    total_revenue = (
        db.query(func.coalesce(func.sum(Booking.price), 0))
        .filter(Booking.is_deleted.is_(False))
        .scalar()
    )
    active_rentals = (
        db.query(Booking)
        .filter(Booking.status.in_(OPEN_STATUSES), Booking.is_deleted.is_(False))
        .count()
    )

    rows = (
        db.query(
            Business.business_id,
            Business.name,
            func.count(Booking.booking_id).label("bookings_count"),
            func.coalesce(func.sum(Booking.price), 0).label("revenue"),
        )
        .outerjoin(Booking, and_(Booking.business_id == Business.business_id, Booking.is_deleted.is_(False)))
        .filter(Business.is_deleted.is_(False))
        .group_by(Business.business_id, Business.name)
        .order_by(func.count(Booking.booking_id).desc())
        .limit(10)
        .all()
    )
    top_businesses = [
        {"business_id": r.business_id, "name": r.name, "bookings_count": r.bookings_count, "revenue": r.revenue}
        for r in rows
    ]

    return {
        "total_businesses": total_businesses,
        "active_businesses": active_businesses,
        "total_staff": total_staff,
        "total_bookings": total_bookings,
        "total_revenue": total_revenue,
        "active_rentals": active_rentals,
        "top_businesses": top_businesses,
    }
