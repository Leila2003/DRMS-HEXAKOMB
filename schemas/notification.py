from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, computed_field

from models.notification import NotificationGroup, NotificationType
from utils.time_utils import time_ago


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notification_id: int
    type: NotificationType
    group: NotificationGroup
    title: str
    body: str
    read: bool
    booking_id: Optional[int] = None
    category_id: Optional[int] = None
    created_at: datetime

    @computed_field
    @property
    def time(self) -> str:
        return time_ago(self.created_at)
