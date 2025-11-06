"""Unit tests for NASA EPIC API Client.

Tests all endpoints using pytest with mocked responses and test data.
"""

import json
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests

from earth_polychromatic_api.client import EpicApiClient

# Test data paths
TEST_DATA_DIR = Path(__file__).parent / "test_datasets"


@pytest.fixture
def mock_session():
    """Fixture providing a mocked requests session."""
    return Mock(spec=requests.Session)


@pytest.fixture
def client(mock_session):
    """Fixture providing an EpicApiClient with mocked session."""
    return EpicApiClient(session=mock_session)


@pytest.fixture
def natural_recent_data():
    """Fixture providing test data for natural recent imagery."""
    with open(TEST_DATA_DIR / "natural_recent_response.json") as f:
        return json.load(f)


@pytest.fixture
def enhanced_date_data():
    """Fixture providing test data for enhanced imagery by date."""
    with open(TEST_DATA_DIR / "enhanced_date_response.json") as f:
        return json.load(f)


@pytest.fixture
def natural_all_dates_data():
    """Fixture providing test data for all natural imagery dates."""
    with open(TEST_DATA_DIR / "natural_all_dates_response.json") as f:
        return json.load(f)


@pytest.fixture
def aerosol_recent_data():
    """Fixture providing test data for aerosol recent imagery."""
    with open(TEST_DATA_DIR / "aerosol_recent_response.json") as f:
        return json.load(f)


@pytest.fixture
def cloud_recent_data():
    """Fixture providing test data for cloud recent imagery."""
    with open(TEST_DATA_DIR / "cloud_recent_response.json") as f:
        return json.load(f)


@pytest.fixture
def enhanced_all_dates_data():
    """Fixture providing test data for all enhanced imagery dates."""
    with open(TEST_DATA_DIR / "enhanced_all_dates_response.json") as f:
        return json.load(f)


@pytest.fixture
def aerosol_all_dates_data():
    """Fixture providing test data for all aerosol imagery dates."""
    with open(TEST_DATA_DIR / "aerosol_all_dates_response.json") as f:
        return json.load(f)


@pytest.fixture
def cloud_all_dates_data():
    """Fixture providing test data for all cloud imagery dates."""
    with open(TEST_DATA_DIR / "cloud_all_dates_response.json") as f:
        return json.load(f)


class TestNaturalEndpoints:
    """Test natural color imagery endpoints."""

    def test_get_natural_recent(self, client, mock_session, natural_recent_data, monkeypatch):
        """Test retrieving most recent natural color imagery metadata.

        Verifies the API call to /natural endpoint returns expected metadata structure
        with proper image identifiers, coordinates, and satellite position data.
        """
        # Arrange - setup mock response with test data
        mock_response = Mock()
        mock_response.json.return_value = natural_recent_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - call the API method
        result = client.get_natural_recent()

        # Assert - verify correct API call and response structure
        mock_session.get.assert_called_once_with("https://epic.gsfc.nasa.gov/api/natural")
        mock_response.raise_for_status.assert_called_once()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["image"] == "epic_1b_20231105001234"
        assert result[0]["centroid_coordinates"]["lat"] == -12.345678
        assert result[1]["date"] == "2023-11-05 03:45:23"

    def test_get_natural_by_date(self, client, mock_session, enhanced_date_data, monkeypatch):
        """Test retrieving natural color imagery metadata for a specific date.

        Tests the /natural/date/{date} endpoint with YYYY-MM-DD format date parameter
        and validates the returned metadata structure matches expected format.
        """
        # Arrange - setup mock response and test parameters
        test_date = "2023-10-31"
        mock_response = Mock()
        mock_response.json.return_value = enhanced_date_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - call the API method with specific date
        result = client.get_natural_by_date(test_date)

        # Assert - verify correct API call with date parameter
        expected_url = f"https://epic.gsfc.nasa.gov/api/natural/date/{test_date}"
        mock_session.get.assert_called_once_with(expected_url)
        mock_response.raise_for_status.assert_called_once()

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["image"] == "epic_RGB_20231031123456"
        assert result[0]["centroid_coordinates"]["lon"] == 123.456789

    def test_get_natural_all_dates(self, client, mock_session, natural_all_dates_data, monkeypatch):
        """Test retrieving all available dates for natural color imagery.

        Validates the /natural/all endpoint returns a list of date objects
        and verifies the date format structure in the response.
        """
        # Arrange - setup mock response with dates list
        mock_response = Mock()
        mock_response.json.return_value = natural_all_dates_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - call the API method
        result = client.get_natural_all_dates()

        # Assert - verify API call and response format
        mock_session.get.assert_called_once_with("https://epic.gsfc.nasa.gov/api/natural/all")
        mock_response.raise_for_status.assert_called_once()

        assert isinstance(result, list)
        assert len(result) == 7
        assert result[0]["date"] == "2023-11-05"
        assert result[-1]["date"] == "2023-10-30"


class TestEnhancedEndpoints:
    """Test enhanced color imagery endpoints."""

    def test_get_enhanced_recent(self, client, mock_session, enhanced_date_data, monkeypatch):
        """Test retrieving most recent enhanced color imagery metadata.

        Verifies the /enhanced endpoint returns enhanced imagery data with proper
        RGB composite image identifiers and metadata structure.
        """
        # Arrange - setup mock response for enhanced imagery
        mock_response = Mock()
        mock_response.json.return_value = enhanced_date_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - call the enhanced imagery API method
        result = client.get_enhanced_recent()

        # Assert - verify enhanced endpoint call and RGB image format
        mock_session.get.assert_called_once_with("https://epic.gsfc.nasa.gov/api/enhanced")
        mock_response.raise_for_status.assert_called_once()

        assert isinstance(result, list)
        assert len(result) == 1
        assert "RGB" in result[0]["image"]
        assert result[0]["version"] == "02"

    def test_get_enhanced_by_date(self, client, mock_session, enhanced_date_data, monkeypatch):
        """Test retrieving enhanced color imagery metadata for a specific date.

        Tests the /enhanced/date/{date} endpoint with date parameter and validates
        the enhanced imagery metadata structure and RGB image naming convention.
        """
        # Arrange - setup test date and mock response
        test_date = "2023-10-31"
        mock_response = Mock()
        mock_response.json.return_value = enhanced_date_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - call enhanced by date method
        result = client.get_enhanced_by_date(test_date)

        # Assert - verify enhanced date endpoint and image format
        expected_url = f"https://epic.gsfc.nasa.gov/api/enhanced/date/{test_date}"
        mock_session.get.assert_called_once_with(expected_url)
        mock_response.raise_for_status.assert_called_once()

        assert isinstance(result, list)
        assert result[0]["image"].startswith("epic_RGB_")
        assert result[0]["caption"].find("Enhanced color") != -1

    def test_get_enhanced_all_dates(
        self, client, mock_session, enhanced_all_dates_data, monkeypatch
    ):
        """Test retrieving all available dates for enhanced color imagery.

        Validates the /enhanced/all endpoint returns a properly formatted list
        of available dates for enhanced color imagery collection.
        """
        # Arrange - setup mock response with enhanced dates
        mock_response = Mock()
        mock_response.json.return_value = enhanced_all_dates_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - get all enhanced dates
        result = client.get_enhanced_all_dates()

        # Assert - verify enhanced all dates endpoint
        mock_session.get.assert_called_once_with("https://epic.gsfc.nasa.gov/api/enhanced/all")
        mock_response.raise_for_status.assert_called_once()

        assert isinstance(result, list)
        assert len(result) == 5
        assert all("date" in item for item in result)


class TestAerosolEndpoints:
    """Test aerosol index imagery endpoints."""

    def test_get_aerosol_recent(self, client, mock_session, aerosol_recent_data, monkeypatch):
        """Test retrieving most recent aerosol index imagery metadata.

        Verifies the /aerosol endpoint returns aerosol measurement data with
        proper UVAI (UV Aerosol Index) image identifiers and atmospheric data.
        """
        # Arrange - setup aerosol data mock response
        mock_response = Mock()
        mock_response.json.return_value = aerosol_recent_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - call aerosol recent API method
        result = client.get_aerosol_recent()

        # Assert - verify aerosol endpoint and UVAI image format
        mock_session.get.assert_called_once_with("https://epic.gsfc.nasa.gov/api/aerosol")
        mock_response.raise_for_status.assert_called_once()

        assert isinstance(result, list)
        assert len(result) == 1
        assert "uvai" in result[0]["image"]
        assert result[0]["caption"].find("Aerosol index") != -1

    def test_get_aerosol_by_date(self, client, mock_session, aerosol_recent_data, monkeypatch):
        """Test retrieving aerosol index imagery metadata for a specific date.

        Tests the /aerosol/date/{date} endpoint with date parameter and validates
        aerosol measurement metadata structure and UVAI image naming.
        """
        # Arrange - setup date parameter and aerosol mock
        test_date = "2023-11-05"
        mock_response = Mock()
        mock_response.json.return_value = aerosol_recent_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - get aerosol data by date
        result = client.get_aerosol_by_date(test_date)

        # Assert - verify aerosol date endpoint call
        expected_url = f"https://epic.gsfc.nasa.gov/api/aerosol/date/{test_date}"
        mock_session.get.assert_called_once_with(expected_url)
        mock_response.raise_for_status.assert_called_once()

        assert isinstance(result, list)
        assert result[0]["image"].startswith("epic_uvai_")
        assert result[0]["centroid_coordinates"]["lat"] == -34.567890

    def test_get_aerosol_all_dates(self, client, mock_session, aerosol_all_dates_data, monkeypatch):
        """Test retrieving all available dates for aerosol index imagery.

        Validates the /aerosol/all endpoint returns available dates for
        aerosol index measurements with proper date format structure.
        """
        # Arrange - setup aerosol all dates mock response
        mock_response = Mock()
        mock_response.json.return_value = aerosol_all_dates_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - get all aerosol measurement dates
        result = client.get_aerosol_all_dates()

        # Assert - verify aerosol all dates endpoint
        mock_session.get.assert_called_once_with("https://epic.gsfc.nasa.gov/api/aerosol/all")
        mock_response.raise_for_status.assert_called_once()

        assert isinstance(result, list)
        assert len(result) == 4
        assert result[0]["date"] == "2023-11-05"


class TestCloudEndpoints:
    """Test cloud fraction imagery endpoints."""

    def test_get_cloud_recent(self, client, mock_session, cloud_recent_data, monkeypatch):
        """Test retrieving most recent cloud fraction imagery metadata.

        Verifies the /cloud endpoint returns cloud coverage measurement data
        with proper cloud fraction image identifiers and meteorological metadata.
        """
        # Arrange - setup cloud data mock response
        mock_response = Mock()
        mock_response.json.return_value = cloud_recent_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - call cloud recent API method
        result = client.get_cloud_recent()

        # Assert - verify cloud endpoint and image format
        mock_session.get.assert_called_once_with("https://epic.gsfc.nasa.gov/api/cloud")
        mock_response.raise_for_status.assert_called_once()

        assert isinstance(result, list)
        assert len(result) == 1
        assert "cloudfraction" in result[0]["image"]
        assert result[0]["caption"].find("Cloud fraction") != -1

    def test_get_cloud_by_date(self, client, mock_session, cloud_recent_data, monkeypatch):
        """Test retrieving cloud fraction imagery metadata for a specific date.

        Tests the /cloud/date/{date} endpoint with date parameter and validates
        cloud fraction measurement metadata and image naming convention.
        """
        # Arrange - setup date and cloud fraction mock
        test_date = "2023-11-05"
        mock_response = Mock()
        mock_response.json.return_value = cloud_recent_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - get cloud data by date
        result = client.get_cloud_by_date(test_date)

        # Assert - verify cloud date endpoint call
        expected_url = f"https://epic.gsfc.nasa.gov/api/cloud/date/{test_date}"
        mock_session.get.assert_called_once_with(expected_url)
        mock_response.raise_for_status.assert_called_once()

        assert isinstance(result, list)
        assert result[0]["image"].startswith("epic_cloudfraction_")
        assert result[0]["centroid_coordinates"]["lon"] == -156.789012

    def test_get_cloud_all_dates(self, client, mock_session, cloud_all_dates_data, monkeypatch):
        """Test retrieving all available dates for cloud fraction imagery.

        Validates the /cloud/all endpoint returns available dates for
        cloud fraction measurements with proper date listing format.
        """
        # Arrange - setup cloud all dates mock response
        mock_response = Mock()
        mock_response.json.return_value = cloud_all_dates_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Act - get all cloud measurement dates
        result = client.get_cloud_all_dates()

        # Assert - verify cloud all dates endpoint
        mock_session.get.assert_called_once_with("https://epic.gsfc.nasa.gov/api/cloud/all")
        mock_response.raise_for_status.assert_called_once()

        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["date"] == "2023-11-05"


class TestImageUrlBuilder:
    """Test image URL construction functionality."""

    def test_build_image_url_png(self, client, monkeypatch):
        """Test building archive URL for PNG format images.

        Verifies the image URL construction follows the proper archive directory
        structure and generates correct PNG download URLs with proper file paths.
        """
        # Arrange - setup image parameters for PNG format
        collection = "natural"
        date = "2023-11-05"
        image_name = "epic_1b_20231105001234"
        format_type = "png"

        # Act - build the archive URL
        result = client.build_image_url(collection, date, image_name, format_type)

        # Assert - verify correct PNG URL structure
        expected_url = (
            "https://epic.gsfc.nasa.gov/archive/natural/2023/11/05/png/epic_1b_20231105001234.png"
        )
        assert result == expected_url

    def test_build_image_url_jpg(self, client, monkeypatch):
        """Test building archive URL for JPG format images.

        Validates JPG format URL construction with proper file extension
        and directory path structure for half-resolution images.
        """
        # Arrange - setup parameters for JPG format
        collection = "enhanced"
        date = "2023-10-31"
        image_name = "epic_RGB_20231031123456"
        format_type = "jpg"

        # Act - build JPG archive URL
        result = client.build_image_url(collection, date, image_name, format_type)

        # Assert - verify correct JPG URL structure
        expected_url = (
            "https://epic.gsfc.nasa.gov/archive/enhanced/2023/10/31/jpg/epic_RGB_20231031123456.jpg"
        )
        assert result == expected_url

    def test_build_image_url_thumbs(self, client, monkeypatch):
        """Test building archive URL for thumbnail images.

        Tests thumbnail format URL construction which uses JPG extension
        but in the thumbs directory for smaller preview images.
        """
        # Arrange - setup parameters for thumbnail format
        collection = "aerosol"
        date = "2023-11-05"
        image_name = "epic_uvai_20231105001122"
        format_type = "thumbs"

        # Act - build thumbnail archive URL
        result = client.build_image_url(collection, date, image_name, format_type)

        # Assert - verify thumbnail URL uses jpg extension in thumbs directory
        expected_url = "https://epic.gsfc.nasa.gov/archive/aerosol/2023/11/05/thumbs/epic_uvai_20231105001122.jpg"
        assert result == expected_url

    def test_build_image_url_default_png(self, client, monkeypatch):
        """Test building archive URL with default PNG format.

        Verifies that when no format_type is specified, the method defaults
        to PNG format and constructs the URL accordingly.
        """
        # Arrange - setup parameters without explicit format (defaults to PNG)
        collection = "cloud"
        date = "2023-11-05"
        image_name = "epic_cloudfraction_20231105002233"

        # Act - build URL with default format
        result = client.build_image_url(collection, date, image_name)

        # Assert - verify default PNG format is used
        expected_url = "https://epic.gsfc.nasa.gov/archive/cloud/2023/11/05/png/epic_cloudfraction_20231105002233.png"
        assert result == expected_url


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_api_error_handling(self, client, mock_session, monkeypatch):
        """Test proper handling of HTTP errors from API responses.

        Verifies that HTTP errors are properly propagated when the API
        returns error status codes and raise_for_status is called.
        """
        # Arrange - setup mock to raise HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_session.get.return_value = mock_response

        # Act & Assert - verify error is properly raised
        with pytest.raises(requests.HTTPError):
            client.get_natural_recent()

        mock_response.raise_for_status.assert_called_once()

    def test_session_initialization_default(self, monkeypatch):
        """Test default session initialization when none provided.

        Verifies that when no session is provided to the constructor,
        a default requests.Session instance is created and used.
        """
        # Arrange & Act - create client without session parameter
        client = EpicApiClient()

        # Assert - verify default session is created
        assert client.session is not None
        assert isinstance(client.session, requests.Session)

    def test_session_initialization_custom(self, mock_session, monkeypatch):
        """Test custom session initialization when provided.

        Validates that when a custom session is provided to the constructor,
        that specific session instance is used instead of creating a new one.
        """
        # Arrange & Act - create client with custom session
        client = EpicApiClient(session=mock_session)

        # Assert - verify custom session is used
        assert client.session is mock_session
