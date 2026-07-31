from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

import service.customer as customer_service
from database.database import get_db
from schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerRead, status_code=201)
def create_customer(
    name: str = Form(...),
    contact: str = Form(...),
    referral_name: Optional[str] = Form(None),
    referral_phone: Optional[str] = Form(None),
    national_id_photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    payload = CustomerCreate(
        name=name,
        contact=contact,
        referral_name=referral_name,
        referral_phone=referral_phone,
    )
    customer = customer_service.create_customer(db, payload)

    if national_id_photo is not None:
        customer = customer_service.upload_national_id_photo(
            db, customer.customer_id, national_id_photo
        )

    return customer


@router.get("", response_model=List[CustomerRead])
def list_customers(db: Session = Depends(get_db)):
    return customer_service.list_customers(db)


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = customer_service.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerRead)
def update_customer(customer_id: int, payload: CustomerUpdate, db: Session = Depends(get_db)):
    customer = customer_service.update_customer(db, customer_id, payload)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("/{customer_id}/national-id-photo", response_model=CustomerRead)
def upload_national_id_photo(
    customer_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    customer = customer_service.upload_national_id_photo(db, customer_id, file)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    deleted = customer_service.delete_customer(db, customer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")
