from datetime import datetime, timezone
from typing import List, Optional, Tuple

from fastapi import UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session

from models import Booking, Customer
from schemas.customer import CustomerCreate, CustomerUpdate
from utils.file_storage import save_customer_national_id_photo


def create_customer(db: Session, payload: CustomerCreate) -> Customer:
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def list_customers(
    db: Session,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[List[Customer], int]:
    query = db.query(Customer).filter(Customer.deleted_at.is_(None))
    if search:
        like = f"%{search}%"
        digits = "".join(ch for ch in search if ch.isdigit())
        conditions = [Customer.name.ilike(like)]
        if digits:
            conditions.append(Customer.contact.ilike(f"%{digits}%"))
        query = query.filter(or_(*conditions))

    total = query.count()
    customers = (
        query.order_by(Customer.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return customers, total


def get_customer_bookings(db: Session, customer_id: str) -> List[Booking]:
    return (
        db.query(Booking)
        .filter(Booking.customer_id == customer_id, Booking.is_deleted.is_(False))
        .order_by(Booking.pickup_date.desc())
        .all()
    )


def get_customer(db: Session, customer_id: str) -> Optional[Customer]:
    customer = db.get(Customer, customer_id)
    if customer is None or customer.deleted_at is not None:
        return None
    return customer


def find_customer_by_contact(db: Session, contact: str) -> Optional[Customer]:
    return (
        db.query(Customer)
        .filter(Customer.contact == contact, Customer.deleted_at.is_(None))
        .first()
    )


def update_customer(
    db: Session, customer_id: str, payload: CustomerUpdate
) -> Optional[Customer]:
    customer = get_customer(db, customer_id)
    if customer is None:
        return None

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer


def upload_national_id_photo(
    db: Session, customer_id: str, file: UploadFile
) -> Optional[Customer]:
    customer = get_customer(db, customer_id)
    if customer is None:
        return None

    customer.nationalID_Photo = save_customer_national_id_photo(customer_id, file)
    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db: Session, customer_id: str) -> bool:
    customer = get_customer(db, customer_id)
    if customer is None:
        return False

    customer.is_deleted = True
    customer.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True
