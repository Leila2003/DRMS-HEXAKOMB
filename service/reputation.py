from typing import Optional

from sqlalchemy.orm import Session

from models import Booking, BookingStatus, ItemCondition


def get_reputation(db: Session, customer_id: int) -> dict:
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
            "class": "rep-new",
            "icon": "🆕",
            "label": "New customer",
            "detail": "No completed rentals yet — this will be their first.",
        }

    flagged = [b for b in closed if b.status == BookingStatus.DAMAGED]
    if flagged:
        last = flagged[0]
        missing = any(item.condition == ItemCondition.MISSING for item in last.items)
        word = "item reported missing" if missing else "returned damaged"
        note: Optional[str] = next((i.condition_notes for i in last.items if i.condition_notes), None)
        label = f"{len(flagged)} flagged return" + ("s" if len(flagged) > 1 else "")
        detail = f"Last time: {word}" + (f' — "{note}"' if note else "") + f" ({last.return_date.strftime('%d %b')})."
        return {"class": "rep-flag", "icon": "⚠️", "label": label, "detail": detail}

    last = closed[0]
    label = "Good history"
    detail = (
        f"{len(closed)} rental" + ("s" if len(closed) > 1 else "")
        + f" returned in good condition — last on {last.return_date.strftime('%d %b')}."
    )
    return {"class": "rep-good", "icon": "✅", "label": label, "detail": detail}
