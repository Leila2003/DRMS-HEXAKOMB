import math
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

import service.booking as booking_service
from database.database import get_db
from models import User
from schemas.booking import BookingCreate, BookingPage, BookingRead, ReturnRequest
from utils.security import get_current_user

router = APIRouter(prefix="/bookings", tags=["Admin", "Staff"])


@router.post("", response_model=BookingRead, status_code=201)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        booking = booking_service.create_booking(db, payload, current_user.user_id)
    except booking_service.BookingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return booking_service.to_booking_dict(booking)


@router.get("", response_model=BookingPage)
def list_bookings(
    status: Optional[str] = Query(default="all"),
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    bookings, total = booking_service.list_bookings(db, status, search, page, page_size)
    total_pages = max(1, math.ceil(total / page_size))
    return BookingPage(
        items=[booking_service.to_booking_list_dict(b) for b in bookings],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{booking_id}", response_model=BookingRead)
def get_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    booking = booking_service.get_booking(db, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking_service.to_booking_dict(booking)


@router.post("/{booking_id}/photos", response_model=BookingRead)
def upload_booking_photos(
    booking_id: UUID,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    booking = booking_service.add_photos(db, booking_id, files)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking_service.to_booking_dict(booking)


@router.post("/{booking_id}/return", response_model=BookingRead)
def return_booking(
    booking_id: UUID,
    payload: ReturnRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        booking = booking_service.process_return(db, booking_id, payload, current_user.user_id)
    except booking_service.BookingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking_service.to_booking_dict(booking)
