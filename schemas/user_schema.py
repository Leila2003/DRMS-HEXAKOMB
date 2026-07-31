from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional

class UserTypeEnum(str, Enum):
    CUSTOMER = "CUSTOMER"
    SHOP_KEEPER = "SHOP KEEPER"
    OWNER = "OWNER"
    ADMIN = "ADMIN"