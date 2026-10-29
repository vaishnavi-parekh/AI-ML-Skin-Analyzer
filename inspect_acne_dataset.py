import cv2
import numpy as np
from datasets import load_dataset

print("Loading ACNE04...")

dataset = load_dataset(
    "Layered-Labs/ACNE04",
    split="train",
    streaming=True
)

sample = next(iter(dataset))

print("\n--- SAMPLE DETAILS ---")
print("Filename:", sample["file_name"])
print("Image size:", sample["image"].size)
print("Severity:", sample["severity"])
print("Annotated lesions:", sample["num_lesions_annotated"])
print("Bounding boxes:", sample["lesion_boxes"])

sample["image"].save("uploads/acne_sample.jpg")

# Draw the annotated acne-lesion boxes on a copy of the image.
annotated = cv2.cvtColor(np.array(sample["image"]), cv2.COLOR_RGB2BGR)
boxes = sample["lesion_boxes"]
for xmin, ymin, xmax, ymax in zip(
    boxes["xmin"], boxes["ymin"], boxes["xmax"], boxes["ymax"]
):
    cv2.rectangle(
        annotated,
        (int(xmin), int(ymin)),
        (int(xmax), int(ymax)),
        (0, 255, 0),
        2,
    )

cv2.imwrite("uploads/acne_sample_annotated.jpg", annotated)
print("\nSaved: uploads/acne_sample.jpg")
print("Annotated image saved to: uploads/acne_sample_annotated.jpg")
