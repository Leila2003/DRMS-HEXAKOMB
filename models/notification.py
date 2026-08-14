import enum
import uuid
from sqlalchemy import Boolean, Column, Enum, ForeignKey, CHAR, String, Text
from sqlalchemy.orm import relationship

from database.database import Base
from models.time_stamp import TimeStamp


class NotificationType(str, enum.Enum):
    WARN = "warn"
    ALERT = "alert"
    INFO = "info"


class NotificationGroup(str, enum.Enum):
    UPCOMING_RETURNS = "Upcoming returns"
    OVERDUE = "Overdue"
    LOW_STOCK = "Low stock"
    INVENTORY = "Inventory"


class Notification(TimeStamp, Base):

    __tablename__ = "notifications"

    notification_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(Enum(NotificationType), nullable=False)
    group = Column(Enum(NotificationGroup), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    read = Column(Boolean, default=False, nullable=False)

    booking_id = Column(CHAR(36), ForeignKey("bookings.booking_id"), nullable=True, index=True)
    category_id = Column(CHAR(36), ForeignKey("items_category.category_id"), nullable=True, index=True)

    booking = relationship("Booking")
    category = relationship("ItemCategory")

    def __repr__(self) -> str:
        return f"<Notification notification_id={self.notification_id} type={self.type}>"
