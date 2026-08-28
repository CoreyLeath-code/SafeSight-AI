"""FastAPI boundary for the release-supported SafeSight v0.1.0 surface."""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from . import __version__
from .image_validation import InvalidImageError, validate_image_bytes

logger = logging.getLogger(__name__)

DEFAULT_MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_CONTENT_TYPES = frozenset({"image/jpeg", "image/png", "image/webp", "image/bmp"})


def _max_upload_bytes() -> int:
    raw = os.getenv("MAX_FILE_SIZE_BYTES", str(DEFAULT_MAX_UPLOAD_BYTES))
    try:
        value = int(raw)
    except ValueError as exc:
        raise RuntimeError("MAX_FILE_SIZE_BYTES must be an integer") from exc
    if value <= 0:
        raise RuntimeError("MAX_FILE_SIZE_BYTES must be greater than zero")
    return value


app = FastAPI(
    title="SafeSight AI",
    description=(
        "Evidence-bounded image-validation and safety-policy reference API. "
        "v0.1.0 intentionally ships without a verified safety model."
    ),
    version=__version__,
)


@app.get("/health")
def health() -> dict[str, str]:
    """Return process liveness; this does not imply model readiness."""
    return {"status": "ok", "service": "safesight-ai", "version": __version__}


@app.get("/ready")
def ready() -> JSONResponse:
    """Fail closed because v0.1.0 contains no verified model artifact."""
    return JSONResponse(
        status_code=503,
        content={"status": "not_ready", "reason": "verified_model_unavailable"},
    )


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> JSONResponse:
    """Validate an image request and fail closed before any fabricated inference."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail={
                "error": "unsupported_media_type",
                "allowed": sorted(ALLOWED_CONTENT_TYPES),
            },
        )

    limit = _max_upload_bytes()
    try:
        payload = await file.read(limit + 1)
    finally:
        await file.close()

    if not payload:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(payload) > limit:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the configured {limit}-byte upload limit.",
        )

    try:
        metadata = validate_image_bytes(payload)
    except InvalidImageError as exc:
        logger.info("Rejected undecodable image payload: %s", exc)
        raise HTTPException(status_code=422, detail="Uploaded file is not a valid image.") from exc

    logger.warning(
        "Validated %s image (%dx%d), but no verified safety model is packaged.",
        metadata.format,
        metadata.width,
        metadata.height,
    )
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Safety model is unavailable.",
            "reason": "verified_model_unavailable",
        },
    )
