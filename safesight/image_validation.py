"""Image payload validation used before any model invocation."""

from __future__ import annotations

import io
from dataclasses import dataclass

from PIL import Image, UnidentifiedImageError


class InvalidImageError(ValueError):
    """Raised when uploaded bytes cannot be decoded as a supported image."""


@dataclass(frozen=True)
class ImageMetadata:
    """Minimal decoded image metadata safe to expose to callers/tests."""

    format: str
    width: int
    height: int


def validate_image_bytes(payload: bytes) -> ImageMetadata:
    """Decode and verify image bytes without performing model inference."""
    if not payload:
        raise InvalidImageError("image payload is empty")
    try:
        with Image.open(io.BytesIO(payload)) as image:
            image_format = image.format or "UNKNOWN"
            width, height = image.size
            image.verify()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise InvalidImageError("payload is not a decodable image") from exc

    if width <= 0 or height <= 0:
        raise InvalidImageError("image dimensions must be positive")
    return ImageMetadata(format=image_format, width=width, height=height)
