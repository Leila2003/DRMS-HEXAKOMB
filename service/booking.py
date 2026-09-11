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
from schemas.booking import BookingCreate, ReturnRequest

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


def process_return(
    db: Session, booking_id: UUID, business_id: UUID, payload: ReturnRequest, user_id: UUID
) -> Optional[Booking]:
    booking = get_booking(db, booking_id, business_id, refresh=False)
    if booking is None:
        return None
    if booking.status in (BookingStatus.RETURNED, BookingStatus.DAMAGED):
        raise BookingError("This booking has already been returned")

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
