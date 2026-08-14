from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, computed_field

from models.notification import NotificationGroup, NotificationType
from utils.time_utils import time_ago


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notification_id: str
    type: NotificationType
    group: NotificationGroup
    title: str
    body: str
    read: bool
    booking_id: Optional[str] = None
    category_id: Optional[str] = None
    created_at: datetime

    @computed_field
    @property
    def time(self) -> str:
        return time_ago(self.created_at)
