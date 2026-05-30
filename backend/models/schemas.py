"""
LogoForge AI - Pydantic Data Schemas.

Defines all request/response models and enumerations used across
the application for validation and serialization.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class LogoStyle(str, Enum):
    """Enumeration of all supported logo generation styles."""

    MINIMALIST = "minimalist"
    VINTAGE = "vintage"
    THREE_D = "three_d"
    GEOMETRIC = "geometric"
    GRADIENT = "gradient"
    MASCOT = "mascot"
    TYPOGRAPHIC = "typographic"
    ABSTRACT = "abstract"
    FLAT = "flat"
    HAND_DRAWN = "hand_drawn"


class GenerateRequest(BaseModel):
    """Schema for incoming logo generation requests.

    Attributes:
        prompt: Text description of the desired logo (3-500 characters).
        style: Visual style to apply to the generated logo.
        colors: Optional color palette hint (e.g. "blue and gold").
        num_images: Number of logo variations to generate (1-4).
        brand_name: Optional brand/company name to overlay on the image via
            Pillow, bypassing the AI model's unreliable text rendering.
    """

    prompt: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Text description of the desired logo",
    )
    style: LogoStyle = Field(
        default=LogoStyle.MINIMALIST,
        description="Visual style for the generated logo",
    )
    colors: Optional[str] = Field(
        default=None,
        description="Optional color palette hint, e.g. 'blue and gold'",
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=4,
        description="Number of logo variations to generate",
    )
    brand_name: Optional[str] = Field(
        default=None,
        max_length=80,
        description="Brand/company name to overlay on the generated logo",
    )


class GeneratedImage(BaseModel):
    """Schema representing a single generated logo image.

    Attributes:
        id: Unique identifier for the image.
        filename: Name of the image file on disk.
        url: Relative URL to retrieve the image.
        prompt: The original user prompt.
        style: The style that was applied.
        colors: Optional color palette that was requested.
        brand_name: Optional brand name overlaid on the image.
        created_at: ISO-8601 timestamp of generation.
    """

    id: str
    filename: str
    url: str
    prompt: str
    style: str
    colors: Optional[str] = None
    brand_name: Optional[str] = None
    created_at: str


class GenerateResponse(BaseModel):
    """Schema for the response after generating logos.

    Attributes:
        success: Whether the generation completed successfully.
        message: Human-readable status message.
        images: List of generated image metadata objects.
    """

    success: bool
    message: str
    images: list[GeneratedImage]


class GalleryResponse(BaseModel):
    """Schema for the gallery listing response.

    Attributes:
        success: Whether the gallery was fetched successfully.
        total: Total number of images in the gallery.
        images: List of all generated image metadata objects.
    """

    success: bool
    total: int
    images: list[GeneratedImage]


class ErrorResponse(BaseModel):
    """Schema for error responses.

    Attributes:
        success: Always False for error responses.
        message: Human-readable error message.
        detail: Optional detailed error information.
    """

    success: bool = False
    message: str
    detail: Optional[str] = None
