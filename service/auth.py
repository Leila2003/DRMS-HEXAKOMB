import os
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from models import User, UserRole
from models.business import Business
from schemas.auth import BusinessRegisterRequest, UserCreate, UserUpdate
from utils.security import hash_password, verify_password



DEFAULT_SUPER_ADMIN_NAME = os.getenv("SUPER_ADMIN_NAME", "Super Admin")
DEFAULT_SUPER_ADMIN_EMAIL = os.getenv("SUPER_ADMIN_EMAIL", "leilamugeni@gmail.com")
DEFAULT_SUPER_ADMIN_PHONE = os.getenv("SUPER_ADMIN_PHONE")
DEFAULT_SUPER_ADMIN_PASSWORD = os.getenv("SUPER_ADMIN_PASSWORD", "mugeni@123")


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email, User.is_deleted.is_(False)).first()
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


def register_business(db: Session, payload: BusinessRegisterRequest) -> tuple[Business, User]:
    """Public self-service signup: creates the Business and its owner
    (business_admin) account together, atomically."""
   
    if db.query(User).filter(User.email == payload.owner_email).first():
        raise ValueError("A user with this email already exists")

    business = Business(
        name=payload.business_name,
        # email=payload.business_email,
        phone=payload.business_phone,
    )
    db.add(business)
    db.flush()  # get business.business_id without committing yet

    owner = User(
        name=payload.owner_name,
        email=payload.owner_email,
        phone=payload.owner_phone,
        password_hash=hash_password(payload.owner_password),
        role=UserRole.BUSINESS_ADMIN,
        business_id=business.business_id,
    )
    db.add(owner)
    db.commit()
    db.refresh(business)
    db.refresh(owner)
    return business, owner


def create_staff_user(db: Session, payload: UserCreate, business_id) -> User:
    """Create a staff account scoped to the calling business_admin's business.
    business_id always comes from the authenticated admin's token/user — never
    from the request body."""
    user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=UserRole.STAFF,
        business_id=business_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def seed_default_super_admin(db: Session) -> None:
    """Ensure a platform super_admin exists. Idempotent."""
    has_super_admin = db.query(User).filter(User.role == UserRole.SUPER_ADMIN).first()
    if has_super_admin is not None:
        return

    existing = db.query(User).filter(User.email == DEFAULT_SUPER_ADMIN_EMAIL).first()
    if existing is not None:
        return

    admin = User(
        name=DEFAULT_SUPER_ADMIN_NAME,
        email=DEFAULT_SUPER_ADMIN_EMAIL,
        phone=DEFAULT_SUPER_ADMIN_PHONE,
        password_hash=hash_password(DEFAULT_SUPER_ADMIN_PASSWORD),
        role=UserRole.SUPER_ADMIN,
        business_id=None,
    )
    db.add(admin)
    db.commit()


def list_staff_users(db: Session, business_id: Optional[object]) -> List[User]:
   
    query = db.query(User).filter(User.role == UserRole.STAFF)
    if business_id is not None:
        query = query.filter(User.business_id == business_id)
    return query.order_by(User.name).all()


def get_user(db: Session, user_id) -> Optional[User]:
    return db.get(User, user_id)


def get_staff_user_in_business(db: Session, user_id, business_id) -> Optional[User]:
    user = get_user(db, user_id)
    if user is None or user.role != UserRole.STAFF or user.business_id != business_id:
        return None
    return user


def update_staff_user(db: Session, user_id, business_id, payload: UserUpdate) -> Optional[User]:
    user = get_staff_user_in_business(db, user_id, business_id)
    if user is None:
        return None

    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        user.name = data["name"]
    if "phone" in data and data["phone"] is not None:
        user.phone = data["phone"]
    if "is_active" in data and data["is_active"] is not None:
        user.is_deleted = not data["is_active"]
        user.deleted_at = None if data["is_active"] else datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)
    return user


def deactivate_staff_user(db: Session, user_id, business_id) -> Optional[User]:
    user = get_staff_user_in_business(db, user_id, business_id)
    if user is None:
        return None
    user.is_deleted = True
    user.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


def delete_staff_user(db: Session, user_id, business_id) -> bool:
    user = get_staff_user_in_business(db, user_id, business_id)
    if user is None:
        return False
    db.delete(user)
    db.commit()
    return True