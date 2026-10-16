from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from models import ItemCategory
from schemas.category import CategoryCreate, CategoryUpdate
from utils.file_storage import save_category_image

LOW_STOCK_THRESHOLD = 3


def is_low_stock(category: ItemCategory) -> bool:
    return category.quantity_available <= LOW_STOCK_THRESHOLD


def create_category(db: Session, payload: CategoryCreate, business_id: UUID) -> ItemCategory:
    category = ItemCategory(
        business_id=business_id,
        item_name=payload.item_name,
        item_type=payload.item_type,
        description=payload.description,
        total_owned=payload.total_owned,
        quantity_available=payload.total_owned,
        quantity_rented=0,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def upload_category_image(
    db: Session, category_id: UUID, business_id: UUID, file: UploadFile
) -> Optional[ItemCategory]:
    category = get_category(db, category_id, business_id)
    if category is None:
        return None

    category.image_url = save_category_image(category_id, file)
    db.commit()
    db.refresh(category)
    return category


def list_categories(db: Session, business_id: UUID, search: Optional[str] = None) -> List[ItemCategory]:
    query = db.query(ItemCategory).filter(
        ItemCategory.business_id == business_id, ItemCategory.deleted_at.is_(None)
    )
    if search:
        query = query.filter(ItemCategory.item_name.ilike(f"%{search}%"))
    return query.order_by(ItemCategory.item_name).all()


def get_category(db: Session, category_id: UUID, business_id: UUID) -> Optional[ItemCategory]:
    category = db.get(ItemCategory, category_id)
    if category is None or category.deleted_at is not None or category.business_id != business_id:
        return None
    return category


def update_category(
    db: Session, category_id: UUID, business_id: UUID, payload: CategoryUpdate
) -> Optional[ItemCategory]:
    category = get_category(db, category_id, business_id)
    if category is None:
        return None

    data = payload.model_dump(exclude_unset=True)
    new_total = data.pop("total_owned", None)
    for field, value in data.items():
        setattr(category, field, value)

    if new_total is not None:
        category.total_owned = new_total
        category.quantity_available = new_total - category.quantity_rented

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: UUID, business_id: UUID) -> bool:
    category = get_category(db, category_id, business_id)
    if category is None:
        return False

    category.is_deleted = True
    category.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True


def adjust_rented(category: ItemCategory, delta: int) -> None:
    """Move `delta` units between available and rented (delta>0 = check out)."""
    category.quantity_rented += delta
    category.quantity_available = category.total_owned - category.quantity_rented


def write_off(category: ItemCategory, quantity: int) -> None:
    """Permanently remove `quantity` units from stock (damaged/missing on return)."""
    category.total_owned -= quantity
    category.quantity_rented -= quantity
    category.quantity_available = category.total_owned - category.quantity_rented
