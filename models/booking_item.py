import enum
import uuid
from sqlalchemy import CHAR, Column, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from database.database import Base
from models.time_stamp import TimeStamp


class ItemCondition(str, enum.Enum):
    PENDING = "pending"
    GOOD = "good"
    DAMAGED = "damaged"
    MISSING = "missing"


class BookingItem(TimeStamp, Base):
  

    __tablename__ = "booking_item"

    booking_item_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id = Column(CHAR(36), ForeignKey("bookings.booking_id"), nullable=False, index=True)
    category_id = Column(CHAR(36), ForeignKey("items_category.category_id"), nullable=False, index=True)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Integer, default=0, nullable=False)
    description = Column(Text, nullable=True)

    condition = Column(Enum(ItemCondition), default=ItemCondition.PENDING, nullable=False)
    condition_notes = Column(Text, nullable=True)
    returned_at = Column(DateTime(timezone=True), nullable=True)
    returned_by_id = Column(CHAR(36), ForeignKey("users.user_id"), nullable=True)

    booking = relationship("Booking", back_populates="items")
    category = relationship("ItemCategory", back_populates="booking_items")
    returned_by = relationship("User")

    def __repr__(self) -> str:
        return f"<BookingItem booking_item_id={self.booking_item_id} booking_id={self.booking_id}>"
