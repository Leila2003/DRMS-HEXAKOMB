from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


from database.database import Base
from models.timestamp import Timestamp



class BookingPhoto(Timestamp, Base):

    __tablename__ = "booking_photos"

    photo_id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.booking_id"), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)

    booking = relationship("Booking", back_populates="photos")

    def __repr__(self) -> str:
        return f"<BookingPhoto photo_id={self.photo_id} booking_id={self.booking_id}>"
