from flask import Blueprint, request, jsonify
from services.yolo_service import predict
import os
import uuid
import json

predict_bp = Blueprint("predict", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATA_FILES = [
    "datafiles/temples.json",
    "datafiles/statues.json",
    "datafiles/pharaohs.json",
    "datafiles/museums.json",
    "datafiles/obelisks.json",
    "datafiles/pyramids.json",
]


def find_artifact(name):
    all_data = []

    for file in DATA_FILES:
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                all_data.extend(json.load(f))

    return next(
        (item for item in all_data if item["name"] == name),
        None
    )


@predict_bp.route("/api/predict", methods=["POST"])
def predict_artifact():

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]

    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    image.save(filepath)

    result = predict(filepath)

    os.remove(filepath)

    if result is None:
        return jsonify({
            "success": False,
            "message": "No artifact detected"
        })

    artifact = find_artifact(result["class"])

    return jsonify({
        "success": True,
        "prediction": result,
        "artifact": artifact
    })