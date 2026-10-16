import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from database.database import Base
from models.timestamp import Timestamp


class Business(Timestamp, Base):
    __tablename__ = "businesses"

    business_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=True)

    @property
    def is_active(self) -> bool:
        return not self.is_deleted

    def __repr__(self) -> str:
        return f"<Business business_id={self.business_id} name={self.name!r}>"