from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

import service.category as category_service
from database.database import get_db
from models import User
from schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from utils.security import require_business_member

router = APIRouter(prefix="/categories", tags=["Business Admin", "Staff"])


@router.post("", response_model=CategoryRead, status_code=201)
def create_category(
    item_name: str = Form(...),
    item_type: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    total_owned: int = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_member),
):
    existing = category_service.list_categories(db, current_user.business_id, search=item_name)
    if any(c.item_name.lower() == item_name.lower() for c in existing):
        raise HTTPException(status_code=400, detail="A category with this name already exists")

    payload = CategoryCreate(
        item_name=item_name,
        item_type=item_type,
        description=description,
        total_owned=total_owned,
    )
    category = category_service.create_category(db, payload, current_user.business_id)

    if image is not None:
        category = category_service.upload_category_image(db, category.category_id, current_user.business_id, image)

    return category


@router.get("", response_model=List[CategoryRead], summary="Get all categories")
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_member),
):
    return category_service.list_categories(db, current_user.business_id)


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_member),
):
    category = category_service.get_category(db, category_id, current_user.business_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/{category_id}/image", response_model=CategoryRead)
def upload_category_image(
    category_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_member),
):
    category = category_service.upload_category_image(db, category_id, current_user.business_id, file)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_member),
):
    category = category_service.update_category(db, category_id, current_user.business_id, payload)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_member),
):
    deleted = category_service.delete_category(db, category_id, current_user.business_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
