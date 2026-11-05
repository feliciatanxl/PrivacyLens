"""
Visual and context clue detectors for School Uniforms, School Badges/Logos,
Street Signs/Location Clues, and Routine/Schedule clues.
Combines Florence-2 vision labels/grounding with OCR text cues.
"""
import re
from typing import Any, Dict, List, Optional

from .box_utils import get_enclosing_box, normalize_box, parse_ocr_regions

# Educational institution keywords for School Badges / Logos (Category 2)
SCHOOL_KEYWORDS_RE = re.compile(
    r'\b(?:primary\s*school|secondary\s*school|junior\s*college|polytechnic|high\s*school|'
    r'international\s*school|grammar\s*school|kindergarten|preschool|academy|'
    r'institution|madrasah|university|college)\b',
    re.I
)

# School uniform / PE attire indicators (Category 1)
UNIFORM_TEXT_RE = re.compile(
    r'\b(?:PE\s*shirt|school\s*uniform|student\s*council|prefect|house\s*captain)\b|\bPE\b',
    re.I
)

# Street signs & Location clues (Category 14)
STREET_SIGN_RE = re.compile(
    r'\b[A-Za-z0-9\s\'-]+(?:\s+(?:street|st\.|road|rd\.|avenue|ave\.|drive|dr\.|lane|lorong|lor\.|crescent|cres\.|way|close|boulevard|blvd\.|walk|place|pl\.|parkway|highway|expressway))\b|'
    r'\b(?:PIE|AYE|CTE|BKE|KPE|SLE|TPE|MCE|ECP)\s*(?:exit\s*\d+)?\b|'
    r'\b(?:MRT|LRT|bus\s*stop|bus\s*interchange|transit|train\s*station|subway|metro\s*station)\b',
    re.I
)

# Schedule & Routine clues
SCHEDULE_RE = re.compile(
    r'\b(?:timetable|schedule|class\s*routine|daily\s*routine|exam\s*timetable|recess|assembly|period\s*\d)\b',
    re.I
)

# Object detection label mappings
OD_HINTS = [
    (
        ('school uniform', 'uniform'),
        'School uniform',
        'review',
        'Visual clothing cues match school uniform or student attire, which may reveal educational affiliation.',
        'Cover school badges, ties, or distinctive collar/color patterns before posting.'
    ),
    (
        ('school badge', 'badge', 'emblem', 'crest', 'logo'),
        'School badge / logo',
        'high',
        'An emblem, badge, or logo was detected which may identify a specific school or organization.',
        'Blur or cover the badge to protect institutional privacy.'
    ),
    (
        ('street sign', 'traffic sign', 'signboard'),
        'Street sign / Location clue',
        'review',
        'A visible sign or street marker was detected, which could expose physical whereabouts.',
        'Conceal street signs or recognizable landmarks before posting.'
    ),
    (
        ('student id', 'id card', 'identification card', 'identity document'),
        'Identity document',
        'high',
        'An identity or student card was detected, likely bearing personal details.',
        'Do not share identification cards online.'
    ),
    (
        ('license plate', 'licence plate'),
        'Vehicle identifier',
        'high',
        'A vehicle license plate is visible.',
        'Black out vehicle license plates to protect owner privacy.'
    ),
    (
        ('timetable', 'calendar', 'schedule'),
        'Schedule / Routine clue',
        'review',
        'A visible calendar or schedule can expose personal routines and whereabouts.',
        'Cover specific times, dates, and locations on visible schedules.'
    ),
]


def detect_visual_context(
    objects: Optional[Dict[str, Any]] = None,
    ocr: Optional[Dict[str, Any]] = None,
    img_width: Optional[int] = None,
    img_height: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Detect school uniforms, badges, street signs, and schedule clues."""
    findings: List[Dict[str, Any]] = []

    # 1. Inspect Object Detection labels from Florence-2
    if objects and 'labels' in objects and 'bboxes' in objects:
        for label, box in zip(objects.get('labels', []), objects.get('bboxes', [])):
            lbl_clean = str(label).lower().strip()
            norm_box = normalize_box(box, width=img_width, height=img_height)
            if not norm_box:
                continue

            for keywords, cat_name, severity, explanation, recommendation in OD_HINTS:
                if any(k in lbl_clean for k in keywords):
                    findings.append({
                        'category': cat_name,
                        'severity': severity,
                        'source': 'cv_object',
                        'confidence': None,
                        'box': norm_box,
                        'explanation': explanation,
                        'recommendation': recommendation,
                    })
                    break

    # 2. Inspect OCR for school badges/names, uniforms, street signs, and schedules
    if ocr:
        text, regions = parse_ocr_regions(ocr, width=img_width, height=img_height)
        if text and regions:
            # School Badges & Institutional Names (Category 2)
            for match in SCHOOL_KEYWORDS_RE.finditer(text):
                box = get_enclosing_box(regions, match.start(), match.end())
                if box:
                    findings.append({
                        'category': 'School badge / logo',
                        'severity': 'high',
                        'source': 'ocr_context',
                        'confidence': None,
                        'box': box,
                        'explanation': 'School or educational institution name identified in text. This can reveal where a student studies.',
                        'recommendation': 'Cover the school name and insignia before publishing.',
                    })

            # School Uniform text (Category 1)
            for match in UNIFORM_TEXT_RE.finditer(text):
                box = get_enclosing_box(regions, match.start(), match.end())
                if box:
                    findings.append({
                        'category': 'School uniform',
                        'severity': 'review',
                        'source': 'ocr_context',
                        'confidence': None,
                        'box': box,
                        'explanation': 'Student attire or PE shirt indicator detected in text.',
                        'recommendation': 'Consider covering school-identifying text on clothing.',
                    })

            # Street signs & Location markers (Category 14)
            for match in STREET_SIGN_RE.finditer(text):
                box = get_enclosing_box(regions, match.start(), match.end())
                if box:
                    findings.append({
                        'category': 'Street sign / Location clue',
                        'severity': 'review',
                        'source': 'ocr_context',
                        'confidence': None,
                        'box': box,
                        'explanation': 'A street name, expressway, or transit stop was identified in the text.',
                        'recommendation': 'Cover street and transit signage to protect your real-time or routine location.',
                    })

            # Schedules & Routine clues
            for match in SCHEDULE_RE.finditer(text):
                box = get_enclosing_box(regions, match.start(), match.end())
                if box:
                    findings.append({
                        'category': 'Schedule / Routine clue',
                        'severity': 'review',
                        'source': 'ocr_context',
                        'confidence': None,
                        'box': box,
                        'explanation': 'A timetable or schedule clue is visible in the text.',
                        'recommendation': 'Cover scheduled hours and locations to protect daily routines.',
                    })

    return findings
