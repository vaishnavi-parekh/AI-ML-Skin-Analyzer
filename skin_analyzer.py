"""Face-region skin analysis with visible problem blobs.

This is an explainable prototype: the trained detector supplies acne boxes,
and lightweight OpenCV signals mark possible dark spots and rough texture.
It is not a medical diagnosis.
"""
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from ultralytics import YOLO


BASE = Path(__file__).parent
LANDMARK_MODEL = BASE / "models" / "face_landmarker.task"
ACNE_MODEL = BASE / "models" / "model_V1.pt"
IMPROVED_ACNE_MODEL = BASE / "runs" / "detect" / "acne04_finetuned" / "weights" / "best.pt"
_acne_model = None


def _model():
    global _acne_model
    if _acne_model is None:
        model_path = IMPROVED_ACNE_MODEL if IMPROVED_ACNE_MODEL.exists() else ACNE_MODEL
        _acne_model = YOLO(str(model_path))
    return _acne_model


def _face_mask(image):
    """Return a face mask and landmarks, or (None, None) if no face exists."""
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(LANDMARK_MODEL)),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_faces=1,
    )
    with mp.tasks.vision.FaceLandmarker.create_from_options(options) as detector:
        result = detector.detect(mp_image)
    if not result.face_landmarks:
        return None, None

    height, width = image.shape[:2]
    points = np.array(
        [(int(p.x * width), int(p.y * height)) for p in result.face_landmarks[0]],
        dtype=np.int32,
    )
    hull = cv2.convexHull(points)
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.fillConvexPoly(mask, hull, 255)

    # The convex hull can stop near the eyebrows on high-forehead or cropped
    # photos. Add the visible forehead between the brow line and the upper
    # forehead landmarks so acne there is not discarded by the face filter.
    forehead_indices = [10, 54, 67, 103, 109, 338, 297, 332, 284]
    brow_indices = [70, 63, 105, 66, 107, 300, 293, 334, 296, 336]
    forehead_points = points[forehead_indices]
    brow_y = int(np.median(points[brow_indices, 1]))
    forehead_top = int(np.min(forehead_points[:, 1]))
    left_x = max(0, int(np.min(forehead_points[:, 0])) - 8)
    right_x = min(width - 1, int(np.max(forehead_points[:, 0])) + 8)
    if forehead_top < brow_y and right_x > left_x:
        forehead = np.array(
            [[left_x, brow_y], [right_x, brow_y],
             [right_x, forehead_top], [left_x, forehead_top]],
            dtype=np.int32,
        )
        cv2.fillConvexPoly(mask, forehead, 255)

    # Eyes and lips are naturally dark/high-detail and would otherwise be
    # mistaken for skin problems. Remove those landmark polygons.
    excluded_groups = [
        [33, 133, 160, 159, 158, 157, 173, 153, 144, 145, 163, 7],
        [362, 263, 387, 386, 385, 384, 398, 373, 380, 374, 381, 382],
        [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185],
    ]
    excluded = np.zeros_like(mask)
    for group_index, group in enumerate(excluded_groups):
        feature = np.array([points[index] for index in group], dtype=np.int32)
        cv2.fillPoly(excluded, [feature], 255)
        # Add a generous rectangular safety margin around eyes and lips. The
        # surrounding eyelid/lip shadows are not skin-issue evidence.
        if group_index < 2:
            x, y, w, h = cv2.boundingRect(feature)
            cv2.rectangle(excluded, (x - 35, y - 35), (x + w + 35, y + h + 35), 255, -1)
    # Nostrils are naturally dark and should not be reported as dark spots.
    for index in (98, 327):
        cv2.circle(excluded, tuple(points[index]), 16, 255, -1)
    excluded = cv2.dilate(excluded, np.ones((17, 17), np.uint8))
    mask[excluded > 0] = 0
    return mask, points


def _components(binary, min_area, max_area):
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, 8)
    found = []
    for index in range(1, count):
        area = int(stats[index, cv2.CC_STAT_AREA])
        if min_area <= area <= max_area:
            x, y, w, h = stats[index, :4]
            found.append((int(x), int(y), int(w), int(h), area, tuple(centroids[index])))
    return found


def _draw_blob(canvas, center, radius, color, label=None):
    center = (int(center[0]), int(center[1]))
    cv2.circle(canvas, center, max(5, int(radius)), color, -1)
    cv2.circle(canvas, center, max(5, int(radius)), (255, 255, 255), 1)
    if label:
        cv2.putText(canvas, label, (center[0] + 7, center[1] - 7),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 2, cv2.LINE_AA)


def _draw_component_regions(canvas, binary, min_area, max_area, color, limit=30, expand=0):
    """Paint connected detector regions instead of replacing them with dots."""
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    selected = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if not min_area <= area <= max_area:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        if w / max(1, h) >= 4 or h / max(1, w) >= 4:
            continue
        selected.append((area, contour))
    for _, contour in sorted(selected, key=lambda item: item[0], reverse=True)[:limit]:
        if expand:
            region = np.zeros(binary.shape, dtype=np.uint8)
            cv2.drawContours(region, [contour], -1, 255, cv2.FILLED)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (expand, expand))
            region = cv2.dilate(region, kernel)
            expanded_contours, _ = cv2.findContours(region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(canvas, expanded_contours, -1, color, cv2.FILLED)
        else:
            cv2.drawContours(canvas, [contour], -1, color, cv2.FILLED)


def _pigmentation_mask(image, face_mask):
    """Find locally darker, skin-colored pixels, adapting to illumination."""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    lightness = lab[:, :, 0].astype(np.float32)
    y, cr, cb = cv2.split(ycrcb)

    # Broad skin-color gate. It removes most hair/background pixels without
    # assuming one particular skin tone.
    skin_color = (
        (y > 20) & (cr > 105) & (cr < 215) &
        (cb > 55) & (cb < 175)
    )

    # Compare each pixel with its nearby facial skin, not with the whole image.
    # This compensates for shadows and uneven lighting better than a fixed V
    # threshold in HSV.
    local_lightness = cv2.GaussianBlur(lightness, (0, 0), 17)
    local_darkness = local_lightness - lightness
    valid = face_mask > 0
    baseline = float(np.median(lightness[valid]))
    candidate = (
        valid & skin_color &
        (local_darkness > 11.0) &
        (lightness < baseline - 7.0)
    ).astype(np.uint8) * 255
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return candidate


def _redness_mask(image, face_mask):
    """Find small, locally red skin regions for visual assistance only.

    This is deliberately separate from the trained detector. It can highlight
    acne-like redness the detector misses, but it is not counted as a model
    detection or presented as a diagnosis.
    """
    b, g, r = cv2.split(image.astype(np.float32))
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1].astype(np.float32)
    redness = r - (g + b) / 2.0
    local_redness = cv2.GaussianBlur(redness, (0, 0), 9)
    candidate = (
        (face_mask > 0) &
        (redness > 12.0) &
        ((redness - local_redness) > 6.0) &
        (saturation > 38.0)
    ).astype(np.uint8) * 255
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    return candidate


def _under_eye_mouth_darkness(image, points):
    """Find darker skin around (not on) the eyes and mouth.

    This is a visual pigmentation hint. Natural shadows and makeup can also
    trigger it, so it is not treated as a medical classification.
    """
    height, width = image.shape[:2]
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    lightness = lab[:, :, 0].astype(np.float32)
    y, cr, cb = cv2.split(ycrcb)
    skin_color = (
        (y > 35) & (cr > 118) & (cr < 205) &
        (cb > 65) & (cb < 155)
    )

    target = np.zeros((height, width), dtype=np.uint8)
    broad_under_eye_dark = np.zeros((height, width), dtype=np.uint8)
    eye_groups = [
        [33, 133, 160, 159, 158, 157, 173, 153, 144, 145, 163, 7],
        [362, 263, 387, 386, 385, 384, 398, 373, 380, 374, 381, 382],
    ]
    for group in eye_groups:
        x, y0, w, h = cv2.boundingRect(np.array([points[i] for i in group]))
        # Only the skin immediately below each eye; the eye itself is excluded.
        under_y1 = min(height - 1, y0 + h + 2)
        under_y2 = min(height - 1, y0 + h + max(12, int(h * 1.0)))
        cv2.rectangle(
            target,
            (max(0, x - 12), min(height - 1, y0 + h + 2)),
            (min(width - 1, x + w + 12), min(height - 1, y0 + h + max(12, int(h * 0.85)))),
            255,
            -1,
        )

        # Broad dark circles do not always have strong local contrast. Compare
        # the under-eye band with a nearby lower-cheek reference band.
        under = lightness[under_y1:under_y2 + 1, max(0, x - 8):min(width, x + w + 8)]
        ref_y1 = min(height - 1, under_y2 + max(4, int(h * 0.35)))
        ref_y2 = min(height - 1, ref_y1 + max(8, int(h * 0.8)))
        reference = lightness[ref_y1:ref_y2 + 1, max(0, x - 8):min(width, x + w + 8)]
        under_values = under[under > 20]
        reference_values = reference[reference > 20]
        if under_values.size and reference_values.size:
            if float(np.median(under_values)) < float(np.median(reference_values)) - 4.0:
                cv2.rectangle(
                    broad_under_eye_dark,
                    (max(0, x - 10), under_y1),
                    (min(width - 1, x + w + 10), under_y2),
                    255,
                    -1,
                )

    mouth_group = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185]
    mouth = np.array([points[i] for i in mouth_group], dtype=np.int32)
    x, y0, w, h = cv2.boundingRect(mouth)
    cv2.rectangle(
        target,
        (max(0, x - 28), max(0, y0 - 20)),
        (min(width - 1, x + w + 28), min(height - 1, y0 + h + 25)),
        255,
        -1,
    )
    # Do not classify the lips themselves as surrounding darkness.
    cv2.fillPoly(target, [mouth], 0)

    local_lightness = cv2.GaussianBlur(lightness, (0, 0), 15)
    valid = (target > 0) & skin_color
    if not np.any(valid):
        return np.zeros((height, width), dtype=np.uint8)
    baseline = float(np.median(lightness[valid]))
    candidate = (
        valid &
        ((local_lightness - lightness) > 2.0) &
        (lightness < baseline - 8.0)
    ).astype(np.uint8) * 255
    candidate = cv2.bitwise_or(candidate, broad_under_eye_dark)
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    return candidate


def analyze_image(image_path):
    image_path = Path(image_path)
    image = cv2.imread(str(image_path))
    if image is None:
        return {"ok": False, "error": "The uploaded image could not be read."}
    if not LANDMARK_MODEL.exists():
        return {"ok": False, "error": f"Missing face model: {LANDMARK_MODEL.name}"}
    if not ACNE_MODEL.exists():
        return {"ok": False, "error": f"Missing acne model: {ACNE_MODEL.name}"}

    mask, landmarks = _face_mask(image)
    if mask is None:
        return {"ok": False, "error": "No face found. Use a clear, front-facing photo in even light."}

    output = image.copy()
    overlay = image.copy()
    height, width = image.shape[:2]
    face_area = max(1, int(cv2.countNonZero(mask)))

    # Acne: use the trained detector and render connected translucent blobs.
    acne = []
    acne_visual = np.zeros((height, width), dtype=np.uint8)
    model_path = IMPROVED_ACNE_MODEL if IMPROVED_ACNE_MODEL.exists() else ACNE_MODEL
    prediction = _model()(image, verbose=False, conf=0.18, iou=0.45)[0]
    for box, confidence in zip(prediction.boxes.xyxy.cpu().numpy(), prediction.boxes.conf.cpu().numpy()):
        x1, y1, x2, y2 = [int(v) for v in box]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        if 0 <= cx < width and 0 <= cy < height and mask[cy, cx]:
            acne.append({"box": [x1, y1, x2, y2], "confidence": round(float(confidence), 3)})
            cv2.ellipse(
                acne_visual, (cx, cy),
                (max(7, (x2 - x1) // 2), max(7, (y2 - y1) // 2)),
                0, 0, 360, 255, -1,
            )

    # Add conservative, component-filtered hints for small red regions the
    # detector may miss. Keep these out of the acne count because they are
    # only estimates.
    estimated_redness = _redness_mask(image, mask)
    acne_visual = cv2.dilate(
        acne_visual,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)),
    )
    overlay[acne_visual > 0] = (0, 0, 255)
    _draw_component_regions(
        overlay, estimated_redness, 30, max(900, face_area // 120),
        (0, 0, 255), 18, expand=7,
    )

    # Pigmentation: adaptive local contrast + broad skin-color filtering.
    # This is more robust to lighting than a fixed dark-pixel threshold.
    dark = _pigmentation_mask(image, mask)
    targeted_dark = _under_eye_mouth_darkness(image, landmarks)
    dark_candidates = _components(dark, max(35, face_area // 5000), max(120, face_area // 500))
    dark_candidates = [item for item in dark_candidates
                       if item[2] / max(1, item[3]) < 4 and item[3] / max(1, item[2]) < 4]
    # Compact marks are shown as dark spots; larger connected patches are
    # shown as possible pigmentation. This is a visual grouping, not a
    # clinical classification.
    dark_spots = sorted([x for x in dark_candidates if x[4] <= 700], key=lambda x: x[4], reverse=True)[:18]
    pigmentation = sorted([x for x in dark_candidates if x[4] > 700], key=lambda x: x[4], reverse=True)[:10]
    _draw_component_regions(overlay, dark, max(35, face_area // 5000), 700, (255, 0, 0), 18, expand=9)
    _draw_component_regions(overlay, dark, 701, max(120, face_area // 500), (0, 180, 0), 10, expand=15)
    # Targeted green hint for visibly darker under-eye/perioral regions.
    _draw_component_regions(overlay, targeted_dark, 25, max(700, face_area // 250),
                            (0, 180, 0), 8, expand=11)

    # Blend translucent blobs over the original image and add a persistent legend.
    cv2.addWeighted(overlay, 0.52, output, 0.48, 0, output)
    legend = [("ACNE / REDNESS", (0, 0, 255)), ("DARK SPOT", (255, 0, 0)),
              ("PIGMENTATION", (0, 180, 0))]
    cv2.rectangle(output, (12, 12), (245, 110), (20, 20, 20), -1)
    for index, (name, color) in enumerate(legend):
        y = 37 + index * 27
        cv2.circle(output, (28, y - 5), 7, color, -1)
        cv2.putText(output, name, (45, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    result_path = image_path.with_name(f"{image_path.stem}_result.jpg")
    cv2.imwrite(str(result_path), output)

    dark_count = len(dark_spots)
    pigmentation_count = len(pigmentation)
    return {
        "ok": True,
        "result_image": str(result_path),
        "skin_type": {"type": "prototype analysis", "maybe_sensitive": False,
                       "reasons": ["This prototype focuses on visible skin markers."]},
        "acne": {"count": len(acne), "detections": acne,
                 "method": f"{model_path.name} + visual redness hint"},
        "dark_spots": {"count": dark_count, "area_percent_of_skin": round(sum(x[4] for x in dark_spots) * 100 / face_area, 2),
                       "method": "adaptive skin-color and local-lightness analysis"},
        "pigmentation": {"count": pigmentation_count, "area_percent_of_skin": round(sum(x[4] for x in pigmentation) * 100 / face_area, 2)},
        "note": "Colored blobs are visual signals, not a medical diagnosis. Red = acne/redness, blue = dark spot, green = pigmentation.",
    }
