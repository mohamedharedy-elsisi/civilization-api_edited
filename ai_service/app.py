from __future__ import annotations

import logging
import os
from typing import Any

import gradio as gr
import spaces
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import inference


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
if MAX_UPLOAD_BYTES <= 0:
    raise ValueError("MAX_UPLOAD_BYTES must be greater than zero")


@spaces.GPU(duration=60)
def _run_detector(image):
    return inference.detect(image)


def _make_prediction(image) -> dict[str, Any]:
    return inference.prediction_response(image, _run_detector)


def _gradio_predict(image) -> dict[str, Any]:
    if image is None:
        return {"success": False, "error": "Upload an image to scan."}
    try:
        return _make_prediction(image)
    except inference.InvalidImageError as exc:
        return {"success": False, "error": str(exc)}
    except inference.ModelUnavailableError:
        return {"success": False, "error": "The AI service is not ready. Please try again later."}
    except Exception:
        logger.exception("Gradio artifact prediction failed")
        return {"success": False, "error": "Prediction failed. Please try again."}


app = FastAPI(title="Egyptian Artifact Inference API")

allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOW_ORIGINS", "").split(",")
    if origin.strip()
]
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        allow_credentials=False,
    )


@app.middleware("http")
async def limit_prediction_request_size(request, call_next):
    if request.url.path == "/api/predict":
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > MAX_UPLOAD_BYTES + 128 * 1024:
                    return JSONResponse(
                        status_code=413,
                        content={"error": "Image file exceeds the upload limit."},
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid Content-Length header."},
                )
    return await call_next(request)


@app.get("/health")
def health() -> JSONResponse:
    loaded = inference.model_is_loaded()
    return JSONResponse(
        status_code=200 if loaded else 503,
        content={
            "status": "ok" if loaded else "unavailable",
            "model_loaded": loaded,
            "catalog_loaded": inference.catalog_is_loaded(),
        },
    )


@app.post("/api/predict")
async def predict_api(image: UploadFile | None = File(default=None)) -> JSONResponse:
    if image is None:
        return JSONResponse(
            status_code=400,
            content={"error": "No image uploaded"},
        )

    try:
        image_bytes = await image.read(MAX_UPLOAD_BYTES + 1)
        if len(image_bytes) > MAX_UPLOAD_BYTES:
            return JSONResponse(
                status_code=413,
                content={"error": "Image file exceeds the upload limit."},
            )
        decoded = inference.decode_image(image_bytes)
    except inference.InvalidImageError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception:
        logger.exception("Uploaded image could not be read")
        return JSONResponse(
            status_code=400,
            content={"error": "The uploaded image could not be read."},
        )
    finally:
        await image.close()

    try:
        return JSONResponse(content=_make_prediction(decoded))
    except inference.ModelUnavailableError:
        return JSONResponse(
            status_code=503,
            content={"error": "The AI service is not ready. Please try again later."},
        )
    except inference.InvalidImageError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception:
        logger.exception("Artifact prediction failed")
        return JSONResponse(
            status_code=500,
            content={"error": "Prediction failed. Please try again."},
        )


demo = gr.Interface(
    fn=_gradio_predict,
    inputs=gr.Image(type="pil", label="Artifact image"),
    outputs=gr.JSON(label="Prediction"),
    title="Egyptian Artifact Detector",
    description="Upload an Egyptian artifact image to identify it.",
    api_name="predict",
)
demo.queue(default_concurrency_limit=1, max_size=16)

app = gr.mount_gradio_app(
    app,
    demo,
    path="/",
    max_file_size=MAX_UPLOAD_BYTES,
    show_error=False,
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "7860")),
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )
