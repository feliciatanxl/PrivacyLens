"""
PrivacyLens Privacy Engine.
Orchestrates all specialised detectors, safely merges multi-detector findings,
validates coordinates, and ensures failure resilience across all 15 privacy categories.
"""
from typing import Any, Dict, List, Optional
from PIL import Image

from .detectors import (
    calculate_iou,
    detect_faces,
    detect_metadata,
    detect_pii,
    detect_qr,
    detect_secrets,
    detect_visual_context,
    normalize_box,
)


def _is_duplicate(finding_a: Dict[str, Any], finding_b: Dict[str, Any]) -> bool:
    """Determine whether two findings are redundant duplicates of the same occurrence."""
    cat_a = finding_a.get('category', '').lower()
    cat_b = finding_b.get('category', '').lower()
    box_a = finding_a.get('box')
    box_b = finding_b.get('box')

    # If neither has a box (e.g., metadata)
    if box_a is None and box_b is None:
        return cat_a == cat_b

    # If only one has a box, they are not duplicates
    if box_a is None or box_b is None:
        return False

    # Check spatial overlap
    iou = calculate_iou(box_a, box_b)
    # Check containment
    x_left = max(box_a[0], box_b[0])
    y_top = max(box_a[1], box_b[1])
    x_right = min(box_a[2], box_b[2])
    y_bottom = min(box_a[3], box_b[3])
    containment = 0.0
    if x_right > x_left and y_bottom > y_top:
        inter = (x_right - x_left) * (y_bottom - y_top)
        min_area = min(
            max(1, (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])),
            max(1, (box_b[2] - box_b[0]) * (box_b[3] - box_b[1]))
        )
        containment = inter / min_area

    # Duplicate if same category with significant overlap
    if cat_a == cat_b and (iou >= 0.5 or containment >= 0.8):
        return True

    # Duplicate if one is a generic version of the other (e.g. address vs address indicator)
    generic_pairs = [
        ('residential address', 'residential address indicator'),
        ('personal name', 'name field'),
        ('phone number', 'singapore phone number'),
        ('school badge / logo', 'school uniform'),
    ]
    for g1, g2 in generic_pairs:
        if (cat_a == g1 and cat_b == g2) or (cat_a == g2 and cat_b == g1):
            if iou >= 0.6 or containment >= 0.8:
                return True

    return False


def analyse_privacy(
    image: Image.Image,
    objects: Optional[Dict[str, Any]] = None,
    ocr: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Run all detectors independently and assemble combined privacy findings.
    Guarantees that a single detector error does not invalidate the entire scan.
    """
    width, height = image.size
    objects = objects or {}
    ocr = ocr or {}

    all_raw_findings: List[Dict[str, Any]] = []
    executed_scanners: List[str] = []
    scanner_errors: List[Dict[str, str]] = []

    # Pipeline definition: (name, function, arguments)
    pipeline = [
        ('ocr_pii', lambda: detect_pii(ocr, img_width=width, img_height=height)),
        ('ocr_secrets', lambda: detect_secrets(ocr, img_width=width, img_height=height)),
        ('visual_context', lambda: detect_visual_context(objects, ocr, img_width=width, img_height=height)),
        ('cv_faces', lambda: detect_faces(image, objects)),
        ('cv_qr', lambda: detect_qr(image)),
        ('metadata', lambda: detect_metadata(image)),
    ]

    for name, run_fn in pipeline:
        try:
            results = run_fn()
            executed_scanners.append(name)
            all_raw_findings.extend(results)
        except Exception as exc:
            scanner_errors.append({
                'scanner': name,
                'error_type': type(exc).__name__,
                'message': str(exc)
            })
            # Surface as an explicit warning so image is not falsely labelled safe
            all_raw_findings.append({
                'category': 'Scanner incomplete',
                'severity': 'review',
                'source': name,
                'confidence': None,
                'box': None,
                'explanation': f'Privacy scanner "{name}" could not finish ({type(exc).__name__}).',
                'recommendation': 'Manually inspect the image for unverified sensitive details.'
            })

    # Validate and normalize all boxes
    validated_findings: List[Dict[str, Any]] = []
    for item in all_raw_findings:
        raw_box = item.get('box')
        norm_box = normalize_box(raw_box, width=width, height=height) if raw_box else None
        validated_findings.append({
            'category': str(item.get('category', 'Sensitive information')),
            'severity': item.get('severity', 'review'),
            'source': item.get('source', 'unknown'),
            'confidence': item.get('confidence', None),
            'box': norm_box,
            'explanation': item.get('explanation', 'A potential privacy risk was detected.'),
            'recommendation': item.get('recommendation', 'Review and consider redacting before sharing.'),
        })

    # Deduplicate findings while preserving distinct categories and multi-findings
    unique_findings: List[Dict[str, Any]] = []
    for candidate in validated_findings:
        # Check against existing
        is_dup = False
        for i, existing in enumerate(unique_findings):
            if _is_duplicate(candidate, existing):
                is_dup = True
                # If candidate has higher severity, replace existing
                if candidate.get('severity') == 'high' and existing.get('severity') != 'high':
                    unique_findings[i] = candidate
                break
        if not is_dup:
            unique_findings.append(candidate)

    status = 'review_required' if unique_findings else 'no_flags_found'
    if scanner_errors:
        status = 'partial_scan'

    return {
        'status': status,
        'findings': unique_findings,
        'total_findings': len(unique_findings),
        'scanners_executed': executed_scanners,
        'scanner_errors': scanner_errors,
        'disclaimer': (
            'Automated detection can miss subtle clues or produce false positives. '
            'Always inspect both the original and redacted image before sharing.'
        )
    }
