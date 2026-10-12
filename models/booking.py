import enum
import uuid
from sqlalchemy import Column, Date, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.database import Base
from models.timestamp import Timestamp


class BookingStatus(str, enum.Enum):
    ACTIVE = "active"
    DUE = "due"
    OVERDUE = "overdue"
    RETURNED = "returned"
    DAMAGED = "damaged"


class CautionOutcome(str, enum.Enum):
    REFUNDED = "refunded"  # deposit given back to the customer
    KEPT = "kept"  # deposit retained by the business


class Booking(Timestamp, Base):

    __tablename__ = "bookings"

    booking_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    business_id = Column(
        UUID(as_uuid=True), ForeignKey("businesses.business_id"), nullable=False, index=True
    )
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.customer_id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)

    pickup_date = Column(Date, nullable=False)
    event_date = Column(Date, nullable=True)
    return_date = Column(Date, nullable=False)

    price = Column(Integer, default=0, nullable=False)
    caution = Column(Integer, default=0, nullable=False)
    # NULL while the booking is open (caution still held); set at return.
    caution_outcome = Column(Enum(CautionOutcome, native_enum=False, length=10), nullable=True)
    status = Column(Enum(BookingStatus), default=BookingStatus.ACTIVE, nullable=False, index=True)

    customer = relationship("Customer", back_populates="bookings")
    user = relationship("User")
    items = relationship("BookingItem", back_populates="booking", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Booking booking_id={self.booking_id} status={self.status}>"
