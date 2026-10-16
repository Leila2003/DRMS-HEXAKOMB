from collections import Counter, OrderedDict
from datetime import date, datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

import service.category as category_service
import service.customer as customer_service
import service.notification as notification_service
from models import (
    Booking,
    BookingItem,
    BookingStatus,
    ItemCondition,
    NotificationGroup,
    NotificationType,
)
from schemas.booking import BookingCreate, BookingUpdate, ReturnRequest

DUE_SOON_DAYS = 2


class BookingError(Exception):
    """Raised for booking business-rule violations; routes map this to HTTP 400."""


def _grouped_items(booking: Booking) -> List[dict]:
    grouped: "OrderedDict[int, dict]" = OrderedDict()
    for item in booking.items:
        entry = grouped.setdefault(
            item.category_id,
            {
                "category_id": item.category_id,
                "category_name": item.category.item_name,
                "icon": item.category.icon,
                "quantity": 0,
                "subtotal": 0,
            },
        )
        entry["quantity"] += item.quantity
        entry["subtotal"] += item.unit_price * item.quantity
    return list(grouped.values())


def to_booking_dict(booking: Booking) -> dict:
    return {
        "booking_id": booking.booking_id,
        "customer": booking.customer,
        "event_date": booking.event_date,
        "pickup_date": booking.pickup_date,
        "return_date": booking.return_date,
        "price": booking.price,
        "caution": booking.caution,
        "total_amount": booking.price + booking.caution,
        "caution_outcome": booking.caution_outcome,
        "status": booking.status,
        "lines": booking.items,
        "items": _grouped_items(booking),
        "created_at": booking.created_at,
    }


def to_booking_list_dict(booking: Booking) -> dict:
    return {
        "booking_id": booking.booking_id,
        "customer": booking.customer,
        "event_date": booking.event_date,
        "pickup_date": booking.pickup_date,
        "return_date": booking.return_date,
        "price": booking.price,
        "caution": booking.caution,
        "total_amount": booking.price + booking.caution,
        "caution_outcome": booking.caution_outcome,
        "status": booking.status,
        "items": _grouped_items(booking),
    }


def refresh_all_statuses(db: Session, business_id: UUID) -> None:
    today = date.today()
    open_bookings = (
        db.query(Booking)
        .filter(
            Booking.business_id == business_id,
            Booking.status.in_([BookingStatus.ACTIVE, BookingStatus.DUE, BookingStatus.OVERDUE]),
            Booking.is_deleted.is_(False),
        )
        .all()
    )
    for booking in open_bookings:
        days_left = (booking.return_date - today).days
        if days_left < 0:
            new_status = BookingStatus.OVERDUE
        elif days_left <= DUE_SOON_DAYS:
            new_status = BookingStatus.DUE
        else:
            new_status = BookingStatus.ACTIVE

        if new_status == booking.status:
            continue
        booking.status = new_status

        if new_status == BookingStatus.DUE:
            notification_service.create_notification(
                db,
                business_id=business_id,
                type=NotificationType.WARN,
                group=NotificationGroup.UPCOMING_RETURNS,
                title="Return due soon" if days_left > 0 else "Return due today",
                body=f"{booking.customer.name} — return due {booking.return_date.isoformat()}.",
                booking_id=booking.booking_id,
            )
        elif new_status == BookingStatus.OVERDUE:
            notification_service.create_notification(
                db,
                business_id=business_id,
                type=NotificationType.ALERT,
                group=NotificationGroup.OVERDUE,
                title="Rental overdue",
                body=f"{booking.customer.name} — return was due {booking.return_date.isoformat()}.",
                booking_id=booking.booking_id,
            )
    db.commit()


def create_booking(db: Session, payload: BookingCreate, user_id: UUID, business_id: UUID) -> Booking:
    if payload.customer_id is not None:
        customer = customer_service.get_customer(db, payload.customer_id, business_id)
        if customer is None:
            raise BookingError("Customer not found")
    else:
        existing = customer_service.find_customer_by_contact(db, payload.new_customer.contact, business_id)
        if existing is not None:
            customer = existing
        else:
            try:
                customer = customer_service.create_customer(db, payload.new_customer, business_id)
            except ValueError as exc:
                raise BookingError(str(exc)) from exc

    booking.caution_outcome = payload.caution_outcome if booking.caution > 0 else None

    counts: Counter = Counter()
    for line in payload.items:
        counts[line.category_id] += line.quantity
    categories = {}
    for category_id, qty in counts.items():
        category = category_service.get_category(db, category_id, business_id)
        if category is None:
            raise BookingError(f"Category {category_id} not found")
        if qty > category.quantity_available:
            raise BookingError(f"Only {category.quantity_available} available in {category.item_name}")
        categories[category_id] = category
        
        # total Price

    total_price = sum(line.unit_price * line.quantity for line in payload.items)

    booking = Booking(
        business_id=business_id,
        customer_id=customer.customer_id,
        user_id=user_id,
        pickup_date=payload.pickup_date,
        event_date=payload.event_date,
        return_date=payload.return_date,
        price=total_price,
        caution=payload.caution,
        status=BookingStatus.ACTIVE,
    )
    db.add(booking)
    db.flush()

    for line in payload.items:
        db.add(
            BookingItem(
                booking_id=booking.booking_id,
                category_id=line.category_id,
                quantity=line.quantity,
                unit_price=line.unit_price,
            )
        )

    for category_id, qty in counts.items():
        category = categories[category_id]
        category_service.adjust_rented(category, qty)
        if category_service.is_low_stock(category):
            notification_service.notify_low_stock(db, category)

    db.commit()
    db.refresh(booking)
    return booking


def list_bookings(db: Session, business_id: UUID) -> List[Booking]:
    refresh_all_statuses(db, business_id)

    return (
        db.query(Booking)
        .filter(Booking.business_id == business_id, Booking.is_deleted.is_(False))
        .order_by(Booking.pickup_date.desc(), Booking.booking_id.desc())
        .all()
    )


def get_booking(db: Session, booking_id: UUID, business_id: UUID, refresh: bool = True) -> Optional[Booking]:
    if refresh:
        refresh_all_statuses(db, business_id)
    booking = db.get(Booking, booking_id)
    if booking is None or booking.is_deleted or booking.business_id != business_id:
        return None
    return booking


OPEN_STATUSES = (BookingStatus.ACTIVE, BookingStatus.DUE, BookingStatus.OVERDUE)


def update_booking(
    db: Session, booking_id: UUID, business_id: UUID, payload: BookingUpdate
) -> Optional[Booking]:
    booking = get_booking(db, booking_id, business_id, refresh=False)
    if booking is None:
        return None
    if booking.status not in OPEN_STATUSES:
        raise BookingError("Only open bookings can be edited")

    changes = payload.model_dump(exclude_unset=True)
    pickup_date = changes.get("pickup_date") or booking.pickup_date
    return_date = changes.get("return_date") or booking.return_date
    if return_date < pickup_date:
        raise BookingError("Return date must be on or after the pickup date")

    for field in ("event_date", "pickup_date", "return_date", "caution"):
        if field in changes and (changes[field] is not None or field == "event_date"):
            setattr(booking, field, changes[field])

    if payload.lines is not None:
        items_by_id = {item.booking_item_id: item for item in booking.items}
        deltas: Counter = Counter()
        for line in payload.lines:
            item = items_by_id.get(line.booking_item_id)
            if item is None:
                raise BookingError(f"Booking item {line.booking_item_id} not found")
            deltas[item.category_id] += line.quantity - item.quantity

        categories = {}
        for category_id, delta in deltas.items():
            category = category_service.get_category(db, category_id, business_id)
            if category is None:
                raise BookingError(f"Category {category_id} not found")
            if delta > category.quantity_available:
                raise BookingError(f"Only {category.quantity_available} more available in {category.item_name}")
            categories[category_id] = category

        for line in payload.lines:
            item = items_by_id[line.booking_item_id]
            item.quantity = line.quantity
            item.unit_price = line.unit_price

        for category_id, delta in deltas.items():
            if delta:
                category = categories[category_id]
                category_service.adjust_rented(category, delta)
                if delta > 0 and category_service.is_low_stock(category):
                    notification_service.notify_low_stock(db, category)

        booking.price = sum(item.unit_price * item.quantity for item in booking.items)

    db.commit()
    # Dates may have moved, so re-derive active/due/overdue.
    refresh_all_statuses(db, business_id)
    db.refresh(booking)
    return booking


def process_return(
    db: Session, booking_id: UUID, business_id: UUID, payload: ReturnRequest, user_id: UUID
) -> Optional[Booking]:
    booking = get_booking(db, booking_id, business_id, refresh=False)
    if booking is None:
        return None
    if booking.status in (BookingStatus.RETURNED, BookingStatus.DAMAGED):
        raise BookingError("This booking has already been returned")
    if booking.caution > 0 and payload.caution_outcome is None:
        raise BookingError("Choose whether the caution is refunded to the customer or kept")

    now = datetime.now(timezone.utc)
    for item in booking.items:
        item.condition = payload.condition
        item.condition_notes = payload.notes
        item.returned_at = now
        item.returned_by_id = user_id

    counts: Counter = Counter()
    for item in booking.items:
        counts[item.category_id] += item.quantity

    if payload.condition == ItemCondition.GOOD:
        booking.status = BookingStatus.RETURNED
        for category_id, qty in counts.items():
            category = category_service.get_category(db, category_id, business_id)
            category_service.adjust_rented(category, -qty)
    else:
        booking.status = BookingStatus.DAMAGED
        for category_id, qty in counts.items():
            category = category_service.get_category(db, category_id, business_id)
            category_service.write_off(category, qty)
        notification_service.create_notification(
            db,
            business_id=business_id,
            type=NotificationType.INFO,
            group=NotificationGroup.INVENTORY,
            title=f"Item flagged {payload.condition.value}",
            body=(
                f"{booking.customer.name} — items recorded as {payload.condition.value} at return."
                + (f" Note: {payload.notes}" if payload.notes else "")
            ),
            booking_id=booking.booking_id,
        )

    db.commit()
    db.refresh(booking)
    return booking
