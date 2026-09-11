import calendar
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Booking, BookingItem, BookingStatus, ItemCategory

CLOSED_STATUSES = [BookingStatus.RETURNED, BookingStatus.DAMAGED]
OPEN_STATUSES = [BookingStatus.ACTIVE, BookingStatus.DUE, BookingStatus.OVERDUE]


def get_summary(db: Session, business_id) -> dict:
    today = date.today()
    month_start = today.replace(day=1)

    bookings_this_month = (
        db.query(Booking)
        .filter(
            Booking.business_id == business_id,
            Booking.pickup_date >= month_start,
            Booking.is_deleted.is_(False),
        )
        .all()
    )
    revenue = sum(b.price for b in bookings_this_month)

    active_rentals = (
        db.query(Booking)
        .filter(
            Booking.business_id == business_id,
            Booking.status.in_(OPEN_STATUSES),
            Booking.is_deleted.is_(False),
        )
        .count()
    )

    rows = (
        db.query(BookingItem.category_id, func.count(BookingItem.booking_item_id).label("cnt"))
        .join(Booking)
        .filter(Booking.business_id == business_id, Booking.is_deleted.is_(False))
        .group_by(BookingItem.category_id)
        .order_by(func.count(BookingItem.booking_item_id).desc())
        .limit(5)
        .all()
    )
    top_categories = []
    for category_id, cnt in rows:
        category = db.get(ItemCategory, category_id)
        if category is None:
            continue
        top_categories.append({"category_id": category_id, "name": category.item_name, "icon": category.icon, "count": cnt})
    most_rented_category = top_categories[0]["name"] if top_categories else None

    thirty_days_ago = today - timedelta(days=30)
    closed = (
        db.query(Booking)
        .filter(
            Booking.business_id == business_id,
            Booking.status.in_(CLOSED_STATUSES),
            Booking.return_date >= thirty_days_ago,
            Booking.is_deleted.is_(False),
        )
        .all()
    )
    if not closed:
        closed = (
            db.query(Booking)
            .filter(
                Booking.business_id == business_id,
                Booking.status.in_(CLOSED_STATUSES),
                Booking.is_deleted.is_(False),
            )
            .all()
        )
    avg_duration = (
        sum((b.return_date - b.pickup_date).days for b in closed) / len(closed) if closed else 0.0
    )

    weekly_counts: dict[int, int] = {}
    for b in bookings_this_month:
        week_index = (b.pickup_date.day - 1) // 7 + 1
        weekly_counts[week_index] = weekly_counts.get(week_index, 0) + 1
    weeks_in_month = max(weekly_counts.keys(), default=0)
    weekly_bookings = [
        {"label": f"W{i}", "count": weekly_counts.get(i, 0)} for i in range(1, max(weeks_in_month, 4) + 1)
    ]

    return {
        "revenue": revenue,
        "revenue_label": f"Revenue · {calendar.month_name[today.month]}",
        "active_rentals": active_rentals,
        "most_rented_category": most_rented_category,
        "avg_rental_duration_days": round(avg_duration, 1),
        "weekly_bookings": weekly_bookings,
        "top_categories": top_categories,
    }
