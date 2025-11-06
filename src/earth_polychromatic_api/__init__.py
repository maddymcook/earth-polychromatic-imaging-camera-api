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

try:
    from ._version import version as __version__
except ImportError:
    # Fallback for development installations without git tags
    __version__ = "0.0.0+unknown"
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
