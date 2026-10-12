import os
import time
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def save_customer_national_id_photo(customer_id: UUID, file: UploadFile) -> str:
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

    # The file always lands at the same path, so a re-upload would otherwise
    # be served from browser cache under the old bytes. A version query
    # param, stored as part of image_url itself, makes the URL change on
    # every upload for every client, not just the one that made the change.
    version = int(time.time() * 1000)
    return f"/uploads/customers/{customer_id}/national_id{extension}?v={version}"


def save_category_image(category_id: UUID, file: UploadFile) -> str:
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

    # See the matching comment in save_customer_national_id_photo above.
    version = int(time.time() * 1000)
    return f"/uploads/categories/{category_id}/image{extension}?v={version}"
