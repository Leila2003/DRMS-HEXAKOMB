import uuid
from sqlalchemy import Column, Integer, ForeignKey, Date, Enum, DateTime, Numeric
from sqlalchemy.orm  import relationship
from models.time_stamp import TimeStamp
from sqlalchemy.dialects.mysql import CHAR
from database.database_connection import Base
from datetime import datetime
from schemas.booking_schema import BookingStatusEnum

# Creation of the bookings table and its respective fields
class Bookings(TimeStamp, Base):
    __tablename__ = 'bookings'
    booking_id = Column(CHAR(36), nullable=False, primary_key=True, default=lambda : str(uuid.uuid4()))
    customer_id = Column(CHAR(36), ForeignKey('customers.customer_id'), nullable=False)
    user_id = Column(CHAR(36), ForeignKey('users.user_id'), nullable=False)
    pickup_date = Column(Date, nullable=False)
    event_date = Column(Date, nullable=False)
    drop_off_date = Column(Date, nullable=False)
    price = Column(Integer, nullable=False)
    caution = Column(Integer, nullable=False)
    status = Column(Enum(BookingStatusEnum), default= BookingStatusEnum.ACTIVE, nullable=False)

    customer = relationship('Customers', foreign_keys=[customer_id], back_populates='bookings')
    user = relationship('User', foreign_keys=[user_id], back_populates='bookings')
    booking_items = relationship('BookingItem', foreign_keys='[BookingItem.booking_id]', back_populates='booking')