"""Earth Polychromatic API Package.

A Python client for NASA's Earth Polychromatic Imaging Camera (EPIC) API.
"""

from .client import EpicApiClient
from .models import (
    AerosolImageMetadata,
    AerosolImagesResponse,
    AttitudeQuaternions,
    AvailableDate,
    AvailableDatesResponse,
    CloudImageMetadata,
    CloudImagesResponse,
    Coordinates2D,
    EnhancedImageMetadata,
    EnhancedImagesResponse,
    EpicImageMetadata,
    ImageryCoordinates,
    NaturalImageMetadata,
    NaturalImagesResponse,
    Position3D,
)
from .service import EpicApiService

__version__ = "1.0.0"
__all__ = [
    "AerosolImageMetadata",
    "AerosolImagesResponse",
    "AttitudeQuaternions",
    "AvailableDate",
    "AvailableDatesResponse",
    "CloudImageMetadata",
    "CloudImagesResponse",
    "Coordinates2D",
    "EnhancedImageMetadata",
    "EnhancedImagesResponse",
    "EpicApiClient",
    "EpicApiService",
    "EpicImageMetadata",
    "ImageryCoordinates",
    "NaturalImageMetadata",
    "NaturalImagesResponse",
    "Position3D",
]
