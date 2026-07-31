from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.database import Base


class ItemCategory(Base):
    """A rentable item type (e.g. Bridal gowns, Tents).

    total_owned / quantity_available / quantity_rented are all stored columns per
    the ERD (quantity_available is not derived). The service layer that adjusts
    stock on booking/return is responsible for keeping
    total_owned == quantity_available + quantity_rented.
    """

    __tablename__ = "items_category"

    category_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    item_name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    item_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_owned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quantity_available: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quantity_rented: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    # soft delete: non-null means this row is treated as removed
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    booking_items: Mapped[List["BookingItem"]] = relationship(back_populates="category")

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def __repr__(self) -> str:
        return f"<ItemCategory category_id={self.category_id} item_name={self.item_name!r}>"
