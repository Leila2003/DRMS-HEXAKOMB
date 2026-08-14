import enum
import uuid

from sqlalchemy import CHAR, Column, Enum, String

from database.database import Base
from models.time_stamp import TimeStamp


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STAFF = "staff"


class User(TimeStamp, Base):


    __tablename__ = "users"

    user_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STAFF, nullable=False)

    @property
    def is_active(self) -> bool:
        """Inverse of the soft-delete flag, exposed for API responses."""
        return not self.is_deleted

    def __repr__(self) -> str:
        return f"<User user_id={self.user_id} name={self.name!r} role={self.role}>"
