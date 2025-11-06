"""Pydantic models for NASA EPIC API responses.

This module contains data models for all NASA EPIC API response types
with comprehensive validation, type hints, and field constraints.
"""

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator, model_validator
from typing_extensions import Self


class Coordinates2D(BaseModel):
    """Geographical coordinates model with latitude and longitude validation."""

    lat: float = Field(..., ge=-90, le=90, description="Latitude in degrees (-90 to 90)")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in degrees (-180 to 180)")

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Position3D(BaseModel):
    """3D position coordinates in space (J2000 coordinate system)."""

    x: float = Field(..., description="X coordinate in kilometers")
    y: float = Field(..., description="Y coordinate in kilometers")
    z: float = Field(..., description="Z coordinate in kilometers")

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class AttitudeQuaternions(BaseModel):
    """Spacecraft attitude quaternions for orientation in space."""

    q0: float = Field(..., ge=-1, le=1, description="Quaternion scalar component")
    q1: float = Field(..., ge=-1, le=1, description="Quaternion i component")
    q2: float = Field(..., ge=-1, le=1, description="Quaternion j component")
    q3: float = Field(..., ge=-1, le=1, description="Quaternion k component")

    @model_validator(mode="after")
    def validate_quaternion_norm(self) -> Self:
        """Validate that quaternion is approximately normalized."""
        q0, q1, q2, q3 = self.q0, self.q1, self.q2, self.q3
        norm_squared = q0**2 + q1**2 + q2**2 + q3**2

        # Constants for quaternion validation
        min_norm_squared = 0.95
        max_norm_squared = 1.05

        # Allow some tolerance for floating point precision
        if not (min_norm_squared <= norm_squared <= max_norm_squared):
            actual_norm = norm_squared**0.5
            msg = f"Quaternion norm should be approximately 1, got {actual_norm}"
            raise ValueError(msg)

        return self

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class ImageryCoordinates(BaseModel):
    """Complete coordinate information for EPIC imagery."""

    centroid_coordinates: Coordinates2D = Field(
        ..., description="Earth coordinates where the satellite is looking"
    )
    dscovr_j2000_position: Position3D = Field(
        ..., description="DSCOVR satellite position in J2000 coordinate system"
    )
    lunar_j2000_position: Position3D = Field(
        ..., description="Moon position in J2000 coordinate system"
    )
    sun_j2000_position: Position3D = Field(
        ..., description="Sun position in J2000 coordinate system"
    )
    attitude_quaternions: AttitudeQuaternions = Field(
        ..., description="Satellite attitude quaternions"
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class EpicImageMetadata(BaseModel):
    """Complete metadata for an EPIC image."""

    identifier: str = Field(
        ..., min_length=14, max_length=14, description="Image identifier timestamp"
    )
    caption: str = Field(..., min_length=10, description="Image caption text")
    image: str = Field(..., min_length=5, description="Base image filename without extension")
    version: str = Field(..., pattern=r"^\d{2}$", description="Image processing version (2 digits)")
    date: datetime = Field(..., description="Image capture date and time")

    # Direct coordinate fields (duplicated in coords object)
    centroid_coordinates: Coordinates2D
    dscovr_j2000_position: Position3D
    lunar_j2000_position: Position3D
    sun_j2000_position: Position3D
    attitude_quaternions: AttitudeQuaternions

    # Nested coords object (contains same data as above fields)
    coords: ImageryCoordinates

    @field_validator("identifier")
    @classmethod
    def validate_identifier_format(cls, v: str) -> str:
        """Validate identifier follows YYYYMMDDHHMISS format."""
        if not re.match(r"^\d{14}$", v):
            msg = "Identifier must be 14 digits in YYYYMMDDHHMISS format"
            raise ValueError(msg)
        return v

    @field_validator("image")
    @classmethod
    def validate_image_name_format(cls, v: str) -> str:
        """Validate image name follows EPIC naming conventions."""
        valid_patterns = [
            r"^epic_1b_\d{14}$",  # Natural color: epic_1b_YYYYMMDDHHMISS
            r"^epic_RGB_\d{14}$",  # Enhanced color: epic_RGB_YYYYMMDDHHMISS
            r"^epic_uvai_\d{14}$",  # Aerosol index: epic_uvai_YYYYMMDDHHMISS
            r"^epic_cloudfraction_\d{14}$",  # Cloud fraction: epic_cloudfraction_YYYYMMDDHHMISS
        ]

        if not any(re.match(pattern, v) for pattern in valid_patterns):
            msg = f"Image name '{v}' does not match any valid EPIC naming convention"
            raise ValueError(msg)

        return v

    @field_validator("caption")
    @classmethod
    def validate_caption_content(cls, v: str) -> str:
        """Validate that caption contains NASA and EPIC."""
        if "NASA" not in v or "EPIC" not in v:
            msg = "Caption must contain 'NASA' and 'EPIC'"
            raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def validate_coordinate_consistency(self) -> Self:
        """Validate that direct coordinates match coords object."""
        coords_obj = self.coords
        if not coords_obj:
            return self

        # Check if direct coordinate fields match coords object
        direct_coords = {
            "centroid_coordinates": self.centroid_coordinates,
            "dscovr_j2000_position": self.dscovr_j2000_position,
            "lunar_j2000_position": self.lunar_j2000_position,
            "sun_j2000_position": self.sun_j2000_position,
            "attitude_quaternions": self.attitude_quaternions,
        }

        # Validate consistency (allowing for small floating point differences)
        for field_name, direct_value in direct_coords.items():
            if direct_value and hasattr(coords_obj, field_name):
                coords_value = getattr(coords_obj, field_name)
                if (
                    direct_value != coords_value
                    and hasattr(direct_value, "model_dump")
                    and hasattr(coords_value, "model_dump")
                    and not _coordinates_approximately_equal(
                        direct_value.model_dump(), coords_value.model_dump()
                    )
                ):
                    msg = f"Mismatch between direct {field_name} and coords.{field_name}"
                    raise ValueError(msg)

        return self

    model_config = ConfigDict(
        extra="forbid", validate_assignment=True, json_encoders={datetime: lambda v: v.isoformat()}
    )


class AvailableDate(BaseModel):
    """Model for available date entries."""

    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date in YYYY-MM-DD format")

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date string can be parsed as a valid date."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError as exc:
            msg = f"Invalid date format: {v}. Expected YYYY-MM-DD"
            raise ValueError(msg) from exc
        return v

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


# Collection-specific models for type safety
class NaturalImageMetadata(EpicImageMetadata):
    """Natural color image metadata with specific validation."""

    @field_validator("image")
    @classmethod
    def validate_natural_image_name(cls, v: str) -> str:
        """Validate natural color image naming convention."""
        if not re.match(r"^epic_1b_\d{14}$", v):
            msg = f"Natural color image name must match pattern 'epic_1b_YYYYMMDDHHMISS', got '{v}'"
            raise ValueError(msg)
        return v


class EnhancedImageMetadata(EpicImageMetadata):
    """Enhanced color image metadata with specific validation."""

    @field_validator("image")
    @classmethod
    def validate_enhanced_image_name(cls, v: str) -> str:
        """Validate enhanced color image naming convention."""
        if not re.match(r"^epic_RGB_\d{14}$", v):
            msg = (
                f"Enhanced color image name must match pattern 'epic_RGB_YYYYMMDDHHMISS', got '{v}'"
            )
            raise ValueError(msg)
        return v


class AerosolImageMetadata(EpicImageMetadata):
    """Aerosol index image metadata with specific validation."""

    @field_validator("image")
    @classmethod
    def validate_aerosol_image_name(cls, v: str) -> str:
        """Validate aerosol index image naming convention."""
        if not re.match(r"^epic_uvai_\d{14}$", v):
            msg = (
                f"Aerosol index image name must match pattern 'epic_uvai_YYYYMMDDHHMISS', got '{v}'"
            )
            raise ValueError(msg)
        return v


class CloudImageMetadata(EpicImageMetadata):
    """Cloud fraction image metadata with specific validation."""

    @field_validator("image")
    @classmethod
    def validate_cloud_image_name(cls, v: str) -> str:
        """Validate cloud fraction image naming convention."""
        if not re.match(r"^epic_cloudfraction_\d{14}$", v):
            msg = (
                f"Cloud fraction image name must match pattern "
                f"'epic_cloudfraction_YYYYMMDDHHMISS', got '{v}'"
            )
            raise ValueError(msg)
        return v


# Response models (lists of the above)
class NaturalImagesResponse(RootModel[list[NaturalImageMetadata]]):
    """Response model for natural color imagery endpoints."""

    root: list[NaturalImageMetadata] = Field(..., min_length=0)

    def __iter__(self):
        """Iterate over items."""
        return iter(self.root)

    def __getitem__(self, item: int) -> NaturalImageMetadata:
        """Get item by index."""
        return self.root[item]

    def __len__(self) -> int:
        """Return length."""
        return len(self.root)


class EnhancedImagesResponse(RootModel[list[EnhancedImageMetadata]]):
    """Response model for enhanced color imagery endpoints."""

    root: list[EnhancedImageMetadata] = Field(..., min_length=0)

    def __iter__(self):
        """Iterate over items."""
        return iter(self.root)

    def __getitem__(self, item: int) -> EnhancedImageMetadata:
        """Get item by index."""
        return self.root[item]

    def __len__(self) -> int:
        """Return length."""
        return len(self.root)


class AerosolImagesResponse(RootModel[list[AerosolImageMetadata]]):
    """Response model for aerosol index imagery endpoints."""

    root: list[AerosolImageMetadata] = Field(..., min_length=0)

    def __iter__(self):
        """Iterate over items."""
        return iter(self.root)

    def __getitem__(self, item: int) -> AerosolImageMetadata:
        """Get item by index."""
        return self.root[item]

    def __len__(self) -> int:
        """Return length."""
        return len(self.root)


class CloudImagesResponse(RootModel[list[CloudImageMetadata]]):
    """Response model for cloud fraction imagery endpoints."""

    root: list[CloudImageMetadata] = Field(..., min_length=0)

    def __iter__(self):
        """Iterate over items."""
        return iter(self.root)

    def __getitem__(self, item: int) -> CloudImageMetadata:
        """Get item by index."""
        return self.root[item]

    def __len__(self) -> int:
        """Return length."""
        return len(self.root)


class AvailableDatesResponse(RootModel[list[AvailableDate]]):
    """Response model for available dates endpoints."""

    root: list[AvailableDate] = Field(..., min_length=0)

    def __iter__(self):
        """Iterate over items."""
        return iter(self.root)

    def __getitem__(self, item: int) -> AvailableDate:
        """Get item by index."""
        return self.root[item]

    def __len__(self) -> int:
        """Return length."""
        return len(self.root)


# Helper functions
def _coordinates_approximately_equal(coord1: dict, coord2: dict, tolerance: float = 1e-6) -> bool:
    """Check if two coordinate dictionaries are approximately equal within tolerance."""
    if set(coord1.keys()) != set(coord2.keys()):
        return False

    for key, val1 in coord1.items():
        val2 = coord2[key]
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            if abs(val1 - val2) > tolerance:
                return False
        elif val1 != val2:
            return False

    return True
