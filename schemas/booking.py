from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from models.booking import BookingStatus, CautionOutcome
from models.booking_item import ItemCondition
from schemas.customer import CustomerCreate, CustomerRead


class BookingItemLineIn(BaseModel):
    category_id: UUID
    quantity: int = Field(default=1, ge=1)
    unit_price: int = Field(ge=0)  # price for this category, per unit


class BookingCreate(BaseModel):
    customer_id: Optional[UUID] = None
    new_customer: Optional[CustomerCreate] = None
    event_date: Optional[date] = None
    pickup_date: date
    return_date: date
    caution: int = Field(default=0, ge=0)  # single deposit for the whole booking
    items: List[BookingItemLineIn] = Field(min_length=1)

    @model_validator(mode="after")
    def check_customer_and_dates(self) -> "BookingCreate":
        if bool(self.customer_id) == bool(self.new_customer):
            raise ValueError("Provide exactly one of customer_id or new_customer")
        if self.return_date < self.pickup_date:
            raise ValueError("Return date must be on or after the pickup date")
        return self


class BookingItemLineUpdate(BaseModel):
    booking_item_id: UUID
    quantity: int = Field(ge=1)
    unit_price: int = Field(ge=0)


class BookingUpdate(BaseModel):
    event_date: Optional[date] = None
    pickup_date: Optional[date] = None
    return_date: Optional[date] = None
    caution: Optional[int] = Field(default=None, ge=0)
    lines: Optional[List[BookingItemLineUpdate]] = None


class ReturnRequest(BaseModel):
    condition: ItemCondition
    notes: Optional[str] = None
    # Required when the booking has a caution: refund it or keep it.
    caution_outcome: Optional[CautionOutcome] = None

    @model_validator(mode="after")
    def check_condition(self) -> "ReturnRequest":
        if self.condition == ItemCondition.PENDING:
            raise ValueError("condition must be good, damaged or missing")
        return self


class BookingItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    booking_item_id: UUID
    category_id: UUID
    quantity: int
    unit_price: int
    description: Optional[str] = None
    condition: ItemCondition

    @computed_field
    @property
    def line_total(self) -> int:
        return self.unit_price * self.quantity


class ItemSummary(BaseModel):
    category_id: UUID
    category_name: str
    icon: Optional[str] = None
    quantity: int
    subtotal: int  # unit_price * quantity summed across this category's lines


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    booking_id: UUID
    customer: CustomerRead
    event_date: Optional[date] = None
    pickup_date: date
    return_date: date
    price: int  # rental total across all categories
    caution: int  # deposit for the whole booking
    total_amount: int  # price + caution
    caution_outcome: Optional[CautionOutcome] = None
    status: BookingStatus
    lines: List[BookingItemRead]
    items: List[ItemSummary]
    created_at: datetime


class BookingListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    booking_id: UUID
    customer: CustomerRead
    event_date: Optional[date] = None
    pickup_date: date
    return_date: date
    price: int  # rental total across all categories
    caution: int  # deposit for the whole booking
    total_amount: int  # price + caution
    caution_outcome: Optional[CautionOutcome] = None
    status: BookingStatus
    items: List[ItemSummary]


class BookingPage(BaseModel):
    items: List[BookingListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
