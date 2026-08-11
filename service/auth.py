from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from models import User, UserRole
from schemas.auth import UserCreate, UserUpdate
from utils.security import hash_password, verify_password

# The single admin account is created from code, not from env vars or a
# signup endpoint. There is only ever one admin; every other account made
# through the API (POST /auth/users) is forced to UserRole.STAFF.
DEFAULT_ADMIN_NAME = "Leila Mugeni"
DEFAULT_ADMIN_EMAIL = "leilamugeni@gmail.com"
DEFAULT_ADMIN_PHONE = "0789139940"
DEFAULT_ADMIN_PASSWORD = "Mugeni@123"


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email, User.is_deleted.is_(False)).first()
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


def create_user(db: Session, payload: UserCreate, role: Optional[UserRole] = None) -> User:
    """Create a user. `role` overrides payload.role when the caller must not
    trust the client-supplied role (e.g. the staff-creation endpoint)."""
    user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=role if role is not None else payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def seed_default_admin(db: Session) -> None:
    """Ensure the single hardcoded admin account exists. Idempotent: does
    nothing once an admin is present, so it's safe to call on every startup."""
    has_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if has_admin is not None:
        return

    existing = db.query(User).filter(User.email == DEFAULT_ADMIN_EMAIL).first()
    if existing is not None:
        return

    admin = User(
        name=DEFAULT_ADMIN_NAME,
        email=DEFAULT_ADMIN_EMAIL,
        phone=DEFAULT_ADMIN_PHONE,
        password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
        role=UserRole.ADMIN,
    )
    db.add(admin)
    db.commit()


def list_staff_users(db: Session) -> List[User]:
    """Admin-facing directory of staff accounts (the admin itself is excluded
    since it isn't managed through this list)."""
    return (
        db.query(User)
        .filter(User.role == UserRole.STAFF)
        .order_by(User.name)
        .all()
    )


def get_user(db: Session, user_id) -> Optional[User]:
    return db.get(User, user_id)


def update_staff_user(db: Session, user_id, payload: UserUpdate) -> Optional[User]:
    user = get_user(db, user_id)
    if user is None or user.role != UserRole.STAFF:
        return None

    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        user.name = data["name"]
    if "phone" in data and data["phone"] is not None:
        user.phone = data["phone"]
    if "password" in data and data["password"] is not None:
        user.password_hash = hash_password(data["password"])
    if "is_active" in data and data["is_active"] is not None:
        user.is_deleted = not data["is_active"]
        user.deleted_at = None if data["is_active"] else datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)
    return user


def deactivate_staff_user(db: Session, user_id) -> Optional[User]:
    """Soft-deletes (deactivates) a staff account. Refuses to touch admins."""
    user = get_user(db, user_id)
    if user is None or user.role != UserRole.STAFF:
        return None

    user.is_deleted = True
    user.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user
