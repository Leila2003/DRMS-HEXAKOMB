from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Booking, BookingStatus, Customer
from schemas.customer import CustomerCreate, CustomerUpdate
from utils.file_storage import save_customer_national_id_photo


def create_customer(db: Session, payload: CustomerCreate, business_id: UUID) -> Customer:
    customer = Customer(business_id=business_id, **payload.model_dump())
    db.add(customer)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("A customer with this contact already exists") from exc
    db.refresh(customer)
    return customer


def list_customers(db: Session, business_id: UUID) -> List[Customer]:
    return (
        db.query(Customer)
        .filter(Customer.business_id == business_id, Customer.deleted_at.is_(None))
        .order_by(Customer.name)
        .all()
    )


def get_customer_bookings(db: Session, customer_id: UUID, business_id: UUID) -> List[Booking]:
    return (
        db.query(Booking)
        .filter(
            Booking.customer_id == customer_id,
            Booking.business_id == business_id,
            Booking.is_deleted.is_(False),
        )
        .order_by(Booking.pickup_date.desc())
        .all()
    )


def get_customer(db: Session, customer_id: UUID, business_id: UUID) -> Optional[Customer]:
    customer = db.get(Customer, customer_id)
    if customer is None or customer.deleted_at is not None or customer.business_id != business_id:
        return None
    return customer


def find_customer_by_contact(db: Session, contact: str, business_id: UUID) -> Optional[Customer]:
    return (
        db.query(Customer)
        .filter(
            Customer.contact == contact,
            Customer.business_id == business_id,
            Customer.deleted_at.is_(None),
        )
        .first()
    )


def update_customer(
    db: Session, customer_id: UUID, business_id: UUID, payload: CustomerUpdate
) -> Optional[Customer]:
    customer = get_customer(db, customer_id, business_id)
    if customer is None:
        return None

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("A customer with this contact already exists") from exc
    db.refresh(customer)
    return customer


def upload_national_id_photo(
    db: Session, customer_id: UUID, business_id: UUID, file: UploadFile
) -> Optional[Customer]:
    customer = get_customer(db, customer_id, business_id)
    if customer is None:
        return None

    customer.nationalID_Photo = save_customer_national_id_photo(customer_id, file)
    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db: Session, customer_id: UUID, business_id: UUID) -> bool:
    customer = get_customer(db, customer_id, business_id)
    if customer is None:
        return False

    open_bookings = (
        db.query(Booking)
        .filter(
            Booking.customer_id == customer_id,
            Booking.business_id == business_id,
            Booking.is_deleted.is_(False),
            Booking.status.in_([BookingStatus.ACTIVE, BookingStatus.DUE, BookingStatus.OVERDUE]),
        )
        .count()
    )
    if open_bookings:
        raise ValueError("This customer has open bookings; process their returns before deleting")

    customer.is_deleted = True
    customer.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True
