"""Transportation estimate models."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class TransportMode(str, Enum):
    """Transportation mode categories."""

    RIDESHARE = "rideshare"
    BIKE_SHARE = "bike_share"
    SCOOTER = "scooter"
    TRANSIT = "transit"


class TransportEstimate(BaseModel):
    """Unified estimate model for all transportation services."""

    # Identification
    service_id: str
    service_name: str
    product_id: str
    product_name: str
    mode: TransportMode

    # Pricing
    price_min: float
    price_max: float
    price_display: str
    currency: str = "USD"

    # Time
    duration_minutes: int
    wait_time_minutes: Optional[int] = None

    # Distance
    walking_distance_meters: Optional[int] = None

    # Deep linking
    deep_link_url: str
    deep_link_fallback: Optional[str] = None

    # Availability
    is_available: bool = True
    availability_message: Optional[str] = None
