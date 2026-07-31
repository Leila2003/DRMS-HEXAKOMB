import uuid
from database.database_connection import Base
from models.time_stamp import TimeStamp
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.dialects.mysql import CHAR
from schemas.user_schema import UserTypeEnum

class User(TimeStamp, Base):
    __tablename__ = 'users'
    user_id =  Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(225), nullable=False)
    role = Column(Enum(UserTypeEnum), nullable=False)

    bookings = relationship('Bookings', foreign_keys='[Bookings.user_id]', back_populates='user')

