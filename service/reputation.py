from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models import Booking, BookingStatus, ItemCondition


def get_reputation(db: Session, customer_id: UUID) -> dict:
    total_bookings = (
        db.query(Booking)
        .filter(Booking.customer_id == customer_id, Booking.is_deleted.is_(False))
        .count()
    )

    if total_bookings == 0:
        return {
            "label": "New customer",
            "detail": "This customer hasn't made a booking yet.",
        }

    closed = (
        db.query(Booking)
        .filter(
            Booking.customer_id == customer_id,
            Booking.status.in_([BookingStatus.RETURNED, BookingStatus.DAMAGED]),
            Booking.is_deleted.is_(False),
        )
        .order_by(Booking.return_date.desc())
        .all()
    )

    if not closed:
        return {
            "label": "New customer",
            "detail": "No completed rentals yet — booking history is still being built.",
        }

    flagged = [b for b in closed if b.status == BookingStatus.DAMAGED]
    if flagged:
        last = flagged[0]
        missing = any(item.condition == ItemCondition.MISSING for item in last.items)
        word = "an item was reported missing" if missing else "an item was returned damaged"
        note: Optional[str] = next((i.condition_notes for i in last.items if i.condition_notes), None)
        count = f"{len(flagged)} flagged return" + ("s" if len(flagged) > 1 else "")
        detail = (
            f"{count}. Last time: {word}"
            + (f' — "{note}"' if note else "")
            + f" ({last.return_date.strftime('%d %b')})."
        )
        return {"label": "Bad reputation", "detail": detail}

    last = closed[0]
    detail = (
        f"{len(closed)} rental" + ("s" if len(closed) > 1 else "")
        + f" returned in good condition — last on {last.return_date.strftime('%d %b')}."
    )
    return {"label": "Good history", "detail": detail}
