"""
PaddleOCR Detector for PrivacyLens.
Provides ultra-fast, robust text and quad bounding box extraction on CPU
using lightweight PP-OCRv4.
"""
import os
import threading
from typing import Any, Dict, List, Optional, Union
import numpy as np
from PIL import Image

# Ensure environment flags prevent unnecessary remote checks
os.environ.setdefault('PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK', 'True')

_ocr_engine = None
_ocr_lock = threading.Lock()
_ocr_initialized = False
_ocr_available = False


def get_paddle_ocr_engine():
    """Lazily initialize and return the singleton PaddleOCR engine."""
    global _ocr_engine, _ocr_initialized, _ocr_available
    if _ocr_initialized:
        return _ocr_engine

    with _ocr_lock:
        if _ocr_initialized:
            return _ocr_engine

        try:
            # Ensure torch is imported first to prevent Windows DLL symbol collision
            import torch  # noqa: F401
            from paddleocr import PaddleOCR

            _ocr_engine = PaddleOCR(
                ocr_version='PP-OCRv4',
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                lang='en',
            )
            _ocr_available = True
            print("PrivacyLens PaddleOCR PP-OCRv4 engine initialized successfully.")
        except Exception as exc:
            print(f"Warning: Could not initialize PaddleOCR engine ({exc}).")
            _ocr_engine = None
            _ocr_available = False
        finally:
            _ocr_initialized = True

    return _ocr_engine


def is_paddle_ocr_available() -> bool:
    """Check if the PaddleOCR engine is available."""
    engine = get_paddle_ocr_engine()
    return engine is not None and _ocr_available


def detect_text_paddle(
    image_or_path: Union[Image.Image, str],
    confidence_threshold: float = 0.5
) -> Dict[str, Any]:
    """
    Run PaddleOCR on an image and return standardized labels and quad_boxes.

    Returns:
        Dict with keys:
            'labels': List[str],
            'quad_boxes': List[List[int]] (8 coords [x1, y1, x2, y2, x3, y3, x4, y4]),
            'bboxes': List[List[int]] (4 coords [x1, y1, x2, y2]),
            'confidences': List[float],
            'engine': 'paddleocr',
            'available': bool
    """
    engine = get_paddle_ocr_engine()
    if engine is None:
        return {
            'labels': [],
            'quad_boxes': [],
            'bboxes': [],
            'confidences': [],
            'engine': 'paddleocr',
            'available': False,
        }

    try:
        if isinstance(image_or_path, Image.Image):
            rgb_img = image_or_path.convert('RGB')
            img_input = np.array(rgb_img)
        else:
            img_input = image_or_path

        with _ocr_lock:
            raw_res = list(engine.predict(img_input))

        if not raw_res:
            return {
                'labels': [],
                'quad_boxes': [],
                'bboxes': [],
                'confidences': [],
                'engine': 'paddleocr',
                'available': True,
            }

        res_item = raw_res[0]
        raw_texts = res_item.get('rec_texts', [])
        raw_scores = res_item.get('rec_scores', [])
        raw_boxes = res_item.get('rec_boxes', [])
        raw_polys = res_item.get('rec_polys', [])

        labels: List[str] = []
        quad_boxes: List[List[int]] = []
        bboxes: List[List[int]] = []
        confidences: List[float] = []

        for idx, text in enumerate(raw_texts):
            text_str = str(text).strip()
            if not text_str:
                continue

            score = float(raw_scores[idx]) if idx < len(raw_scores) else 1.0
            if score < confidence_threshold:
                continue

            # Standard 4-point box [x1, y1, x2, y2]
            box = None
            if idx < len(raw_boxes):
                b = raw_boxes[idx]
                if hasattr(b, 'tolist'):
                    b = b.tolist()
                if len(b) == 4:
                    box = [int(round(c)) for c in b]

            # 4-point polygon [[x1, y1], [x2, y2], [x3, y3], [x4, y4]] -> 8 elements
            quad = None
            if idx < len(raw_polys):
                poly = raw_polys[idx]
                if hasattr(poly, 'tolist'):
                    poly = poly.tolist()
                if len(poly) == 4 and all(len(pt) == 2 for pt in poly):
                    quad = [
                        int(round(poly[0][0])), int(round(poly[0][1])),
                        int(round(poly[1][0])), int(round(poly[1][1])),
                        int(round(poly[2][0])), int(round(poly[2][1])),
                        int(round(poly[3][0])), int(round(poly[3][1]))
                    ]

            # Fallback if quad is missing or box is missing
            if quad is None and box is not None:
                quad = [box[0], box[1], box[2], box[1], box[2], box[3], box[0], box[3]]
            elif box is None and quad is not None:
                xs = quad[0::2]
                ys = quad[1::2]
                box = [min(xs), min(ys), max(xs), max(ys)]

            if box is not None:
                labels.append(text_str)
                quad_boxes.append(quad or [box[0], box[1], box[2], box[1], box[2], box[3], box[0], box[3]])
                bboxes.append(box)
                confidences.append(score)

        return {
            'labels': labels,
            'quad_boxes': quad_boxes,
            'bboxes': bboxes,
            'confidences': confidences,
            'engine': 'paddleocr',
            'available': True,
        }

    except Exception as exc:
        print(f"Warning: PaddleOCR inference error ({exc})")
        return {
            'labels': [],
            'quad_boxes': [],
            'bboxes': [],
            'confidences': [],
            'engine': 'paddleocr',
            'available': False,
            'error': str(exc),
        }
