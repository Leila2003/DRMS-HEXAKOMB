import enum
import uuid

from sqlalchemy import Boolean, Column, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
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

    notification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    business_id = Column(
        UUID(as_uuid=True), ForeignKey("businesses.business_id"), nullable=False, index=True
    )
    type = Column(Enum(NotificationType), nullable=False)
    group = Column(Enum(NotificationGroup), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    read = Column(Boolean, default=False, nullable=False)

    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.booking_id"), nullable=True, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("items_category.category_id"), nullable=True, index=True)

    booking = relationship("Booking")
    category = relationship("ItemCategory")

    def __repr__(self) -> str:
        return f"<Notification notification_id={self.notification_id} type={self.type}>"
