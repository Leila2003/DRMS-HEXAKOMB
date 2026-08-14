import uuid
from sqlalchemy import Column, CHAR, String, Text, Integer
from sqlalchemy.orm import relationship

from database.database import Base
from models.time_stamp import TimeStamp


class ItemCategory(TimeStamp, Base):

    __tablename__ = "items_category"

    category_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_name = Column(String(150), unique=True, nullable=False)
    item_type = Column(String(100), nullable=True)
    image_url = Column(String(500), nullable=True)
    icon = Column(String(10), nullable=True)
    tile_color = Column(String(30), nullable=True)
    description = Column(Text, nullable=True)
    total_owned = Column(Integer, default=0, nullable=False)
    quantity_available = Column(Integer, default=0, nullable=False)
    quantity_rented = Column(Integer, default=0, nullable=False)

    booking_items = relationship("BookingItem", back_populates="category")

    def __repr__(self) -> str:
        return f"<ItemCategory category_id={self.category_id} item_name={self.item_name!r}>"
