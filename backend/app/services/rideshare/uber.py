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
