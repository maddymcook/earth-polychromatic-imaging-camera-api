"""Unit tests for NASA EPIC API Service typed methods.

Tests the typed methods that return Pydantic models with validation.
"""

import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from earth_polychromatic_api.models import (
    AerosolImageMetadata,
    AerosolImagesResponse,
    AvailableDatesResponse,
    CloudImageMetadata,
    CloudImagesResponse,
    EnhancedImageMetadata,
    EnhancedImagesResponse,
    NaturalImageMetadata,
    NaturalImagesResponse,
)
from earth_polychromatic_api.service import EpicApiService

# Test data paths
TEST_DATA_DIR = Path(__file__).parent.parent.parent / "test_datasets"


@pytest.fixture
def mock_session():
    """Fixture providing a mocked requests session."""
    return Mock()


@pytest.fixture
def service(mock_session):
    """Fixture providing a configured EpicApiService instance."""
    return EpicApiService(session=mock_session)


@pytest.fixture
def natural_recent_data():
    """Load fresh natural color recent test data from real API."""
    test_file = TEST_DATA_DIR / "natural_recent_response.json"
    with test_file.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def natural_all_dates_data():
    """Load fresh natural color all dates test data from real API."""
    test_file = TEST_DATA_DIR / "natural_all_dates_response.json"
    with test_file.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def enhanced_recent_data():
    """Load fresh enhanced color recent test data from real API."""
    test_file = TEST_DATA_DIR / "enhanced_recent_response.json"
    with test_file.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def enhanced_date_data():
    """Load fresh enhanced color date test data from real API."""
    test_file = TEST_DATA_DIR / "enhanced_date_response.json"
    with test_file.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def aerosol_recent_data():
    """Load fresh aerosol index test data from real API."""
    test_file = TEST_DATA_DIR / "aerosol_recent_response.json"
    with test_file.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def cloud_recent_data():
    """Load fresh cloud fraction test data from real API."""
    test_file = TEST_DATA_DIR / "cloud_recent_response.json"
    with test_file.open(encoding="utf-8") as f:
        return json.load(f)


class TestNaturalTypedEndpoints:
    """Test natural color imagery typed endpoints with Pydantic validation."""

    def test_get_natural_recent_typed(self, service, mock_session, natural_recent_data):
        """Test retrieving most recent natural color imagery as typed models."""
        # Arrange - setup mock response with natural color test data
        mock_response = Mock()
        mock_response.json.return_value = natural_recent_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - call the typed API method
        result = service.get_natural_recent_typed()

        # Assert - verify response structure and data validation
        assert isinstance(result, NaturalImagesResponse)
        assert isinstance(result.root, list)
        assert len(result.root) > 0

        # Verify first image metadata
        first_image = result.root[0]
        assert isinstance(first_image, NaturalImageMetadata)
        assert hasattr(first_image, "identifier")
        assert hasattr(first_image, "image")
        assert hasattr(first_image, "date")

    def test_get_natural_by_date_typed(self, service, mock_session, natural_recent_data):
        """Test retrieving natural color imagery by date as typed models."""
        # Arrange - setup date parameter and mock response
        test_date = "2025-07-15"
        mock_response = Mock()
        mock_response.json.return_value = natural_recent_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - call typed method with specific date
        result = service.get_natural_by_date_typed(test_date)

        # Assert - verify date-specific natural imagery response
        assert isinstance(result, NaturalImagesResponse)
        assert len(result.root) > 0
        first_image = result.root[0]
        assert isinstance(first_image, NaturalImageMetadata)

    def test_get_natural_all_dates_typed(self, service, mock_session, natural_all_dates_data):
        """Test retrieving all available natural color dates as typed models."""
        # Arrange - setup mock response with dates list
        mock_response = Mock()
        mock_response.json.return_value = natural_all_dates_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - get all natural dates as typed models
        result = service.get_natural_all_dates_typed()

        # Assert - verify dates response structure and validation
        assert isinstance(result, AvailableDatesResponse)
        assert len(result.root) > 0
        # Verify date format validation
        first_date = result.root[0]
        assert hasattr(first_date, "date")


class TestEnhancedTypedEndpoints:
    """Test enhanced color imagery typed endpoints with Pydantic validation."""

    def test_get_enhanced_recent_typed(self, service, mock_session, enhanced_recent_data):
        """Test retrieving most recent enhanced color imagery as typed models."""
        # Arrange - setup mock response for enhanced imagery
        mock_response = Mock()
        mock_response.json.return_value = enhanced_recent_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - call enhanced typed API method
        result = service.get_enhanced_recent_typed()

        # Assert - verify enhanced imagery response with RGB naming
        assert isinstance(result, EnhancedImagesResponse)
        assert len(result.root) > 0
        first_image = result.root[0]
        assert isinstance(first_image, EnhancedImageMetadata)

    def test_get_enhanced_by_date_typed(self, service, mock_session, enhanced_date_data):
        """Test retrieving enhanced color imagery by date as typed models."""
        # Arrange - setup test date and enhanced mock response
        test_date = "2025-07-15"
        mock_response = Mock()
        mock_response.json.return_value = enhanced_date_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - call enhanced by date typed method
        result = service.get_enhanced_by_date_typed(test_date)

        # Assert - verify enhanced date-specific response
        assert isinstance(result, EnhancedImagesResponse)
        assert len(result.root) > 0
        first_image = result.root[0]
        assert isinstance(first_image, EnhancedImageMetadata)


class TestAerosolTypedEndpoints:
    """Test aerosol index imagery typed endpoints with Pydantic validation."""

    def test_get_aerosol_recent_typed(self, service, mock_session, aerosol_recent_data):
        """Test retrieving most recent aerosol index imagery as typed models."""
        # Arrange - setup aerosol data mock response
        mock_response = Mock()
        mock_response.json.return_value = aerosol_recent_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - call aerosol typed API method
        result = service.get_aerosol_recent_typed()

        # Assert - verify aerosol imagery response with UVAI naming
        assert isinstance(result, AerosolImagesResponse)
        assert len(result.root) > 0
        first_image = result.root[0]
        assert isinstance(first_image, AerosolImageMetadata)

    def test_get_aerosol_by_date_typed(self, service, mock_session, aerosol_recent_data):
        """Test retrieving aerosol index imagery by date as typed models."""
        # Arrange - setup date parameter and aerosol mock
        test_date = "2025-01-14"
        mock_response = Mock()
        mock_response.json.return_value = aerosol_recent_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - get aerosol data by date as typed models
        result = service.get_aerosol_by_date_typed(test_date)

        # Assert - verify aerosol date response validation
        assert isinstance(result, AerosolImagesResponse)
        assert len(result.root) > 0
        first_image = result.root[0]
        assert isinstance(first_image, AerosolImageMetadata)


class TestCloudTypedEndpoints:
    """Test cloud fraction imagery typed endpoints with Pydantic validation."""

    def test_get_cloud_recent_typed(self, service, mock_session, cloud_recent_data):
        """Test retrieving most recent cloud fraction imagery as typed models."""
        # Arrange - setup cloud data mock response
        mock_response = Mock()
        mock_response.json.return_value = cloud_recent_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - call cloud typed API method
        result = service.get_cloud_recent_typed()

        # Assert - verify cloud imagery response
        assert isinstance(result, CloudImagesResponse)
        assert len(result.root) > 0
        first_image = result.root[0]
        assert isinstance(first_image, CloudImageMetadata)

    def test_get_cloud_by_date_typed(self, service, mock_session, cloud_recent_data):
        """Test retrieving cloud fraction imagery by date as typed models."""
        # Arrange - setup date and cloud fraction mock
        test_date = "2025-01-14"
        mock_response = Mock()
        mock_response.json.return_value = cloud_recent_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - get cloud data by date as typed models
        result = service.get_cloud_by_date_typed(test_date)

        # Assert - verify cloud date response validation
        assert isinstance(result, CloudImagesResponse)
        assert len(result.root) > 0
        first_image = result.root[0]
        assert isinstance(first_image, CloudImageMetadata)


class TestTypedValidation:
    """Test validation behavior of typed methods."""

    def test_typed_method_empty_response(self, service, mock_session):
        """Test typed methods handle empty responses correctly."""
        # Arrange - setup empty response
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - call typed method with empty response
        result = service.get_natural_recent_typed()

        # Assert - verify empty but properly typed response
        assert isinstance(result, NaturalImagesResponse)
        assert isinstance(result.root, list)
        assert len(result.root) == 0
