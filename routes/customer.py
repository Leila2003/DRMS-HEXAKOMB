import math
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

import service.booking as booking_service
import service.customer as customer_service
import service.reputation as reputation_service
from database.database import get_db
from models import User
from schemas.booking import BookingListItem
from schemas.customer import (
    CustomerCreate,
    CustomerPage,
    CustomerRead,
    CustomerUpdate,
    ReputationRead,
)
from utils.security import get_current_user

router = APIRouter(prefix="/customers", tags=["Admin", "Staff"])


@router.post("", response_model=CustomerRead, status_code=201)
def create_customer(
    name: str = Form(...),
    contact: str = Form(...),
    referral_name: Optional[str] = Form(None),
    referral_phone: Optional[str] = Form(None),
    national_id_photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
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


@router.get("", response_model=CustomerPage)
def list_customers(
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    customers, total = customer_service.list_customers(db, search, page, page_size)
    total_pages = max(1, math.ceil(total / page_size))
    return CustomerPage(items=customers, total=total, page=page, page_size=page_size, total_pages=total_pages)


@router.get("/lookup", response_model=Optional[CustomerRead])
def lookup_customer(
    contact: str,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Check whether a customer already exists for this contact, before booking creates a new one."""
    return customer_service.find_customer_by_contact(db, contact)


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    customer = customer_service.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/{customer_id}/reputation", response_model=ReputationRead)
def get_customer_reputation(
    customer_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    customer = customer_service.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return reputation_service.get_reputation(db, customer_id)


@router.get("/{customer_id}/bookings", response_model=List[BookingListItem])
def get_customer_bookings(
    customer_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    customer = customer_service.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    bookings = customer_service.get_customer_bookings(db, customer_id)
    return [booking_service.to_booking_list_dict(b) for b in bookings]


@router.put("/{customer_id}", response_model=CustomerRead)
def update_customer(
    customer_id: str,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    customer = customer_service.update_customer(db, customer_id, payload)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("/{customer_id}/national-id-photo", response_model=CustomerRead)
def upload_national_id_photo(
    customer_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    customer = customer_service.upload_national_id_photo(db, customer_id, file)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.delete("/{customer_id}", status_code=204)
def delete_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    deleted = customer_service.delete_customer(db, customer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")
