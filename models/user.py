import enum
import uuid

from sqlalchemy import Column, Enum, String
from sqlalchemy.dialects.postgresql import UUID

from database.database import Base
from models.timestamp import Timestamp


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STAFF = "staff"


class User(Timestamp, Base):



    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STAFF, nullable=False)

    def __repr__(self) -> str:
        return f"<User user_id={self.user_id} name={self.name!r} role={self.role}>"
