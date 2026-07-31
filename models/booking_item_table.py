import uuid
from sqlalchemy import Column, Integer, ForeignKey, Date, Enum, DateTime, Numeric
from sqlalchemy.orm  import relationship
from models.time_stamp import TimeStamp
from sqlalchemy.dialects.mysql import CHAR
from database.database_connection import Base
from datetime import datetime

# Creation of the bookings table and its respective fields
class BookingItem(TimeStamp, Base):
    __tablename__ = 'booking_item'
    booking_item_id = Column(CHAR(36), nullable=False, primary_key=True, default=lambda : str(uuid.uuid4()))
    booking_id = Column(CHAR(36), ForeignKey('bookings.booking_id'), nullable=False)
    category_id = Column(CHAR(36), ForeignKey('item_categories.category_id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)


    booking = relationship('Bookings', foreign_keys=[booking_id], back_populates='booking_items')
    category = relationship('ItemCategory', foreign_keys=[category_id], back_populates='booking_items')


