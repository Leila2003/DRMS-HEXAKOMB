import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from database.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STAFF = "staff"


class User(Base):
    """An admin/staff account that logs into the dashboard (not a rental customer)."""

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.STAFF, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    # soft delete: non-null means this row is treated as removed
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def __repr__(self) -> str:
        return f"<User user_id={self.user_id} name={self.name!r} role={self.role}>"
