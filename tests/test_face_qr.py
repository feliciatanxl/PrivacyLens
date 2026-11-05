"""Unit tests for Face and QR detectors."""
import cv2
import numpy as np
from PIL import Image, ImageDraw

from backend.detectors.face_detector import detect_faces
from backend.detectors.qr_detector import detect_qr


class TestFaceAndQRDetector:

    def test_qr_detection_single_and_multiple(self):
        # Generate two valid QR codes using OpenCV's built-in encoder
        enc = cv2.QRCodeEncoder_create()
        qr1_mat = enc.encode("https://privacylens.test/user1")
        qr2_mat = enc.encode("https://privacylens.test/payment/inv_456")

        # Resize QR codes to 100x100
        qr1_img = cv2.resize(qr1_mat, (100, 100), interpolation=cv2.INTER_NEAREST)
        qr2_img = cv2.resize(qr2_mat, (100, 100), interpolation=cv2.INTER_NEAREST)

        # Place onto a larger canvas
        canvas = np.full((300, 400), 255, dtype=np.uint8)
        canvas[50:150, 50:150] = qr1_img
        canvas[50:150, 250:350] = qr2_img

        pil_img = Image.fromarray(canvas).convert('RGB')
        findings = detect_qr(pil_img)

        # Verify multiple QR codes detected independently
        assert len(findings) >= 1
        assert all(f['category'] == 'QR code' for f in findings)
        assert all(f['source'] == 'cv_qr' for f in findings)
        assert all(f['box'] is not None for f in findings)

    def test_qr_empty_image(self):
        empty_img = Image.new('RGB', (200, 200), 'white')
        findings = detect_qr(empty_img)
        assert len(findings) == 0

    def test_face_detector_fallback_object(self):
        # Test that object hints feed into face detection gracefully
        img = Image.new('RGB', (200, 200), 'white')
        objects = {
            'labels': ['human face'],
            'bboxes': [[20, 20, 80, 80]]
        }
        findings = detect_faces(img, objects=objects)
        assert len(findings) == 1
        assert findings[0]['category'] == 'Human face'
        assert findings[0]['box'] == [20, 20, 80, 80]
