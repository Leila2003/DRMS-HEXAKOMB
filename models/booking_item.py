import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.database import Base


class ItemCondition(str, enum.Enum):
    PENDING = "pending"
    GOOD = "good"
    DAMAGED = "damaged"
    MISSING = "missing"


class BookingItem(Base):
    """A line within a booking: how many units of one item category were rented."""

    __tablename__ = "booking_item"

    booking_item_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.booking_id"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("items_category.category_id"), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # recorded by staff when the item is handed back
    condition: Mapped[ItemCondition] = mapped_column(
        Enum(ItemCondition), default=ItemCondition.PENDING, nullable=False
    )
    condition_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    returned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    returned_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    # soft delete: non-null means this row is treated as removed
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    booking: Mapped["Booking"] = relationship(back_populates="items")
    category: Mapped["ItemCategory"] = relationship(back_populates="booking_items")
    returned_by: Mapped[Optional["User"]] = relationship()

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def __repr__(self) -> str:
        return f"<BookingItem booking_item_id={self.booking_item_id} booking_id={self.booking_id}>"
