import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.database import Base
from models.timestamp import Timestamp


class ItemCondition(str, enum.Enum):
    PENDING = "pending"
    GOOD = "good"
    DAMAGED = "damaged"
    MISSING = "missing"


class BookingItem(Timestamp, Base):


    __tablename__ = "booking_item"

    booking_item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.booking_id"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("items_category.category_id"), nullable=False, index=True)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Integer, default=0, nullable=False)
    description = Column(Text, nullable=True)

    condition = Column(Enum(ItemCondition), default=ItemCondition.PENDING, nullable=False)
    condition_notes = Column(Text, nullable=True)
    returned_at = Column(DateTime(timezone=True), nullable=True)
    returned_by_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)

    booking = relationship("Booking", back_populates="items")
    category = relationship("ItemCategory", back_populates="booking_items")
    returned_by = relationship("User")

    def __repr__(self) -> str:
        return f"<BookingItem booking_item_id={self.booking_item_id} booking_id={self.booking_id}>"
