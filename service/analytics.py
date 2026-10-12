import calendar
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Booking, BookingItem, BookingStatus, ItemCategory
from models.booking import CautionOutcome

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

    # Revenue figures count item amounts only (Booking.price). Caution is a
    # refundable deposit, so it is reported on its own and never added in.
    base = db.query(Booking).filter(Booking.business_id == business_id, Booking.is_deleted.is_(False))
    total_revenue = base.with_entities(func.coalesce(func.sum(Booking.price), 0)).scalar()
    revenue_gained = (
        base.filter(Booking.status.in_(CLOSED_STATUSES))
        .with_entities(func.coalesce(func.sum(Booking.price), 0))
        .scalar()
    )
    caution_held = (
        base.filter(Booking.status.in_(OPEN_STATUSES))
        .with_entities(func.coalesce(func.sum(Booking.caution), 0))
        .scalar()
    )
    caution_refunded = (
        base.filter(Booking.caution_outcome == CautionOutcome.REFUNDED)
        .with_entities(func.coalesce(func.sum(Booking.caution), 0))
        .scalar()
    )
    caution_kept = (
        base.filter(Booking.caution_outcome == CautionOutcome.KEPT)
        .with_entities(func.coalesce(func.sum(Booking.caution), 0))
        .scalar()
    )

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

    # Real Monday-Sunday calendar weeks (not "weeks of this month"), trailing
    # 6 weeks including the current one.
    WEEKS_TO_SHOW = 6
    current_week_start = today - timedelta(days=today.weekday())
    week_starts = [current_week_start - timedelta(weeks=i) for i in range(WEEKS_TO_SHOW - 1, -1, -1)]
    range_end = current_week_start + timedelta(days=6)

    bookings_in_range = (
        db.query(Booking)
        .filter(
            Booking.business_id == business_id,
            Booking.pickup_date >= week_starts[0],
            Booking.pickup_date <= range_end,
            Booking.is_deleted.is_(False),
        )
        .all()
    )
    weekly_counts = {ws: 0 for ws in week_starts}
    for b in bookings_in_range:
        week_start = b.pickup_date - timedelta(days=b.pickup_date.weekday())
        if week_start in weekly_counts:
            weekly_counts[week_start] += 1

    weekly_bookings = [
        {
            "label": "This week" if ws == current_week_start else f"{ws.strftime('%b')} {ws.day}",
            "count": weekly_counts[ws],
        }
        for ws in week_starts
    ]

    return {
        "revenue": revenue,
        "revenue_label": f"Revenue · {calendar.month_name[today.month]}",
        "total_revenue": total_revenue,
        "revenue_gained": revenue_gained,
        "caution_held": caution_held,
        "caution_refunded": caution_refunded,
        "caution_kept": caution_kept,
        "active_rentals": active_rentals,
        "most_rented_category": most_rented_category,
        "avg_rental_duration_days": round(avg_duration, 1),
        "weekly_bookings": weekly_bookings,
        "top_categories": top_categories,
    }
