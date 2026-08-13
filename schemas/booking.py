from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from models.booking import BookingStatus
from models.booking_item import ItemCondition
from schemas.customer import CustomerCreate, CustomerRead


class BookingItemLineIn(BaseModel):
    category_id: UUID
    unit_price: int = Field(ge=0)
    description: Optional[str] = None


class BookingCreate(BaseModel):
    customer_id: Optional[UUID] = None
    new_customer: Optional[CustomerCreate] = None
    event_date: Optional[date] = None
    pickup_date: date
    return_date: date
    caution: int = Field(default=0, ge=0)
    items: List[BookingItemLineIn] = Field(min_length=1)

    @model_validator(mode="after")
    def check_customer_and_dates(self) -> "BookingCreate":
        if bool(self.customer_id) == bool(self.new_customer):
            raise ValueError("Provide exactly one of customer_id or new_customer")
        if self.return_date < self.pickup_date:
            raise ValueError("Return date must be on or after the pickup date")
        return self


class ReturnRequest(BaseModel):
    condition: ItemCondition
    notes: Optional[str] = None

    @model_validator(mode="after")
    def check_condition(self) -> "ReturnRequest":
        if self.condition == ItemCondition.PENDING:
            raise ValueError("condition must be good, damaged or missing")
        return self


class BookingItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    booking_item_id: UUID
    category_id: UUID
    unit_price: int
    description: Optional[str] = None
    condition: ItemCondition


class ItemSummary(BaseModel):
    category_id: UUID
    category_name: str
    icon: Optional[str] = None
    quantity: int


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    booking_id: UUID
    customer: CustomerRead
    event_date: Optional[date] = None
    pickup_date: date
    return_date: date
    price: int
    caution: int
    status: BookingStatus
    lines: List[BookingItemRead]
    items: List[ItemSummary]
    photos: List[str]
    created_at: datetime


class BookingListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    booking_id: UUID
    customer: CustomerRead
    event_date: Optional[date] = None
    pickup_date: date
    return_date: date
    price: int
    caution: int
    status: BookingStatus
    items: List[ItemSummary]


class BookingPage(BaseModel):
    items: List[BookingListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
