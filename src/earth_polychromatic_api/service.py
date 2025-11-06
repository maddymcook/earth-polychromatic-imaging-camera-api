"""NASA EPIC API Service.

This module provides a high-level service for interacting with NASA's EPIC API
that returns validated Pydantic models.
"""

import requests

from .client import EpicApiClient
from .models import (
    AerosolImagesResponse,
    AvailableDatesResponse,
    CloudImagesResponse,
    EnhancedImagesResponse,
    NaturalImagesResponse,
)


class EpicApiService:
    """High-level service for NASA EPIC API with Pydantic model validation.

    This service wraps the raw EpicApiClient and provides methods that return
    validated Pydantic models with proper data transformation and validation.
    """

    def __init__(self, session: requests.Session | None = None):
        """Initialize the EPIC API service.

        Args:
            session: Optional requests session for custom configuration
        """
        self.client = EpicApiClient(session=session)

    def get_natural_recent_typed(self) -> NaturalImagesResponse:
        """Retrieve metadata for the most recent natural color imagery as typed models.

        Returns:
            NaturalImagesResponse with validated metadata models
        """
        data = self.client.get_natural_recent()
        return NaturalImagesResponse.model_validate(data)

    def get_natural_by_date_typed(self, date: str) -> NaturalImagesResponse:
        """Retrieve metadata for natural color imagery for a specific date as typed models.

        Args:
            date: Date string in YYYY-MM-DD format

        Returns:
            NaturalImagesResponse with validated metadata models
        """
        data = self.client.get_natural_by_date(date)
        return NaturalImagesResponse.model_validate(data)

    def get_natural_all_dates_typed(self) -> AvailableDatesResponse:
        """Retrieve all available dates for natural color imagery as typed models.

        Returns:
            AvailableDatesResponse with validated date models
        """
        data = self.client.get_natural_all_dates()
        return AvailableDatesResponse.model_validate(data)

    def get_enhanced_recent_typed(self) -> EnhancedImagesResponse:
        """Retrieve metadata for the most recent enhanced color imagery as typed models.

        Returns:
            EnhancedImagesResponse with validated metadata models
        """
        data = self.client.get_enhanced_recent()
        return EnhancedImagesResponse.model_validate(data)

    def get_enhanced_by_date_typed(self, date: str) -> EnhancedImagesResponse:
        """Retrieve metadata for enhanced color imagery for a specific date as typed models.

        Args:
            date: Date string in YYYY-MM-DD format

        Returns:
            EnhancedImagesResponse with validated metadata models
        """
        data = self.client.get_enhanced_by_date(date)
        return EnhancedImagesResponse.model_validate(data)

    def get_enhanced_all_dates_typed(self) -> AvailableDatesResponse:
        """Retrieve all available dates for enhanced color imagery as typed models.

        Returns:
            AvailableDatesResponse with validated date models
        """
        data = self.client.get_enhanced_all_dates()
        return AvailableDatesResponse.model_validate(data)

    def get_aerosol_recent_typed(self) -> AerosolImagesResponse:
        """Retrieve metadata for the most recent aerosol index imagery as typed models.

        Returns:
            AerosolImagesResponse with validated metadata models
        """
        data = self.client.get_aerosol_recent()
        return AerosolImagesResponse.model_validate(data)

    def get_aerosol_by_date_typed(self, date: str) -> AerosolImagesResponse:
        """Retrieve metadata for aerosol index imagery for a specific date as typed models.

        Args:
            date: Date string in YYYY-MM-DD format

        Returns:
            AerosolImagesResponse with validated metadata models
        """
        data = self.client.get_aerosol_by_date(date)
        return AerosolImagesResponse.model_validate(data)

    def get_aerosol_all_dates_typed(self) -> AvailableDatesResponse:
        """Retrieve all available dates for aerosol index imagery as typed models.

        Returns:
            AvailableDatesResponse with validated date models
        """
        data = self.client.get_aerosol_all_dates()
        return AvailableDatesResponse.model_validate(data)

    def get_cloud_recent_typed(self) -> CloudImagesResponse:
        """Retrieve metadata for the most recent cloud fraction imagery as typed models.

        Returns:
            CloudImagesResponse with validated metadata models
        """
        data = self.client.get_cloud_recent()
        return CloudImagesResponse.model_validate(data)

    def get_cloud_by_date_typed(self, date: str) -> CloudImagesResponse:
        """Retrieve metadata for cloud fraction imagery for a specific date as typed models.

        Args:
            date: Date string in YYYY-MM-DD format

        Returns:
            CloudImagesResponse with validated metadata models
        """
        data = self.client.get_cloud_by_date(date)
        return CloudImagesResponse.model_validate(data)

    def get_cloud_all_dates_typed(self) -> AvailableDatesResponse:
        """Retrieve all available dates for cloud fraction imagery as typed models.

        Returns:
            AvailableDatesResponse with validated date models
        """
        data = self.client.get_cloud_all_dates()
        return AvailableDatesResponse.model_validate(data)
