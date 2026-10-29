import cv2
import mediapipe as mp
from pathlib import Path

# File paths
image_path = Path("uploads/face.jpg")
model_path = Path("models/face_landmarker.task")
output_path = Path("uploads/face_landmarks.jpg")

# Check that the required files exist
if not image_path.exists():
    raise FileNotFoundError(f"Image not found: {image_path}")
if not model_path.exists():
    raise FileNotFoundError(f"Model not found: {model_path}")

# Load the image
image = cv2.imread(str(image_path))
if image is None:
    raise ValueError("OpenCV could not read the image.")

# Convert BGR (OpenCV format) to RGB
rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Prepare the MediaPipe image
mp_image = mp.Image(
    image_format=mp.ImageFormat.SRGB,
    data=rgb_image,
)

# Configure the face landmarker
options = mp.tasks.vision.FaceLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
    running_mode=mp.tasks.vision.RunningMode.IMAGE,
    num_faces=1,
)

# Detect facial landmarks
with mp.tasks.vision.FaceLandmarker.create_from_options(options) as landmarker:
    result = landmarker.detect(mp_image)

# Check the result
if not result.face_landmarks:
    print("No face detected. Try a clear, front-facing image.")
else:
    print("Face detected successfully!")
    print("Number of facial landmarks:", len(result.face_landmarks[0]))

    # Draw the detected landmark points
    for landmark in result.face_landmarks[0]:
        x = int(landmark.x * image.shape[1])
        y = int(landmark.y * image.shape[0])
        cv2.circle(image, (x, y), 2, (0, 255, 0), -1)

    # Save the output image
    cv2.imwrite(str(output_path), image)
    print("Output saved to:", output_path)
