from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models import Customer
from schemas.customer import CustomerCreate, CustomerRead

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerRead, status_code=201)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("", response_model=List[CustomerRead])
def list_customers(db: Session = Depends(get_db)):
    return db.query(Customer).filter(Customer.deleted_at.is_(None)).all()


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if customer is None or customer.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
