# tests/integration/test_api.py
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from api.main import app

client = TestClient(app)


def _make_jpeg_bytes() -> bytes:
    """Create a minimal valid JPEG image in memory."""
    buf = io.BytesIO()
    Image.new("RGB", (64, 64), color=(128, 0, 0)).save(buf, format="JPEG")
    return buf.getvalue()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_predict_no_file_returns_422():
    """POST /predict without a file should return 422 Unprocessable Entity."""
    response = client.post("/predict")
    assert response.status_code == 422


def test_predict_unsupported_type_returns_415():
    """POST /predict with a non-image file should return 415."""
    fake_file = io.BytesIO(b"not an image")
    response = client.post(
        "/predict",
        files={"file": ("malware.exe", fake_file, "application/octet-stream")},
    )
    assert response.status_code == 415


def test_predict_empty_file_returns_400():
    """POST /predict with an empty image file should return 400."""
    empty_file = io.BytesIO(b"")
    response = client.post(
        "/predict",
        files={"file": ("empty.jpg", empty_file, "image/jpeg")},
    )
    assert response.status_code == 400


def test_predict_valid_image_fails_closed_without_model():
    """A valid image must not receive a fabricated low-risk safety classification."""
    jpeg_bytes = _make_jpeg_bytes()
    response = client.post(
        "/predict",
        files={"file": ("test.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Safety model is unavailable."



def test_predict_invalid_image_bytes_return_422():
    response = client.post(
        "/predict",
        files={"file": ("spoofed.jpg", io.BytesIO(b"not an image"), "image/jpeg")},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Uploaded file is not a valid image."
