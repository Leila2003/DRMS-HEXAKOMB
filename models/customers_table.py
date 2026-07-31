import uuid
from database.database_connection import Base
from models.time_stamp import TimeStamp
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.dialects.mysql import CHAR
from schemas.user_schema import UserTypeEnum

class Customers(TimeStamp, Base):
    __tablename__ = 'customers'
    customer_id =  Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    national_id = Column(String(20), unique=True, nullable=False)
    customer_name = Column(String(100), nullable=False)
    customer_contact = Column(String(20), nullable=False)
    referral_name = Column(String(100), nullable=False)
    referral_contact = Column(String(20), nullable=False)

    bookings = relationship('Bookings', foreign_keys='[Bookings.customer_id]', back_populates='customer')