import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def save_booking_photo(booking_id: str, file: UploadFile) -> str:
    extension = ALLOWED_IMAGE_TYPES.get(file.content_type)
    if extension is None:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image type. Allowed: JPEG, PNG, WEBP.",
        )

    booking_dir = UPLOAD_DIR / "bookings" / str(booking_id)
    booking_dir.mkdir(parents=True, exist_ok=True)

    destination = booking_dir / f"{uuid.uuid4().hex}{extension}"
    with destination.open("wb") as buffer:
        buffer.write(file.file.read())

    return f"/uploads/bookings/{booking_id}/{destination.name}"


def save_customer_national_id_photo(customer_id: str, file: UploadFile) -> str:
    extension = ALLOWED_IMAGE_TYPES.get(file.content_type)
    if extension is None:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image type. Allowed: JPEG, PNG, WEBP.",
            
        )

    customer_dir = UPLOAD_DIR / "customers" / str(customer_id)
    customer_dir.mkdir(parents=True, exist_ok=True)

    destination = customer_dir / f"national_id{extension}"
    with destination.open("wb") as buffer:
        buffer.write(file.file.read())

    return f"/uploads/customers/{customer_id}/national_id{extension}"


def save_category_image(category_id: str, file: UploadFile) -> str:
    extension = ALLOWED_IMAGE_TYPES.get(file.content_type)
    if extension is None:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image type. Allowed: JPEG, PNG, WEBP.",
        )

    category_dir = UPLOAD_DIR / "categories" / str(category_id)
    category_dir.mkdir(parents=True, exist_ok=True)

    destination = category_dir / f"image{extension}"
    with destination.open("wb") as buffer:
        buffer.write(file.file.read())

    return f"/uploads/categories/{category_id}/image{extension}"
