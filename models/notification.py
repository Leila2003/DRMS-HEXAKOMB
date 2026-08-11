import enum

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database.database import Base
from models.timestamp import Timestamp


class NotificationType(str, enum.Enum):
    WARN = "warn"
    ALERT = "alert"
    INFO = "info"


class NotificationGroup(str, enum.Enum):
    UPCOMING_RETURNS = "Upcoming returns"
    OVERDUE = "Overdue"
    LOW_STOCK = "Low stock"
    INVENTORY = "Inventory"


class Notification(Timestamp, Base):

    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(NotificationType), nullable=False)
    group = Column(Enum(NotificationGroup), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    read = Column(Boolean, default=False, nullable=False)

    booking_id = Column(Integer, ForeignKey("bookings.booking_id"), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("items_category.category_id"), nullable=True, index=True)

    booking = relationship("Booking")
    category = relationship("ItemCategory")

    def __repr__(self) -> str:
        return f"<Notification notification_id={self.notification_id} type={self.type}>"
