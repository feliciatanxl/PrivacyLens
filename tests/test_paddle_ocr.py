"""Unit tests for PaddleOCR detector module."""
import os
import pytest
from PIL import Image
from backend.detectors.paddle_ocr_detector import detect_text_paddle, is_paddle_ocr_available
from backend.detectors.pii_detector import detect_pii
from backend.privacy_engine import analyse_privacy

TEST_IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'test_images')


def test_paddle_ocr_availability():
    """Verify that PaddleOCR is available on the system."""
    assert is_paddle_ocr_available() is True


def test_paddle_ocr_text_extraction():
    """Verify that PaddleOCR extracts text and quad coordinates from a real label."""
    img_path = os.path.join(TEST_IMAGES_DIR, '01_delivery_label.png')
    assert os.path.exists(img_path)
    img = Image.open(img_path)

    result = detect_text_paddle(img)
    assert result['available'] is True
    assert result['engine'] == 'paddleocr'
    assert len(result['labels']) > 0
    assert len(result['quad_boxes']) == len(result['labels'])
    assert len(result['bboxes']) == len(result['labels'])

    all_text = " ".join(result['labels'])
    assert 'PARCEL' in all_text or 'DELIVERY' in all_text or 'Jordan' in all_text
    assert '9123' in all_text or '4567' in all_text or 'Clementi' in all_text


def test_paddle_ocr_pii_integration():
    """Verify that PaddleOCR results feed into PII detector to find phone and address."""
    img_path = os.path.join(TEST_IMAGES_DIR, '01_delivery_label.png')
    img = Image.open(img_path)

    ocr_res = detect_text_paddle(img)
    pii = detect_pii(ocr_res, img_width=img.width, img_height=img.height)

    categories = [p['category'].lower() for p in pii]
    assert any('phone' in c for c in categories)
    assert any('address' in c for c in categories)


def test_paddle_ocr_blank_image():
    """Verify graceful handling of blank/empty images."""
    blank = Image.new('RGB', (100, 100), color=(255, 255, 255))
    result = detect_text_paddle(blank)
    assert result['available'] is True
    assert result['labels'] == []
    assert result['quad_boxes'] == []


def test_analyse_privacy_with_paddle():
    """Verify that analyse_privacy operates seamlessly with PaddleOCR output."""
    img_path = os.path.join(TEST_IMAGES_DIR, '01_delivery_label.png')
    img = Image.open(img_path)

    ocr_res = detect_text_paddle(img)
    privacy = analyse_privacy(img, objects={}, ocr=ocr_res)

    assert privacy['status'] in ('complete', 'partial', 'review_required')
    assert len(privacy['findings']) >= 2
    cats = [f['category'].lower() for f in privacy['findings']]
    assert any('phone' in c for c in cats)
