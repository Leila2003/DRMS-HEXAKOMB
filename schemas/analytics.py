from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class WeekBucket(BaseModel):
    label: str
    count: int


class TopCategory(BaseModel):
    category_id: UUID
    name: str
    icon: Optional[str] = None
    count: int


class AnalyticsSummary(BaseModel):
    revenue: int
    revenue_label: str
    active_rentals: int
    most_rented_category: Optional[str] = None
    avg_rental_duration_days: float
    weekly_bookings: List[WeekBucket]
    top_categories: List[TopCategory]
