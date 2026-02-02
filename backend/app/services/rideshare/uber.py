"""Uber rideshare service integration."""

import httpx
from typing import Optional

from app.models.coordinates import Coordinates
from app.models.estimate import TransportEstimate, TransportMode
from app.services.base import TransportationService
from app.services.exceptions import ServiceUnavailableError, AuthenticationError
from app.config import get_settings


class UberService:
    """Uber rideshare service for price estimates and deep linking."""

    service_id = "uber"
    service_name = "Uber"
    BASE_URL = "https://test-api.uber.com/v1.2"  # Using test environment for development

    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the Uber service.

        Args:
            access_token: Optional Uber OAuth access token (Bearer type).
                         If not provided, falls back to the token from environment config.

        Note:
            Uber uses OAuth 2.0 Bearer tokens, not server tokens.
            Access tokens expire after 30 days.
        """
        self.access_token = access_token or get_settings().uber_access_token
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """
        Get or create the HTTP client for Uber API requests.

        Implements lazy initialization - the client is only created when
        first accessed, not during __init__.

        Returns:
            Configured httpx.AsyncClient instance
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                    "Accept-Language": "en_US"
                },
                timeout=10.0
            )
        return self._client

    async def get_estimates(
        self,
        origin: Coordinates,
        destination: Coordinates
    ) -> list[TransportEstimate]:
        """
        Fetch price and time estimates from Uber for a trip.

        Args:
            origin: Starting point coordinates
            destination: Ending point coordinates

        Returns:
            List of TransportEstimate objects (one per Uber product type like UberX, UberXL)

        Raises:
            AuthenticationError: If access token is invalid or expired
            ServiceUnavailableError: If Uber API is unreachable or returns an error
        """
        # Step 1: Build query parameters from coordinates
        params = {
            "start_latitude": origin.lat,
            "start_longitude": origin.lng,
            "end_latitude": destination.lat,
            "end_longitude": destination.lng
        }

        try:
            # Step 2: Make GET request to Uber API
            response = await self.client.get("/estimates/price", params=params)

            # Step 3: Handle HTTP status codes
            if response.status_code == 401:
                raise AuthenticationError(
                    self.service_id,
                    "Invalid or expired access token"
                )
            elif response.status_code == 422:
                # No products available for this route
                return []
            elif response.status_code != 200:
                raise ServiceUnavailableError(
                    self.service_id,
                    f"API returned status code {response.status_code}"
                )

            # Step 4: Parse JSON response
            data = response.json()
            prices = data.get("prices", [])

            # Step 5: Convert each price to TransportEstimate
            estimates = []
            for price in prices:
                estimate = TransportEstimate(
                    service_id=self.service_id,
                    service_name=self.service_name,
                    product_id=price["product_id"],
                    product_name=price["display_name"],
                    mode=TransportMode.RIDESHARE,
                    price_min=price.get("low_estimate", 0),
                    price_max=price.get("high_estimate", 0),
                    price_display=price.get("estimate", "N/A"),
                    currency=price.get("currency_code", "USD"),
                    duration_minutes=int(price.get("duration", 0) / 60),  # Convert seconds to minutes
                    deep_link_url=self._generate_deep_link(origin, destination),
                    deep_link_fallback=self._generate_web_link(origin, destination)
                )
                estimates.append(estimate)

            return estimates

        except httpx.RequestError as e:
            # Network error (connection failed, timeout, etc.)
            raise ServiceUnavailableError(
                self.service_id,
                f"Network error: {str(e)}"
            )

    def _generate_deep_link(self, origin: Coordinates, destination: Coordinates) -> str:
        """
        Generate Uber app deep link for the trip.

        Args:
            origin: Starting point coordinates
            destination: Ending point coordinates

        Returns:
            Deep link URL that opens the Uber app
        """
        # TODO: Implement in Step 4
        return f"uber://?action=setPickup&pickup[latitude]={origin.lat}&pickup[longitude]={origin.lng}&dropoff[latitude]={destination.lat}&dropoff[longitude]={destination.lng}"

    def _generate_web_link(self, origin: Coordinates, destination: Coordinates) -> str:
        """
        Generate Uber web fallback link for the trip.

        Args:
            origin: Starting point coordinates
            destination: Ending point coordinates

        Returns:
            Web URL that opens Uber in browser
        """
        # TODO: Implement in Step 4
        return f"https://m.uber.com/ul/?action=setPickup&pickup[latitude]={origin.lat}&pickup[longitude]={origin.lng}&dropoff[latitude]={destination.lat}&dropoff[longitude]={destination.lng}"
