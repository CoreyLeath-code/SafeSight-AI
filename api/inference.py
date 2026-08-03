# api/inference.py
import io
import logging
from typing import Any, Dict

from PIL import Image

logger = logging.getLogger(__name__)


class ModelUnavailableError(RuntimeError):
    """Raised when no verified safety model is available for inference."""



def run_inference(image_tensor: Any, model: Any) -> Any:
    """Run model inference on a pre-processed image tensor.

    Args:
        image_tensor: Tensor produced by the preprocessing step.
        model: A loaded ML model with a ``predict`` method.

    Returns:
        Raw model predictions.
    """
    predictions = model.predict(image_tensor)
    return predictions


def predict(image_bytes: bytes) -> Dict[str, Any]:
    """Accept raw image bytes and return a risk prediction dictionary.

    Opens and validates the image with Pillow. A safety classification is never
    fabricated when no verified model artifact is available.

    Args:
        image_bytes: Raw bytes of the uploaded image file.

    Returns:
        A dict containing ``risk_level`` and ``confidence`` keys.

    Raises:
        ValueError: If the image cannot be opened or decoded.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()
    except Exception as exc:
        raise ValueError(f"Invalid image data: {exc}") from exc

    logger.warning("Inference requested without a verified safety model.")
    raise ModelUnavailableError("No verified safety model is available.")
