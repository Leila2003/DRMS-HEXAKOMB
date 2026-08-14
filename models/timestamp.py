from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy.sql import expression, func


class Timestamp:
   

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False, server_default=expression.false(), nullable=False)
