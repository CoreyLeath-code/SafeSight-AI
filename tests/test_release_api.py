import io

from fastapi.testclient import TestClient
from PIL import Image

from safesight.api import app

client = TestClient(app)


def _jpeg_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (32, 24), color=(32, 64, 96)).save(buffer, format="JPEG")
    return buffer.getvalue()


def test_health_is_liveness_not_model_readiness():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "safesight-ai",
        "version": "0.1.0",
    }


def test_readiness_fails_closed_without_verified_model():
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "reason": "verified_model_unavailable",
    }


def test_predict_rejects_unsupported_media_type():
    response = client.post(
        "/predict",
        files={"file": ("payload.txt", io.BytesIO(b"not an image"), "text/plain")},
    )
    assert response.status_code == 415
    assert response.json()["detail"]["error"] == "unsupported_media_type"


def test_predict_rejects_empty_image_payload():
    response = client.post(
        "/predict",
        files={"file": ("empty.jpg", io.BytesIO(b""), "image/jpeg")},
    )
    assert response.status_code == 400


def test_predict_rejects_payload_over_configured_limit(monkeypatch):
    monkeypatch.setenv("MAX_FILE_SIZE_BYTES", "8")
    response = client.post(
        "/predict",
        files={"file": ("large.jpg", io.BytesIO(b"123456789"), "image/jpeg")},
    )
    assert response.status_code == 413


def test_predict_rejects_invalid_image_bytes():
    response = client.post(
        "/predict",
        files={"file": ("spoofed.jpg", io.BytesIO(b"not a jpeg"), "image/jpeg")},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "Uploaded file is not a valid image."


def test_valid_image_still_fails_closed_without_model():
    response = client.post(
        "/predict",
        files={"file": ("valid.jpg", io.BytesIO(_jpeg_bytes()), "image/jpeg")},
    )
    assert response.status_code == 503
    assert response.json() == {
        "detail": "Safety model is unavailable.",
        "reason": "verified_model_unavailable",
    }


def test_invalid_upload_limit_configuration_is_not_silently_accepted(monkeypatch):
    monkeypatch.setenv("MAX_FILE_SIZE_BYTES", "not-an-integer")
    try:
        response = client.post(
            "/predict",
            files={"file": ("valid.jpg", io.BytesIO(_jpeg_bytes()), "image/jpeg")},
        )
    except RuntimeError as exc:
        assert "MAX_FILE_SIZE_BYTES" in str(exc)
    else:
        assert response.status_code == 500
