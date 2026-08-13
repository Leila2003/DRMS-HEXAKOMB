import enum
import uuid

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

from database.database import Base
from models.timestamp import Timestamp


class BookingStatus(str, enum.Enum):
    ACTIVE = "active"
    DUE = "due"
    OVERDUE = "overdue"
    RETURNED = "returned"
    DAMAGED = "damaged"


class Booking(Timestamp, Base):

    __tablename__ = "bookings"

    booking_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.customer_id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)

    pickup_date = Column(Date, nullable=False)
    event_date = Column(Date, nullable=True)
    return_date = Column(Date, nullable=False)

    price = Column(Integer, default=0, nullable=False)
    caution = Column(Integer, default=0, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.ACTIVE, nullable=False, index=True)


    photo_urls = Column(ARRAY(String(500)), default=list, server_default=text("'{}'"), nullable=False)

    customer = relationship("Customer", back_populates="bookings")
    user = relationship("User")
    items = relationship("BookingItem", back_populates="booking", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Booking booking_id={self.booking_id} status={self.status}>"
