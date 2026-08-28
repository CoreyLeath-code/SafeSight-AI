import io

from fastapi.testclient import TestClient
from PIL import Image

from api.main import app

client = TestClient(app)


def _make_jpeg_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (64, 64), color=(128, 0, 0)).save(buffer, format="JPEG")
    return buffer.getvalue()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "safesight-ai",
        "version": "0.1.0",
    }


def test_ready_fails_closed_without_model():
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json()["reason"] == "verified_model_unavailable"


def test_predict_no_file_returns_422():
    response = client.post("/predict")
    assert response.status_code == 422


def test_predict_unsupported_type_returns_415():
    response = client.post(
        "/predict",
        files={"file": ("malware.exe", io.BytesIO(b"not an image"), "application/octet-stream")},
    )
    assert response.status_code == 415


def test_predict_empty_file_returns_400():
    response = client.post(
        "/predict",
        files={"file": ("empty.jpg", io.BytesIO(b""), "image/jpeg")},
    )
    assert response.status_code == 400


def test_predict_valid_image_fails_closed_without_model():
    response = client.post(
        "/predict",
        files={"file": ("test.jpg", io.BytesIO(_make_jpeg_bytes()), "image/jpeg")},
    )
    assert response.status_code == 503
    assert response.json() == {
        "detail": "Safety model is unavailable.",
        "reason": "verified_model_unavailable",
    }


def test_predict_invalid_image_bytes_return_422():
    response = client.post(
        "/predict",
        files={"file": ("spoofed.jpg", io.BytesIO(b"not an image"), "image/jpeg")},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "Uploaded file is not a valid image."
