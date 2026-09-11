from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class BusinessAdminRead(BaseModel):
   

    business_id: UUID
    name: str
    phone: Optional[str] = None
    is_active: bool
    created_at: datetime
    owner_name: Optional[str] = None
    owner_email: Optional[EmailStr] = None
    staff_count: int
