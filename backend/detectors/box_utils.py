"""Bounding box normalization, conversion, and deduplication utilities."""
from typing import List, Optional, Tuple, Dict, Any


def normalize_box(box: Any, width: Optional[int] = None, height: Optional[int] = None) -> Optional[List[int]]:
    """Convert 4-point or 8-point coordinates to integer [x1, y1, x2, y2]."""
    if not box or not isinstance(box, (list, tuple)):
        return None
    try:
        coords = [float(c) for c in box]
    except (ValueError, TypeError):
        return None

    if len(coords) == 4:
        x1, y1, x2, y2 = coords
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
    elif len(coords) == 8:
        xs = coords[0::2]
        ys = coords[1::2]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
    else:
        return None

    ix1 = max(0, int(round(min_x)))
    iy1 = max(0, int(round(min_y)))
    ix2 = max(ix1, int(round(max_x)))
    iy2 = max(iy1, int(round(max_y)))

    if width is not None:
        ix1 = min(width, ix1)
        ix2 = min(width, ix2)
    if height is not None:
        iy1 = min(height, iy1)
        iy2 = min(height, iy2)

    return [ix1, iy1, ix2, iy2]


def parse_ocr_regions(ocr: Dict[str, Any], width: Optional[int] = None, height: Optional[int] = None) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Map OCR character offsets back to one or more OCR region boxes.
    Supports both quad_boxes (8 coords) and bboxes (4 coords).
    """
    labels = ocr.get('labels') or []
    boxes = ocr.get('quad_boxes') or ocr.get('bboxes') or []

    parts: List[str] = []
    regions: List[Dict[str, Any]] = []
    pos = 0

    for text, raw_box in zip(labels, boxes):
        text_str = str(text).strip()
        if not text_str:
            continue
        norm_box = normalize_box(raw_box, width=width, height=height)
        if not norm_box:
            continue

        if parts:
            parts.append('\n')
            pos += 1

        start = pos
        parts.append(text_str)
        pos += len(text_str)

        regions.append({
            'text': text_str,
            'start': start,
            'end': pos,
            'box': norm_box
        })

    return ''.join(parts), regions


def get_enclosing_box(regions: List[Dict[str, Any]], match_start: int, match_end: int) -> Optional[List[int]]:
    """Compute the minimal bounding box enclosing all OCR regions that intersect the character span."""
    overlapping = [
        r['box'] for r in regions
        if match_start < r['end'] and match_end > r['start'] and r.get('box')
    ]
    if not overlapping:
        return None
    return [
        min(b[0] for b in overlapping),
        min(b[1] for b in overlapping),
        max(b[2] for b in overlapping),
        max(b[3] for b in overlapping),
    ]


def calculate_iou(box_a: List[int], box_b: List[int]) -> float:
    """Calculate Intersection-over-Union (IoU) between two bounding boxes."""
    x_left = max(box_a[0], box_b[0])
    y_top = max(box_a[1], box_b[1])
    x_right = min(box_a[2], box_b[2])
    y_bottom = min(box_a[3], box_b[3])

    if x_right <= x_left or y_bottom <= y_top:
        return 0.0

    intersection = (x_right - x_left) * (y_bottom - y_top)
    area_a = max(1, (box_a[2] - box_a[0]) * (box_a[3] - box_a[1]))
    area_b = max(1, (box_b[2] - box_b[0]) * (box_b[3] - box_b[1]))
    union = area_a + area_b - intersection
    return intersection / union if union > 0 else 0.0


def calculate_containment(box_a: List[int], box_b: List[int]) -> float:
    """Calculate ratio of intersection over the smaller box's area."""
    x_left = max(box_a[0], box_b[0])
    y_top = max(box_a[1], box_b[1])
    x_right = min(box_a[2], box_b[2])
    y_bottom = min(box_a[3], box_b[3])

    if x_right <= x_left or y_bottom <= y_top:
        return 0.0

    intersection = (x_right - x_left) * (y_bottom - y_top)
    min_area = min(
        max(1, (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])),
        max(1, (box_b[2] - box_b[0]) * (box_b[3] - box_b[1]))
    )
    return intersection / min_area
