from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    item_name: str
    item_type: Optional[str] = None
    description: Optional[str] = None
    total_owned: int = Field(gt=0)


class CategoryUpdate(BaseModel):
    """Partial update: send only the field(s) you want to change.
    quantity_available/quantity_rented/created_at are system-managed
    (via booking check-out/return and creation) and are never
    client-writable here."""

    item_name: Optional[str] = None
    item_type: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    total_owned: Optional[int] = Field(default=None, gt=0)


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: UUID
    item_name: str
    item_type: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    total_owned: int
    quantity_available: int
    quantity_rented: int
    created_at: datetime
