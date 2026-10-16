from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

import service.booking as booking_service
import service.customer as customer_service
import service.reputation as reputation_service
from database.database import get_db
from models import User
from schemas.booking import BookingListItem
from schemas.customer import (
    CustomerCreate,
    CustomerRead,
    CustomerUpdate,
    ReputationRead,
)
from utils.security import require_business_admin, require_business_member

router = APIRouter(prefix="/customers", tags=["Business Admin", "Staff"])


@router.post("", response_model=CustomerRead, status_code=201)
def create_customer(
    name: str = Form(...),
    contact: str = Form(...),
    referral_name: Optional[str] = Form(None),
    referral_phone: Optional[str] = Form(None),
    national_id_photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_member),
):
    payload = CustomerCreate(
        name=name,
        contact=contact,
        referral_name=referral_name,
        referral_phone=referral_phone,
    )
    try:
        customer = customer_service.create_customer(db, payload, current_user.business_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if national_id_photo is not None:
        customer = customer_service.upload_national_id_photo(
            db, customer.customer_id, current_user.business_id, national_id_photo
        )

    return customer


@router.get("", response_model=List[CustomerRead], summary="Get all customers")
def list_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_member),
):
    return customer_service.list_customers(db, current_user.business_id)


# @router.get("/lookup", response_model=Optional[CustomerRead])
# def lookup_customer(
#     contact: str,
#     db: Session = Depends(get_db),
#     _user: User = Depends(get_current_user),
# ):
#     """Check whether a customer already exists for this contact, before booking creates a new one."""
#     return customer_service.find_customer_by_contact(db, contact)


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_member),
):
    customer = customer_service.get_customer(db, customer_id, current_user.business_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/{customer_id}/reputation", response_model=ReputationRead)
def get_customer_reputation(
    customer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_member),
):
    customer = customer_service.get_customer(db, customer_id, current_user.business_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return reputation_service.get_reputation(db, customer_id)


@router.get("/{customer_id}/bookings", response_model=List[BookingListItem])
def get_customer_bookings(
    customer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_member),
):
    customer = customer_service.get_customer(db, customer_id, current_user.business_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    bookings = customer_service.get_customer_bookings(db, customer_id, current_user.business_id)
    return [booking_service.to_booking_list_dict(b) for b in bookings]


@router.put("/{customer_id}", response_model=CustomerRead)
def update_customer(
    customer_id: UUID,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_admin),
):
    try:
        customer = customer_service.update_customer(db, customer_id, current_user.business_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


# @router.post("/{customer_id}/national-id-photo", response_model=CustomerRead)
# def upload_national_id_photo(
#     customer_id: UUID,
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     _user: User = Depends(get_current_user),
# ):
#     customer = customer_service.upload_national_id_photo(db, customer_id, file)
#     if customer is None:
#         raise HTTPException(status_code=404, detail="Customer not found")
#     return customer


@router.delete("/{customer_id}", status_code=204)
def delete_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_admin),
):
    try:
        deleted = customer_service.delete_customer(db, customer_id, current_user.business_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")
