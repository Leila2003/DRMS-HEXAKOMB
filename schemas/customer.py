from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CustomerCreate(BaseModel):
    name: str
    contact: str
    referral_name: Optional[str] = None
    referral_phone: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    nationalID_Photo: Optional[str] = None
    referral_name: Optional[str] = None
    referral_phone: Optional[str] = None


class CustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: int
    name: str
    contact: str
    nationalID_Photo: Optional[str] = None
    referral_name: Optional[str] = None
    referral_phone: Optional[str] = None
    rentals_count: int = 0
    created_at: datetime


class CustomerPage(BaseModel):
    items: List["CustomerRead"]
    total: int
    page: int
    page_size: int
    total_pages: int


class ReputationRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    cls: str = Field(alias="class")
    icon: str
    label: str
    detail: str
