from __future__ import annotations

import logging
import os
import threading
import warnings
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
from typing import Any, Callable

import requests
from huggingface_hub import hf_hub_download
from PIL import Image, ImageOps, UnidentifiedImageError
from ultralytics import YOLO


logger = logging.getLogger(__name__)

MAX_IMAGE_PIXELS = int(os.getenv("MAX_IMAGE_PIXELS", "20000000"))
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}
DEFAULT_DATA_API_URL = "https://civilization-api.vercel.app"
CATALOG_ENDPOINTS = (
    "obelisks",
    "pharaohs",
    "statues",
    "temples",
    "museums",
    "pyramids",
)


class InvalidImageError(ValueError):
    """Raised when an upload is not a supported, decodable image."""


class ModelUnavailableError(RuntimeError):
    """Raised when the configured detector could not be loaded."""


_model: YOLO | None = None
_model_error: Exception | None = None
_model_lock = threading.Lock()
_catalog: dict[str, dict[str, Any]] = {}
_catalog_loaded = False
_catalog_lock = threading.Lock()


def _resolve_model_path() -> Path:
    model_path = os.getenv("MODEL_PATH", "").strip()
    if model_path:
        path = Path(model_path).expanduser()
        if not path.is_absolute():
            path = Path(__file__).resolve().parent / path
        if not path.is_file():
            raise FileNotFoundError("Configured MODEL_PATH does not exist")
        return path.resolve()

    repository_id = os.getenv("HF_MODEL_REPO_ID", "").strip()
    if not repository_id:
        raise FileNotFoundError("Configure MODEL_PATH or HF_MODEL_REPO_ID")

    filename = os.getenv("HF_MODEL_FILENAME", "best.pt").strip() or "best.pt"
    revision = os.getenv("HF_MODEL_REVISION", "main").strip() or "main"
    token = os.getenv("HF_TOKEN", "").strip() or None
    downloaded_path = hf_hub_download(
        repo_id=repository_id,
        filename=filename,
        revision=revision,
        token=token,
        repo_type="model",
    )
    return Path(downloaded_path)


def initialize_model() -> None:
    """Load the YOLO model once during service startup."""
    global _model, _model_error

    with _model_lock:
        if _model is not None:
            return

        try:
            model_path = _resolve_model_path()
            loaded_model = YOLO(str(model_path))
            if os.getenv("USE_ZERO_GPU", "false").strip().lower() == "true":
                loaded_model.to("cuda")
            _model = loaded_model
            _model_error = None
            logger.info("YOLO model initialized")
        except Exception as exc:  # Keep the app and health route available for recovery.
            _model_error = exc
            logger.exception("YOLO model initialization failed")


def model_is_loaded() -> bool:
    return _model is not None


def decode_image(image_bytes: bytes) -> Image.Image:
    if not image_bytes:
        raise InvalidImageError("The uploaded file is empty.")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(image_bytes)) as source:
                image_format = source.format
                source.verify()
            if image_format not in ALLOWED_IMAGE_FORMATS:
                raise InvalidImageError("Upload a JPEG, PNG, or WebP image.")

            with Image.open(BytesIO(image_bytes)) as source:
                if source.width * source.height > MAX_IMAGE_PIXELS:
                    raise InvalidImageError("The image dimensions are too large.")
                source.load()
                return ImageOps.exif_transpose(source).convert("RGB")
    except InvalidImageError:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as exc:
        raise InvalidImageError("The uploaded file is not a valid supported image.") from exc


def normalize_image(image: Image.Image) -> Image.Image:
    if not isinstance(image, Image.Image):
        raise InvalidImageError("Choose a valid image to scan.")
    if image.width <= 0 or image.height <= 0:
        raise InvalidImageError("The image has invalid dimensions.")
    if image.width * image.height > MAX_IMAGE_PIXELS:
        raise InvalidImageError("The image dimensions are too large.")
    return ImageOps.exif_transpose(image).convert("RGB")


def detect(image: Image.Image) -> dict[str, Any] | None:
    if _model is None:
        raise ModelUnavailableError("The AI model is not available.") from _model_error

    normalized_image = normalize_image(image)
    with _model_lock:
        results = _model(normalized_image, conf=0.05, verbose=False)

    if not results or results[0].boxes is None or len(results[0].boxes) == 0:
        return None

    box = results[0].boxes[0]
    class_id = int(box.cls[0].item())
    confidence = float(box.conf[0].item())
    names = _model.names
    class_name = names[class_id] if isinstance(names, (list, tuple)) else names[class_id]
    return {"class": str(class_name), "confidence": round(confidence, 3)}


def _fetch_catalog_section(endpoint: str) -> list[dict[str, Any]]:
    base_url = os.getenv("CIVILIZATION_API_BASE_URL", DEFAULT_DATA_API_URL).strip().rstrip("/")
    if not base_url:
        return []

    response = requests.get(
        f"{base_url}/api/{endpoint}",
        timeout=(2, 4),
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list):
        raise ValueError(f"The {endpoint} catalog response was not a list")
    return [item for item in data if isinstance(item, dict)]


def load_catalog() -> None:
    """Load artifact metadata from the Data API once; inference still works if it is down."""
    global _catalog, _catalog_loaded

    with _catalog_lock:
        if _catalog_loaded:
            return
        _catalog_loaded = True

        collected: dict[str, dict[str, Any]] = {}
        with ThreadPoolExecutor(max_workers=len(CATALOG_ENDPOINTS)) as executor:
            futures = {
                executor.submit(_fetch_catalog_section, endpoint): endpoint
                for endpoint in CATALOG_ENDPOINTS
            }
            for future, endpoint in futures.items():
                try:
                    items = future.result()
                except Exception as exc:
                    logger.warning("Could not load the %s catalog: %s", endpoint, exc)
                    continue
                for item in items:
                    name = item.get("name")
                    if isinstance(name, str):
                        collected[name] = item

        _catalog = collected


def catalog_is_loaded() -> bool:
    return _catalog_loaded


def artifact_details(class_name: str) -> dict[str, Any] | None:
    load_catalog()
    return _catalog.get(class_name)


def prediction_response(
    image: Image.Image,
    detector: Callable[[Image.Image], dict[str, Any] | None],
) -> dict[str, Any]:
    prediction = detector(normalize_image(image))
    if prediction is None:
        return {"success": False, "message": "No artifact detected"}

    return {
        "success": True,
        "prediction": prediction,
        "artifact": artifact_details(str(prediction["class"])),
    }


initialize_model()
