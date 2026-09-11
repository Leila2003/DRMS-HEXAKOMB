from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import service.booking as booking_service
from database.database import get_db
from models import User
from schemas.booking import BookingCreate, BookingListItem, BookingRead, ReturnRequest
from utils.security import require_business_member

router = APIRouter(prefix="/bookings", tags=["Business Admin", "Staff"])


@router.post("", response_model=BookingRead, status_code=201)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_member),
):
    try:
        booking = booking_service.create_booking(db, payload, current_user.user_id, current_user.business_id)
    except booking_service.BookingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return booking_service.to_booking_dict(booking)


@router.get("", response_model=List[BookingListItem], summary="Get all bookings")
def list_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_member),
):
    bookings = booking_service.list_bookings(db, current_user.business_id)
    return [booking_service.to_booking_list_dict(b) for b in bookings]


@router.get("/{booking_id}", response_model=BookingRead)
def get_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_member),
):
    booking = booking_service.get_booking(db, booking_id, current_user.business_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking_service.to_booking_dict(booking)


@router.post("/{booking_id}/return", response_model=BookingRead)
def return_booking(
    booking_id: UUID,
    payload: ReturnRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_member),
):
    try:
        booking = booking_service.process_return(
            db, booking_id, current_user.business_id, payload, current_user.user_id
        )
    except booking_service.BookingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking_service.to_booking_dict(booking)
