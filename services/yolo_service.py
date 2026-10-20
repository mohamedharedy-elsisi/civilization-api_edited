from ultralytics import YOLO
import os

MODEL_PATH = os.path.join("weights", "best.pt")

model = YOLO(MODEL_PATH)


def predict(image_path):
    results = model(image_path, conf=0.05)

    if len(results) == 0:
        return None

    result = results[0]

    if len(result.boxes) == 0:
        return None

    box = result.boxes[0]

    class_id = int(box.cls[0])
    confidence = float(box.conf[0])

    class_name = model.names[class_id]

    return {
        "class": class_name,
        "confidence": round(confidence, 3)
    }