import uuid
from database.database_connection import Base
from models.time_stamp import TimeStamp
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Enum, DateTime, Integer
from sqlalchemy.dialects.mysql import CHAR
from schemas.user_schema import UserTypeEnum

class ItemCategory(TimeStamp, Base):
    __tablename__ = 'item_categories'
    category_id =  Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_name = Column(String(100), nullable=False)
    item_type = Column(String(100), nullable=False)
    photo_url  = Column(String(500), nullable=False)
    description = Column(String(200), nullable=False)
    total_number_owned = Column(Integer, default=0, nullable=False)
    quantity_available = Column(Integer, nullable=False, default=0)
    quantity_rented = Column(Integer, nullable=False, default=0)

    booking_items = relationship('BookingItem', foreign_keys='[BookingItem.category_id]', back_populates='category')