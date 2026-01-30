"""Base protocols for transportation service integrations."""

from typing import Protocol, runtime_checkable
from app.models.coordinates import Coordinates
from app.models.estimate import TransportEstimate


@runtime_checkable
class TransportationService(Protocol):
    """Protocol for all transportation service integrations."""

    service_id: str
    service_name: str

    async def get_estimates(
        self,
        origin: Coordinates,
        destination: Coordinates
    ) -> list[TransportEstimate]:
        """
        Fetch price/time estimates for a trip.

        Args:
            origin: Starting point coordinates
            destination: Ending point coordinates

        Returns:
            List of TransportEstimate objects (one per product type)

        Raises:
            ServiceUnavailableError: If the service API is down
            AuthenticationError: If credentials are invalid
            RateLimitError: If API rate limits are exceeded
        """
        ...


@runtime_checkable
class MicromobilityService(TransportationService, Protocol):
    """Extended protocol for bike/scooter shares with station data."""

    async def get_nearby_stations(
        self,
        location: Coordinates,
        radius_meters: int = 500
    ) -> list[dict]:
        """
        Find stations near a location with availability info.

        Args:
            location: Geographic coordinates to search near
            radius_meters: Search radius in meters (default: 500)

        Returns:
            List of station dictionaries with location and availability data
        """
        ...

    async def get_station_availability(
        self,
        station_id: str
    ) -> dict:
        """
        Get real-time availability for a specific station.

        Args:
            station_id: Unique identifier for the station

        Returns:
            Dictionary with availability data (bikes available, docks available, etc.)
        """
        ...
