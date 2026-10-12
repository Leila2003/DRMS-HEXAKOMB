import enum
import uuid

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.database import Base
from models.timestamp import Timestamp


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"      
    BUSINESS_ADMIN = "business_admin" 
    STAFF = "staff"                    


class User(Timestamp, Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STAFF, nullable=False)

   
    business_id = Column(
        UUID(as_uuid=True), ForeignKey("businesses.business_id"), nullable=True, index=True
    )
    business = relationship("Business", backref="users")

    @property
    def is_active(self) -> bool:
        return not self.is_deleted

    @property
    def business_name(self):
        return self.business.name if self.business is not None else None

    def __repr__(self) -> str:
        return f"<User user_id={self.user_id} name={self.name!r} role={self.role}>"