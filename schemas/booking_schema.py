from pydantic import BaseModel, model_validator
from enum import Enum
from datetime import date, datetime

class BookingStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    CANCELLED = "CANCELLED"