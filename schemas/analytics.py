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
    total_revenue: int  # item amounts across all bookings (caution excluded)
    revenue_gained: int  # item amounts from returned/damaged (closed) bookings
    caution_held: int  # deposits on open bookings, refundable to customers
    caution_refunded: int  # deposits given back to customers at return
    caution_kept: int  # deposits retained by the business at return
    active_rentals: int
    most_rented_category: Optional[str] = None
    avg_rental_duration_days: float
    weekly_bookings: List[WeekBucket]
    top_categories: List[TopCategory]


class TopBusiness(BaseModel):
    business_id: UUID
    name: str
    bookings_count: int
    revenue: int


class PlatformAnalyticsSummary(BaseModel):
   

    total_businesses: int
    active_businesses: int
    total_staff: int
    total_bookings: int
    total_revenue: int
    active_rentals: int
    top_businesses: List[TopBusiness]
