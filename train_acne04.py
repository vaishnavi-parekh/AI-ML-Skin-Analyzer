"""Fine-tune the existing acne detector on ACNE04.

The original model_V1.pt is kept unchanged. The new weights are written under
runs/detect/acne04_finetuned/weights/best.pt after training.
"""
from pathlib import Path
import os

from ultralytics import YOLO


ROOT = Path(__file__).parent
DATA = ROOT / "datasets" / "acne04_yolo" / "data.yaml"
BASE_MODEL = ROOT / "models" / "model_V1.pt"


def main():
    if not DATA.exists():
        raise FileNotFoundError("Run prepare_acne04.py first.")
    model = YOLO(str(BASE_MODEL))
    # Ultralytics uses the available CUDA GPU automatically when device is
    # omitted.  ACNE_DEVICE can still override this (for example, "cpu" or
    # "0" in Colab).
    device = os.getenv("ACNE_DEVICE") or None
    model.train(
        data=str(DATA),
        epochs=int(os.getenv("ACNE_EPOCHS", "15")),
        imgsz=int(os.getenv("ACNE_IMGSZ", "512")),
        batch=int(os.getenv("ACNE_BATCH", "-1")),
        device=device,
        workers=0,
        patience=5,
        project=str(ROOT / "runs" / "detect"),
        name="acne04_finetuned",
        exist_ok=True,
        pretrained=True,
        plots=True,
    )


if __name__ == "__main__":
    main()
