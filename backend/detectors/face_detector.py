"""
Detect human faces using OpenCV Haar Cascades (frontal and profile).
Can also ingest object detection hints as fallback without performing facial recognition.
"""
import os
from typing import Any, Dict, List, Optional
import cv2
import numpy as np
from PIL import Image

from .box_utils import calculate_containment, calculate_iou, normalize_box


def _get_cascade(xml_name: str) -> Optional[cv2.CascadeClassifier]:
    path = os.path.join(cv2.data.haarcascades, xml_name)
    if os.path.exists(path):
        cascade = cv2.CascadeClassifier(path)
        if not cascade.empty():
            return cascade
    return None


def detect_faces(
    image: Image.Image,
    objects: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Locate visible human faces in the image."""
    findings: List[Dict[str, Any]] = []
    width, height = image.size

    # Convert to grayscale for Haar cascade
    rgb = np.array(image.convert('RGB'))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    # Histogram equalization to enhance face contrast in varying lighting
    gray_eq = cv2.equalizeHist(gray)

    raw_boxes: List[List[int]] = []

    # 1. Frontal face cascade
    frontal = _get_cascade('haarcascade_frontalface_default.xml')
    if frontal is not None:
        detected = frontal.detectMultiScale(
            gray_eq,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(24, 24)
        )
        for (x, y, w, h) in detected:
            raw_boxes.append([int(x), int(y), int(x + w), int(y + h)])

    # 2. Profile face cascade (catches side-profile faces)
    profile = _get_cascade('haarcascade_profileface.xml')
    if profile is not None:
        detected_p = profile.detectMultiScale(
            gray_eq,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(24, 24)
        )
        for (x, y, w, h) in detected_p:
            raw_boxes.append([int(x), int(y), int(x + w), int(y + h)])

    # 3. If object detection provided 'face' labels, merge them
    if objects and 'labels' in objects and 'bboxes' in objects:
        for label, bbox in zip(objects['labels'], objects['bboxes']):
            lbl = str(label).lower()
            if 'face' in lbl or 'head' in lbl:
                nbox = normalize_box(bbox, width=width, height=height)
                if nbox:
                    raw_boxes.append(nbox)

    # Deduplicate overlapping face boxes
    deduped: List[List[int]] = []
    for box in raw_boxes:
        norm = normalize_box(box, width=width, height=height)
        if not norm:
            continue
        is_dup = False
        for existing in deduped:
            if calculate_iou(norm, existing) > 0.4 or calculate_containment(norm, existing) > 0.7:
                is_dup = True
                break
        if not is_dup:
            deduped.append(norm)

    for box in deduped:
        findings.append({
            'category': 'Human face',
            'severity': 'review',
            'source': 'cv_face',
            'confidence': None,
            'box': box,
            'explanation': 'A visible human face was detected. Faces allow biometric identification and recognition.',
            'recommendation': 'Verify consent or consider covering the face before posting online.',
        })

    return findings
