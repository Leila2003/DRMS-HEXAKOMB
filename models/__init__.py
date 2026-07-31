"""
Import every model here so that:
1. SQLAlchemy can resolve the string-based relationship() references between
   them (e.g. Booking.customer -> "Customer") no matter which module is
   imported first.
2. Base.metadata knows about all tables, which Alembic's autogenerate needs.

Usage elsewhere: `from database.database import Base` then
`import models` (or `from models import Booking, Customer, ...`).
"""

from models.booking import Booking, BookingStatus
from models.booking_item import BookingItem, ItemCondition
from models.customer import Customer
from models.itemCategory import ItemCategory
from models.user import User, UserRole

__all__ = [
    "Booking",
    "BookingStatus",
    "BookingItem",
    "ItemCondition",
    "Customer",
    "ItemCategory",
    "User",
    "UserRole",
]
