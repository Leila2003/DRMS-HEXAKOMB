from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CustomerCreate(BaseModel):
    name: str
    contact: str
    referral_name: Optional[str] = None
    referral_phone: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    nationalID_Photo: Optional[str] = None
    referral_name: Optional[str] = None
    referral_phone: Optional[str] = None


class CustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: int
    name: str
    contact: str
    nationalID_Photo: Optional[str] = None
    referral_name: Optional[str] = None
    referral_phone: Optional[str] = None
    created_at: datetime
