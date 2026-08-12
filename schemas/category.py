from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    item_name: str
    item_type: Optional[str] = None
    description: Optional[str] = None
    total_owned: int = Field(gt=0)


class CategoryUpdate(BaseModel):
    item_name: str
    item_type: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    total_owned: int = Field(gt=0)
    quantity_available: int
    quantity_rented: int
    created_at: datetime


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int
    item_name: str
    item_type: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    total_owned: int
    quantity_available: int
    quantity_rented: int
    created_at: datetime
