import uuid

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.database import Base
from models.timestamp import Timestamp


class Customer(Timestamp, Base):


    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("business_id", "contact", name="uq_customers_business_contact"),
    )


    customer_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    business_id = Column(
        UUID(as_uuid=True), ForeignKey("businesses.business_id"), nullable=False, index=True
    )
    name = Column(String(150), nullable=False)
    nationalID_Photo = Column("national_id_photo", String(500), nullable=True)
    contact = Column(String(30), index=True, nullable=False)
    referral_name = Column(String(150), nullable=True)
    referral_phone = Column(String(30), nullable=True)
    
    business = relationship("Business")
    bookings = relationship("Booking", back_populates="customer")
    # bookings = relationship("Booking", back_populates="customer")

    @property
    def rentals_count(self) -> int:

        return len(self.bookings)
        

    def __repr__(self) -> str:
        return f"<Customer customer_id={self.customer_id} name={self.name!r}>"
