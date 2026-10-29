
import cv2
from pathlib import Path

# Locate the image inside the uploads folder
image_path = Path("uploads/face.jpg")

# Read the image
image = cv2.imread(str(image_path))

# Check whether the image was loaded
if image is None:
    print("Error: Could not read the image.")
else:
    print("Image loaded successfully!")
    print("Image dimensions:", image.shape)

    # Save a copy of the image
    output_path = "uploads/face_copy.jpg"
    cv2.imwrite(output_path, image)

    print("Image copy saved to:", output_path)
