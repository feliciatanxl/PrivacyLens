"""
Detect QR codes using OpenCV (QRCodeDetectorAruco and standard QRCodeDetector).
Supports detecting multiple QR codes within a single image and handling varied contrast.
Does not log or reveal raw payload content.
"""
from typing import Any, Dict, List
import cv2
import numpy as np
from PIL import Image

from .box_utils import calculate_iou, normalize_box


def _extract_boxes_from_points(points, width: int, height: int) -> List[List[int]]:
    boxes = []
    if points is None:
        return boxes
    try:
        arr = np.asarray(points).reshape(-1, 4, 2)
        for quad in arr:
            x0, y0 = quad.min(axis=0)
            x1, y1 = quad.max(axis=0)
            nbox = normalize_box([x0, y0, x1, y1], width=width, height=height)
            if nbox and (nbox[2] - nbox[0] >= 10) and (nbox[3] - nbox[1] >= 10):
                boxes.append(nbox)
    except Exception:
        pass
    return boxes


def detect_qr(image: Image.Image) -> List[Dict[str, Any]]:
    """Detect all visible QR codes in the image."""
    rgb = np.array(image.convert('RGB'))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    width, height = image.size

    detected_boxes: List[List[int]] = []

    # 1. Try OpenCV QRCodeDetectorAruco (fast & modern)
    try:
        aruco_detector = cv2.QRCodeDetectorAruco()
        ok, pts = aruco_detector.detectMulti(bgr)
        if ok and pts is not None:
            detected_boxes.extend(_extract_boxes_from_points(pts, width, height))
    except Exception:
        pass

    # 2. Try standard QRCodeDetector detectMulti
    if not detected_boxes:
        try:
            std_detector = cv2.QRCodeDetector()
            ok, pts = std_detector.detectMulti(bgr)
            if ok and pts is not None:
                detected_boxes.extend(_extract_boxes_from_points(pts, width, height))
            else:
                ok_single, pt_single = std_detector.detect(bgr)
                if ok_single and pt_single is not None:
                    detected_boxes.extend(_extract_boxes_from_points(pt_single, width, height))
        except Exception:
            pass

    # 3. Fallback: Contrast enhancement / adaptive threshold for faint or screen QR codes
    if not detected_boxes:
        try:
            # Otsu thresholding
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            thresh_bgr = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
            std_detector = cv2.QRCodeDetector()
            ok, pts = std_detector.detectMulti(thresh_bgr)
            if ok and pts is not None:
                detected_boxes.extend(_extract_boxes_from_points(pts, width, height))
        except Exception:
            pass

    # Deduplicate overlapping QR boxes
    unique_boxes: List[List[int]] = []
    for box in detected_boxes:
        if not any(calculate_iou(box, existing) > 0.4 for existing in unique_boxes):
            unique_boxes.append(box)

    findings: List[Dict[str, Any]] = []
    for box in unique_boxes:
        findings.append({
            'category': 'QR code',
            'severity': 'review',
            'source': 'cv_qr',
            'confidence': None,
            'box': box,
            'explanation': 'A QR code was detected. QR codes can encode private profile URLs, Wi-Fi passwords, contact cards, or payment links.',
            'recommendation': 'Verify the destination link of the QR code or cover it before sharing.',
        })

    return findings
