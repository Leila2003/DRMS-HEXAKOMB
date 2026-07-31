from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.database import Base


class Customer(Base):
    """A person who rents items. Reputation/history is derived from their bookings
    (see rentals_count), not stored directly, so it can never drift out of sync."""

    __tablename__ = "customers"

    customer_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    national_id_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    contact: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    referral_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    referral_phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    # soft delete: non-null means this row is treated as removed
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    bookings: Mapped[List["Booking"]] = relationship(back_populates="customer")

    @property
    def rentals_count(self) -> int:
        """Total number of bookings ever made by this customer."""
        return len(self.bookings)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def __repr__(self) -> str:
        return f"<Customer customer_id={self.customer_id} name={self.name!r}>"
