import uuid

from sqlalchemy import Column, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.database import Base
from models.timestamp import Timestamp


class ItemCategory(Timestamp, Base):

    __tablename__ = "items_category"
    __table_args__ = (
        UniqueConstraint("business_id", "item_name", name="uq_items_category_business_item_name"),
    )

    category_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    business_id = Column(
        UUID(as_uuid=True), ForeignKey("businesses.business_id"), nullable=False, index=True
    )
    item_name = Column(String(150), nullable=False)
    item_type = Column(String(100), nullable=True)
    image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    total_owned = Column(Integer, default=0, nullable=False)
    quantity_available = Column(Integer, default=0, nullable=False)
    quantity_rented = Column(Integer, default=0, nullable=False)
    icon = Column(String(10), nullable=True)
    tile_color = Column(String(30), nullable=True)

    booking_items = relationship("BookingItem", back_populates="category")

    def __repr__(self) -> str:
        return f"<ItemCategory category_id={self.category_id} item_name={self.item_name!r}>"
