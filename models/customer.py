import uuid
from sqlalchemy import Column, CHAR, String
from sqlalchemy.orm import relationship

from database.database import Base
from models.time_stamp import TimeStamp


class Customer(TimeStamp, Base):


    __tablename__ = "customers"
    

    customer_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(150), nullable=False)
    nationalID_Photo = Column("national_id_photo", String(500), nullable=True)
    contact = Column(String(30), unique=True, index=True, nullable=False)
    referral_name = Column(String(150), nullable=True)
    referral_phone = Column(String(30), nullable=True)

    bookings = relationship("Booking", back_populates="customer")

    @property
    def rentals_count(self) -> int:
      
        return len(self.bookings)

    def __repr__(self) -> str:
        return f"<Customer customer_id={self.customer_id} name={self.name!r}>"
