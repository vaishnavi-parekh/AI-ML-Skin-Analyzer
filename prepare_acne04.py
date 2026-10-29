"""Convert the downloaded ACNE04 Hugging Face dataset to YOLO format."""
from pathlib import Path
import gc

from datasets import load_from_disk


ROOT = Path(__file__).parent
SOURCE = ROOT / "datasets" / "ACNE04"
DEST = ROOT / "datasets" / "acne04_yolo"


def write_row(row, index, split_name):
    image_dir = DEST / "images" / split_name
    label_dir = DEST / "labels" / split_name
    image_dir.mkdir(parents=True, exist_ok=True)
    label_dir.mkdir(parents=True, exist_ok=True)

    image = row["image"].convert("RGB")
    width, height = image.size
    stem = f"acne04_{index:04d}"
    image_path = image_dir / f"{stem}.jpg"
    label_path = label_dir / f"{stem}.txt"
    if image_path.exists() and label_path.exists():
        return False
    image.save(image_path, quality=90)
    boxes = row["lesion_boxes"]
    lines = []
    for xmin, ymin, xmax, ymax in zip(
        boxes["xmin"], boxes["ymin"], boxes["xmax"], boxes["ymax"]
    ):
        x_center = ((xmin + xmax) / 2) / width
        y_center = ((ymin + ymax) / 2) / height
        box_width = (xmax - xmin) / width
        box_height = (ymax - ymin) / height
        lines.append(f"0 {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}")
    label_path.write_text("\n".join(lines), encoding="utf-8")
    image.close()
    return True


def main():
    dataset = load_from_disk(str(SOURCE))["train"]
    counts = {"train": 0, "val": 0}
    for index, row in enumerate(dataset):
        split_name = "train" if row["split"] == "train" else "val"
        if write_row(row, index, split_name):
            counts[split_name] += 1
        if index % 25 == 0:
            gc.collect()
    # Keep the YAML portable: Colab, Windows, and Drive all resolve the
    # image folders relative to this file's directory.
    yaml = """path: .
train: images/train
val: images/val
names:
  0: Acne
"""
    (DEST / "data.yaml").write_text(yaml, encoding="utf-8")
    print(f"Prepared {counts['train']} training and {counts['val']} validation images in {DEST}")


if __name__ == "__main__":
    main()
