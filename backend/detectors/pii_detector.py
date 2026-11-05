"""
Detect PII (Personal Identifiable Information) from OCR regions.
Covers: Emails, Phone numbers (SG & International), Personal names,
Residential addresses, NRIC/FIN/SSN identifiers, Payment cards, and IP addresses.
Outputs structured findings without logging or exposing raw private data.
"""
import ipaddress
import re
from typing import Any, Dict, List

from .box_utils import get_enclosing_box, parse_ocr_regions

# Patterns
EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')

# Singapore phone numbers (+65 followed by 6, 8, or 9 and 7 digits)
SG_PHONE_RE = re.compile(r'(?<!\d)(?:\+65[\s-]?)?[689]\d{3}[\s-]?\d{4}(?!\d)')

# International phone numbers (E.164 / North American / general international formats)
INTL_PHONE_RE = re.compile(
    r'(?<!\d)(?:\+\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}(?!\d)'
)
LABELLED_PHONE_RE = re.compile(
    r'\b(?:tel|phone|mobile|cell|hp|contact|hotline)\s*[:#]?\s*(\+?\d[\d\s\-\(\)]{6,16}\d)\b',
    re.I
)

# National Identification (Singapore NRIC/FIN, US SSN, UK NI)
SG_NRIC_FIN_RE = re.compile(r'\b[STFGM]\d{7}[A-Z]\b', re.I)
US_SSN_RE = re.compile(r'\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b')
LABELLED_ID_RE = re.compile(
    r'\b(?:NRIC|FIN|SSN|National\s*ID|ID\s*No|Identity\s*No|Passport\s*No)\s*[:#]?\s*([A-Za-z0-9\-]{5,15})\b',
    re.I
)

# Payment Cards (13 to 19 digits)
CARD_RE = re.compile(r'(?<!\d)(?:\d[ -]?){13,19}(?!\d)')

# IP Addresses (IPv4 and IPv6)
IPV4_RE = re.compile(r'(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])')
IPV6_RE = re.compile(
    r'(?<![\w:])(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}(?![\w:])|'
    r'(?<![\w:])(?:[0-9a-fA-F]{1,4}:)*::(?:[0-9a-fA-F]{1,4}:)*[0-9a-fA-F]{1,4}(?![\w:])|'
    r'(?<![\w:])::(?:[0-9a-fA-F]{1,4}:)*[0-9a-fA-F]{1,4}(?![\w:])',
    re.I
)

# Residential Addresses
ADDRESS_KEYWORDS_RE = re.compile(
    r'\b(?:blk|block|street|st\.|road|rd\.|avenue|ave\.|drive|dr\.|lane|lorong|lor\.|crescent|cres\.|way|close|boulevard|blvd\.|walk|place|pl\.|park|grove|hill|view|postal\s*code|zip\s*code)\b|#[0-9]{1,3}-[0-9]{2,4}\b',
    re.I
)
SG_POSTAL_RE = re.compile(r'\b(?:Singapore\s*)?\b\d{6}\b', re.I)
LABELLED_ADDRESS_RE = re.compile(
    r'\b(?:deliver(?:y)?\s*to|ship(?:ping)?\s*to|billing\s*address|delivery\s*address|residential\s*address|address)\s*:\s*([^\n\r]+)',
    re.I
)

# Personal Names
LABELLED_NAME_RE = re.compile(
    r'\b(?:recipient|full\s*name|student\s*name|cardholder(?:\s*name)?|patient\s*name|customer\s*name|employee\s*name|attn|attention|name)\s*:\s*([A-Za-z][A-Za-z .\'-]{2,50})',
    re.I
)
HONORIFIC_NAME_RE = re.compile(
    r'\b(?:Mr|Mrs|Ms|Miss|Dr|Prof|Mdm)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b'
)


def _luhn_check(digits: str) -> bool:
    """Validate payment card number using Luhn algorithm."""
    nums = [int(c) for c in digits if c.isdigit()]
    if len(nums) < 13 or len(nums) > 19:
        return False
    if len(set(nums)) == 1:
        return False
    return sum(
        (v * 2 - 9 if v * 2 > 9 else v * 2) if (len(nums) - i) % 2 == 0 else v
        for i, v in enumerate(nums)
    ) % 10 == 0


def _parse_ipv4(val: str):
    try:
        return ipaddress.IPv4Address(val)
    except (ValueError, ipaddress.AddressValueError):
        return None


def _is_valid_ipv6(val: str) -> bool:
    try:
        ipaddress.IPv6Address(val)
        return True
    except (ValueError, ipaddress.AddressValueError):
        return False


def _make_finding(category: str, severity: str, box: List[int], explanation: str, recommendation: str) -> Dict[str, Any]:
    return {
        'category': category,
        'severity': severity,
        'source': 'ocr',
        'confidence': None,
        'box': box,
        'explanation': explanation,
        'recommendation': recommendation,
    }


def detect_pii(ocr: Dict[str, Any], img_width: int = None, img_height: int = None) -> List[Dict[str, Any]]:
    """Detect PII entities in OCR text and map back to bounding boxes."""
    text, regions = parse_ocr_regions(ocr, width=img_width, height=img_height)
    if not text or not regions:
        return []

    findings: List[Dict[str, Any]] = []

    # 1. Emails (Category 5)
    for match in EMAIL_RE.finditer(text):
        box = get_enclosing_box(regions, match.start(), match.end())
        if box:
            findings.append(_make_finding(
                category='Email address',
                severity='high',
                box=box,
                explanation='An email address is visible and could expose contact details or lead to spam/phishing.',
                recommendation='Review and cover this detail before sharing.'
            ))

    # 2. Phone Numbers (Category 6) - SG & International
    phone_spans = set()
    for match in SG_PHONE_RE.finditer(text):
        phone_spans.add((match.start(), match.end()))
        box = get_enclosing_box(regions, match.start(), match.end())
        if box:
            findings.append(_make_finding(
                category='Singapore phone number',
                severity='high',
                box=box,
                explanation='A Singapore telephone number is visible and could lead to unwanted calls or harassment.',
                recommendation='Review and cover this detail before sharing.'
            ))

    for match in LABELLED_PHONE_RE.finditer(text):
        span = (match.start(), match.end())
        if not any(s <= match.start() and match.end() <= e for s, e in phone_spans):
            phone_spans.add(span)
            box = get_enclosing_box(regions, match.start(), match.end())
            if box:
                findings.append(_make_finding(
                    category='Singapore phone number' if '+65' in match.group() else 'International phone number',
                    severity='high',
                    box=box,
                    explanation='A contact phone number is visible.',
                    recommendation='Review and cover this detail before sharing.'
                ))

    for match in INTL_PHONE_RE.finditer(text):
        matched_str = match.group().strip()
        if '+' in matched_str or '(' in matched_str:
            if not any(s <= match.start() and match.end() <= e for s, e in phone_spans):
                phone_spans.add((match.start(), match.end()))
                box = get_enclosing_box(regions, match.start(), match.end())
                if box:
                    findings.append(_make_finding(
                        category='International phone number',
                        severity='high',
                        box=box,
                        explanation='An international phone number is visible.',
                        recommendation='Review and cover this detail before sharing.'
                    ))

    # 3. National ID Numbers (Category 9)
    for match in SG_NRIC_FIN_RE.finditer(text):
        box = get_enclosing_box(regions, match.start(), match.end())
        if box:
            findings.append(_make_finding(
                category='Possible Singapore ID number',
                severity='high',
                box=box,
                explanation='A Singapore NRIC or FIN format identifier is visible. Exposing national ID numbers poses identity theft risks.',
                recommendation='Review and cover this detail before sharing.'
            ))

    for match in US_SSN_RE.finditer(text):
        box = get_enclosing_box(regions, match.start(), match.end())
        if box:
            findings.append(_make_finding(
                category='National ID (SSN)',
                severity='high',
                box=box,
                explanation='A format matching a Social Security Number (SSN) is visible.',
                recommendation='Review and cover this detail before sharing.'
            ))

    for match in LABELLED_ID_RE.finditer(text):
        box = get_enclosing_box(regions, match.start(), match.end())
        if box:
            findings.append(_make_finding(
                category='Possible identity document',
                severity='high',
                box=box,
                explanation='A labelled government identity or passport number is visible.',
                recommendation='Review and cover this detail before sharing.'
            ))

    # 4. Payment Cards (Category 10)
    for match in CARD_RE.finditer(text):
        raw_val = match.group()
        digits = re.sub(r'\D', '', raw_val)
        if 13 <= len(digits) <= 19 and _luhn_check(digits):
            box = get_enclosing_box(regions, match.start(), match.end())
            if box:
                findings.append(_make_finding(
                    category='Possible payment card',
                    severity='high',
                    box=box,
                    explanation='A valid payment card number is visible. This can allow unauthorized financial charges.',
                    recommendation='Review and cover this detail before sharing.'
                ))

    # 5. IP Addresses (Category 13)
    for match in IPV4_RE.finditer(text):
        val = match.group()
        ip_obj = _parse_ipv4(val)
        if ip_obj is not None:
            box = get_enclosing_box(regions, match.start(), match.end())
            if box:
                cat_name = 'Public IP address' if ip_obj.is_global else 'IP address'
                findings.append(_make_finding(
                    category=cat_name,
                    severity='review',
                    box=box,
                    explanation=f'An IPv4 address ({cat_name.lower()}) is visible and could expose network infrastructure.',
                    recommendation='Review and cover this detail before sharing.'
                ))

    for match in IPV6_RE.finditer(text):
        val = match.group().strip()
        if _is_valid_ipv6(val):
            box = get_enclosing_box(regions, match.start(), match.end())
            if box:
                findings.append(_make_finding(
                    category='IP address (IPv6)',
                    severity='review',
                    box=box,
                    explanation='An IPv6 network address is visible and may pinpoint a network endpoint.',
                    recommendation='Review and cover this detail before sharing.'
                ))

    # 6. Residential Addresses (Category 8)
    address_spans = set()
    for match in LABELLED_ADDRESS_RE.finditer(text):
        address_spans.add((match.start(), match.end()))
        box = get_enclosing_box(regions, match.start(), match.end())
        if box:
            findings.append(_make_finding(
                category='Possible address',
                severity='high',
                box=box,
                explanation='A labelled shipping or residential address is visible, disclosing physical location.',
                recommendation='Review and cover this detail before sharing.'
            ))

    for match in ADDRESS_KEYWORDS_RE.finditer(text):
        if not any(s <= match.start() and match.end() <= e for s, e in address_spans):
            box = get_enclosing_box(regions, match.start(), match.end())
            if box:
                findings.append(_make_finding(
                    category='Possible address',
                    severity='review',
                    box=box,
                    explanation='Text containing residential indicators (block, street, or unit number) may expose a location.',
                    recommendation='Review and cover this detail before sharing.'
                ))

    # 7. Personal Names (Category 7)
    for match in LABELLED_NAME_RE.finditer(text):
        box = get_enclosing_box(regions, match.start(), match.end())
        if box:
            findings.append(_make_finding(
                category='Name field',
                severity='review',
                box=box,
                explanation='A labelled personal name field is visible, potentially identifying a person.',
                recommendation='Review and cover this detail before sharing.'
            ))

    for match in HONORIFIC_NAME_RE.finditer(text):
        box = get_enclosing_box(regions, match.start(), match.end())
        if box:
            findings.append(_make_finding(
                category='Name field',
                severity='review',
                box=box,
                explanation='A person\'s name with title is visible.',
                recommendation='Review and cover this detail before sharing.'
            ))

    return findings
