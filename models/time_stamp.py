from sqlalchemy import Column, DateTime, Boolean
from datetime import datetime

# Class for timestamps
class TimeStamp:
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True, default=None)