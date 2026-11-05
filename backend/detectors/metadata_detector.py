"""
Detect sensitive embedded EXIF metadata (GPS location coordinates, timestamps, device serials).
Does not log or expose raw coordinates or private identifiers in output.
"""
from typing import Any, Dict, List
from PIL import ExifTags, Image


def detect_metadata(image: Image.Image) -> List[Dict[str, Any]]:
    """Inspect image EXIF metadata for embedded privacy risks."""
    findings: List[Dict[str, Any]] = []

    try:
        exif = image.getexif()
    except Exception:
        return findings

    if not exif:
        return findings

    tags = {}
    for tag_id, value in exif.items():
        tag_name = ExifTags.TAGS.get(tag_id, tag_id)
        tags[tag_name] = value

    # Check for GPS metadata (IFD 34853)
    gps_info = None
    if hasattr(ExifTags, 'IFD') and hasattr(ExifTags.IFD, 'GPSInfo'):
        try:
            gps_info = exif.get_ifd(ExifTags.IFD.GPSInfo)
        except Exception:
            pass

    if not gps_info:
        # Fallback to direct tag
        raw_gps = exif.get(34853) or tags.get('GPSInfo')
        if isinstance(raw_gps, dict):
            gps_info = raw_gps

    if gps_info and len(gps_info) > 0:
        findings.append({
            'category': 'Embedded GPS metadata',
            'severity': 'high',
            'source': 'metadata',
            'confidence': None,
            'box': None,
            'explanation': 'Photo contains embedded GPS coordinates indicating the physical location where the image was taken.',
            'recommendation': 'Remove EXIF metadata before sharing to prevent covert location tracking.',
        })

    # Timestamp metadata
    time_keys = {'DateTimeOriginal', 'DateTimeDigitized', 'DateTime'}
    found_time = any(k in tags for k in time_keys)
    if not found_time and hasattr(ExifTags, 'IFD') and hasattr(ExifTags.IFD, 'Exif'):
        try:
            exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
            for k, v in exif_ifd.items():
                if ExifTags.TAGS.get(k, k) in time_keys:
                    found_time = True
                    break
        except Exception:
            pass

    if found_time:
        findings.append({
            'category': 'Embedded timestamp metadata',
            'severity': 'review',
            'source': 'metadata',
            'confidence': None,
            'box': None,
            'explanation': 'Photo contains embedded date and time stamps that may disclose routines or schedules.',
            'recommendation': 'Strip EXIF metadata if you do not want capture time disclosed.',
        })

    # Device & Hardware metadata (Camera model, serial number)
    device_details = []
    if 'Make' in tags or 'Model' in tags:
        device_details.append('camera make/model')
    if 'BodySerialNumber' in tags or 'LensSerialNumber' in tags:
        device_details.append('hardware serial numbers')

    if device_details:
        findings.append({
            'category': 'Device & Hardware metadata',
            'severity': 'review',
            'source': 'metadata',
            'confidence': None,
            'box': None,
            'explanation': f"Metadata contains device information ({', '.join(device_details)}) which can link photos to a specific device.",
            'recommendation': 'Strip EXIF metadata before uploading to social networks.',
        })

    return findings
