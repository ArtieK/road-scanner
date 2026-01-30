"""Geographic coordinates model with validation."""

from pydantic import BaseModel, field_validator


class Coordinates(BaseModel):
    """Geographic coordinates with validation."""

    lat: float
    lng: float

    @field_validator('lat')
    @classmethod
    def validate_lat(cls, v: float) -> float:
        """Validate latitude is between -90 and 90."""
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @field_validator('lng')
    @classmethod
    def validate_lng(cls, v: float) -> float:
        """Validate longitude is between -180 and 180."""
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v
