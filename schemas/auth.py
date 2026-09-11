from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from models.user import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    # role: UserRole = UserRole.STAFF


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole
    is_active: bool
    business_id: Optional[UUID] = None
    created_at: datetime


class BusinessRegisterRequest(BaseModel):
    """Public endpoint payload: a shop owner signing themselves up."""
    business_name: str
    business_phone: Optional[str] = None

    owner_name: str
    owner_email: EmailStr
    owner_phone: Optional[str] = None
    owner_password: str


class BusinessRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    business_id: UUID
    name: str
    phone: Optional[str] = None
    created_at: datetime


class BusinessRegisterResponse(BaseModel):
    business: BusinessRead
    owner: UserRead