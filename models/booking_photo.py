import uuid
from sqlalchemy import Column, ForeignKey, CHAR, String
from sqlalchemy.orm import relationship


from database.database import Base
from models.time_stamp import TimeStamp



class BookingPhoto(TimeStamp, Base):

    __tablename__ = "booking_photos"

    photo_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id = Column(CHAR(36), ForeignKey("bookings.booking_id"), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)

    booking = relationship("Booking", back_populates="photos")

    def __repr__(self) -> str:
        return f"<BookingPhoto photo_id={self.photo_id} booking_id={self.booking_id}>"
