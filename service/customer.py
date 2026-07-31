from datetime import datetime, timezone
from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from models import Customer
from schemas.customer import CustomerCreate, CustomerUpdate
from utils.file_storage import save_customer_national_id_photo


def create_customer(db: Session, payload: CustomerCreate) -> Customer:
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def list_customers(db: Session) -> List[Customer]:
    return db.query(Customer).filter(Customer.deleted_at.is_(None)).all()


def get_customer(db: Session, customer_id: int) -> Optional[Customer]:
    customer = db.get(Customer, customer_id)
    if customer is None or customer.deleted_at is not None:
        return None
    return customer


def update_customer(
    db: Session, customer_id: int, payload: CustomerUpdate
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
    db: Session, customer_id: int, file: UploadFile
) -> Optional[Customer]:
    customer = get_customer(db, customer_id)
    if customer is None:
        return None

    customer.nationalID_Photo = save_customer_national_id_photo(customer_id, file)
    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db: Session, customer_id: int) -> bool:
    customer = get_customer(db, customer_id)
    if customer is None:
        return False

    customer.is_deleted = True
    customer.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True
