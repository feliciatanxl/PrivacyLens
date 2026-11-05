"""Unit tests for Redaction Service and verification."""
import io
from PIL import ExifTags, Image
from backend.services.redaction_service import redact_image, verify_redaction


class TestRedactionService:

    def test_solid_opaque_redaction(self):
        # Create a white image with red boxes to redact
        img = Image.new('RGB', (200, 200), (255, 255, 255))
        # Add EXIF to test metadata stripping
        exif = img.getexif()
        exif[305] = "CameraModel123"
        exif[306] = "2026:11:06 01:00:00"

        boxes = [
            [20, 20, 60, 60],
            [100, 100, 150, 140]
        ]

        redacted = redact_image(img, boxes, margin=4)

        # Verify pixels in redacted regions are solid black
        assert redacted.getpixel((40, 40)) == (0, 0, 0)
        assert redacted.getpixel((120, 120)) == (0, 0, 0)
        # Margin area (e.g. 18, 18) should also be black
        assert redacted.getpixel((18, 18)) == (0, 0, 0)
        # Outside area remains white
        assert redacted.getpixel((5, 5)) == (255, 255, 255)

        # Verify EXIF is completely stripped
        verification = verify_redaction(img, redacted, boxes)
        assert verification['all_verified'] is True
        assert verification['boxes_verified'] == 2
        assert verification['metadata_stripped'] is True
