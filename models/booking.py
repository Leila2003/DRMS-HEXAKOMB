import enum
import uuid
from sqlalchemy import CHAR, Column, Date, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship

from database.database import Base
from models.time_stamp import TimeStamp


class BookingStatus(str, enum.Enum):
    ACTIVE = "active"
    DUE = "due"
    OVERDUE = "overdue"
    RETURNED = "returned"
    DAMAGED = "damaged"


class Booking(TimeStamp, Base):
   
    __tablename__ = "bookings"

    booking_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(CHAR(36), ForeignKey("customers.customer_id"), nullable=False, index=True)
    user_id = Column(CHAR(36), ForeignKey("users.user_id"), nullable=False, index=True)

    pickup_date = Column(Date, nullable=False)
    event_date = Column(Date, nullable=True)
    return_date = Column(Date, nullable=False)

    price = Column(Integer, default=0, nullable=False)
    caution = Column(Integer, default=0, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.ACTIVE, nullable=False, index=True)

    customer = relationship("Customer", back_populates="bookings")
    user = relationship("User")
    items = relationship("BookingItem", back_populates="booking", cascade="all, delete-orphan")
    photos = relationship("BookingPhoto", back_populates="booking", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Booking booking_id={self.booking_id} status={self.status}>"
