"""
Detect secrets, API keys, credentials, and passwords from OCR text.
Crucially, never expose or log the raw secret values in output or logs.
"""
import re
from typing import Any, Dict, List

from .box_utils import get_enclosing_box, parse_ocr_regions

# Secret Patterns
SECRET_PATTERNS = [
    (
        'GitHub token',
        re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{30,})\b'),
        'An exposed GitHub personal access token was detected.',
        'Cover it. Rotate any real credential that was exposed.'
    ),
    (
        'AWS access key ID',
        re.compile(r'\b(?:AKIA|ASIA|ABIA|ACCA)[A-Z0-9]{16}\b'),
        'An AWS Access Key ID was detected.',
        'Cover it. Rotate any real credential that was exposed.'
    ),
    (
        'OpenAI-style API key',
        re.compile(r'\bsk-(?:proj-|none-)?[A-Za-z0-9_-]{20,}\b'),
        'An OpenAI-style API key was detected.',
        'Cover it. Rotate any real credential that was exposed.'
    ),
    (
        'Google API key',
        re.compile(r'\bAIza[0-9A-Za-z\-_]{35}\b'),
        'A Google Cloud / Maps API key was detected.',
        'Cover it. Rotate any real credential that was exposed.'
    ),
    (
        'Slack token',
        re.compile(r'\bxox[baprs]-[0-9A-Za-z]{10,}\b'),
        'A Slack token was detected.',
        'Cover it. Rotate any real credential that was exposed.'
    ),
    (
        'Stripe secret key',
        re.compile(r'\b(?:sk|rk)_(?:live|test)_[0-9a-zA-Z]{24,}\b'),
        'A Stripe API key was detected.',
        'Cover it. Rotate any real credential that was exposed.'
    ),
    (
        'JSON Web Token (JWT)',
        re.compile(r'\beyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]+\b'),
        'A JSON Web Token (JWT) session or authentication token was detected.',
        'Cover it. Rotate any real credential that was exposed.'
    ),
    (
        'Private key header',
        re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
        'A private encryption/signing key block was detected.',
        'Cover it. Rotate any real credential that was exposed.'
    ),
    (
        'Credential assignment',
        re.compile(r'\b(?:password|passwd|pwd|passcode|api[_-]?key|secret|access[_-]?token|auth[_-]?token|client[_-]?secret)\s*[:=]\s*["\']?[^\s"\']{4,}', re.I),
        'Possible secret or credential visible.',
        'Cover it. Rotate any real credential that was exposed.'
    ),
]


def detect_secrets(ocr: Dict[str, Any], img_width: int = None, img_height: int = None) -> List[Dict[str, Any]]:
    """Detect secrets and credentials in OCR text and map back to bounding boxes."""
    text, regions = parse_ocr_regions(ocr, width=img_width, height=img_height)
    if not text or not regions:
        return []

    findings: List[Dict[str, Any]] = []

    for label, pattern, explanation, recommendation in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            box = get_enclosing_box(regions, match.start(), match.end())
            if box:
                findings.append({
                    'category': label,
                    'severity': 'high',
                    'source': 'ocr',
                    'confidence': None,
                    'box': box,
                    'explanation': explanation,
                    'recommendation': recommendation,
                })

    return findings
