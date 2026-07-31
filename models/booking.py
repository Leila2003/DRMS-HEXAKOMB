import enum
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.database import Base


class BookingStatus(str, enum.Enum):
    ACTIVE = "active"
    DUE = "due"
    OVERDUE = "overdue"
    RETURNED = "returned"
    DAMAGED = "damaged"
    


class Booking(Base):
    """One rental order: a customer, the staff member who handled it, the rental
    window, and the money involved. The rented item lines live on BookingItem."""

    __tablename__ = "bookings"

    booking_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.customer_id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)

    pickup_date: Mapped[date] = mapped_column(Date, nullable=False)
    event_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    return_date: Mapped[date] = mapped_column(Date, nullable=False)

    price: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    caution: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus), default=BookingStatus.ACTIVE, nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    # soft delete: non-null means this row is treated as removed
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    customer: Mapped["Customer"] = relationship(back_populates="bookings")
    user: Mapped["User"] = relationship()
    items: Mapped[List["BookingItem"]] = relationship(back_populates="booking", cascade="all, delete-orphan")

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def __repr__(self) -> str:
        return f"<Booking booking_id={self.booking_id} status={self.status}>"
