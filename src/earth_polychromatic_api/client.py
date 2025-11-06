"""NASA EPIC API Client.

This module provides a client for interacting with NASA's Earth Polychromatic
Imaging Camera (EPIC) API to retrieve Earth imagery and metadata.
"""

from typing import Any, cast

import requests


class EpicApiClient:
    """Client for NASA EPIC API.

    Provides methods to retrieve natural, enhanced, aerosol, and cloud imagery
    metadata from the DSCOVR EPIC instrument.
    """

    BASE_URL = "https://epic.gsfc.nasa.gov/api"
    ARCHIVE_BASE_URL = "https://epic.gsfc.nasa.gov/archive"

    def __init__(self, session: requests.Session | None = None):
        """Initialize the EPIC API client.

        Args:
            session: Optional requests session for custom configuration
        """
        self.session = session or requests.Session()

    def get_natural_recent(self) -> list[dict[str, Any]]:
        """Retrieve metadata for the most recent natural color imagery.

        Returns:
            List of dictionaries containing image metadata
        """
        url = f"{self.BASE_URL}/natural"
        response = self.session.get(url)
        response.raise_for_status()
        return cast("list[dict[str, Any]]", response.json())

    def get_natural_by_date(self, date: str) -> list[dict[str, Any]]:
        """Retrieve metadata for natural color imagery for a specific date.

        Args:
            date: Date string in YYYY-MM-DD format

        Returns:
            List of dictionaries containing image metadata
        """
        url = f"{self.BASE_URL}/natural/date/{date}"
        response = self.session.get(url)
        response.raise_for_status()
        return cast("list[dict[str, Any]]", response.json())

    def get_natural_all_dates(self) -> list[dict[str, str]]:
        """Retrieve a listing of all dates with available natural color imagery.

        Returns:
            List of dictionaries with date keys
        """
        url = f"{self.BASE_URL}/natural/all"
        response = self.session.get(url)
        response.raise_for_status()
        return cast("list[dict[str, str]]", response.json())

    def get_enhanced_recent(self) -> list[dict[str, Any]]:
        """
        Retrieve metadata for the most recent enhanced color imagery.

        Returns:
            List of dictionaries containing image metadata
        """
        url = f"{self.BASE_URL}/enhanced"
        response = self.session.get(url)
        response.raise_for_status()
        return cast("list[dict[str, Any]]", response.json())

    def get_enhanced_by_date(self, date: str) -> list[dict[str, Any]]:
        """
        Retrieve metadata for enhanced color imagery for a specific date.

        Args:
            date: Date string in YYYY-MM-DD format

        Returns:
            List of dictionaries containing image metadata
        """
        url = f"{self.BASE_URL}/enhanced/date/{date}"
        response = self.session.get(url)
        response.raise_for_status()
        return cast("list[dict[str, Any]]", response.json())

    def get_enhanced_all_dates(self) -> list[dict[str, str]]:
        """
        Retrieve a listing of all dates with available enhanced color imagery.

        Returns:
            List of dictionaries with date keys
        """
        url = f"{self.BASE_URL}/enhanced/all"
        response = self.session.get(url)
        response.raise_for_status()
        return cast("list[dict[str, str]]", response.json())

    def get_aerosol_recent(self) -> list[dict[str, Any]]:
        """
        Retrieve metadata for the most recent aerosol index imagery.

        Returns:
            List of dictionaries containing image metadata
        """
        url = f"{self.BASE_URL}/aerosol"
        response = self.session.get(url)
        response.raise_for_status()
        return cast("list[dict[str, Any]]", response.json())

    def get_aerosol_by_date(self, date: str) -> list[dict[str, Any]]:
        """
        Retrieve metadata for aerosol index imagery for a specific date.

        Args:
            date: Date string in YYYY-MM-DD format

        Returns:
            List of dictionaries containing image metadata
        """
        url = f"{self.BASE_URL}/aerosol/date/{date}"
        response = self.session.get(url)
        response.raise_for_status()
        return cast("list[dict[str, Any]]", response.json())

    def get_aerosol_all_dates(self) -> list[dict[str, str]]:
        """
        Retrieve a listing of all dates with available aerosol index imagery.

        Returns:
            List of dictionaries with date keys
        """
        url = f"{self.BASE_URL}/aerosol/all"
        response = self.session.get(url)
        response.raise_for_status()
        return cast("list[dict[str, str]]", response.json())

    def get_cloud_recent(self) -> list[dict[str, Any]]:
        """
        Retrieve metadata for the most recent cloud fraction imagery.

        Returns:
            List of dictionaries containing image metadata
        """
        url = f"{self.BASE_URL}/cloud"
        response = self.session.get(url)
        response.raise_for_status()
        return cast("list[dict[str, Any]]", response.json())

    def get_cloud_by_date(self, date: str) -> list[dict[str, Any]]:
        """
        Retrieve metadata for cloud fraction imagery for a specific date.

        Args:
            date: Date string in YYYY-MM-DD format

        Returns:
            List of dictionaries containing image metadata
        """
        url = f"{self.BASE_URL}/cloud/date/{date}"
        response = self.session.get(url)
        response.raise_for_status()
        return cast("list[dict[str, Any]]", response.json())

    def get_cloud_all_dates(self) -> list[dict[str, str]]:
        """
        Retrieve a listing of all dates with available cloud fraction imagery.

        Returns:
            List of dictionaries with date keys
        """
        url = f"{self.BASE_URL}/cloud/all"
        response = self.session.get(url)
        response.raise_for_status()
        return cast("list[dict[str, str]]", response.json())

    def build_image_url(
        self, collection: str, date: str, image_name: str, format_type: str = "png"
    ) -> str:
        """
        Build the full URL for downloading an image from the archive.

        Args:
            collection: Image collection type (natural, enhanced, aerosol, cloud)
            date: Date string in YYYY-MM-DD format
            image_name: Base image name without extension
            format_type: Image format (png, jpg, thumbs)

        Returns:
            Complete URL for image download
        """
        year, month, day = date.split("-")

        # Add appropriate extension based on format
        filename = f"{image_name}.png" if format_type == "png" else f"{image_name}.jpg"

        return f"{self.ARCHIVE_BASE_URL}/{collection}/{year}/{month}/{day}/{format_type}/{filename}"
