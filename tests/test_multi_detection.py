import unittest

from backend.detectors.pii_detector import detect_pii
from backend.detectors.secret_detector import detect_secrets


class TestMultipleDetections(unittest.TestCase):

    def test_multiple_sensitive_items(self):

        # Simulated Florence-2 OCR output
        ocr = {
            "labels": [
                "Name: Alex Example",
                "Email: alex@example.com",
                "Phone: 9123 4567",
                "Address: Blk 123, #04-56",
                "IP: 192.0.2.10",
                "Password: DemoPassword123!"
            ],
            "quad_boxes": [
                [10, 10, 300, 10, 300, 40, 10, 40],
                [10, 50, 300, 50, 300, 80, 10, 80],
                [10, 90, 300, 90, 300, 120, 10, 120],
                [10, 130, 300, 130, 300, 160, 10, 160],
                [10, 170, 300, 170, 300, 200, 10, 200],
                [10, 210, 300, 210, 300, 240, 10, 240]
            ]
        }

        pii = detect_pii(ocr)
        secrets = detect_secrets(ocr)

        findings = pii + secrets

        print("\n=== DETECTED PRIVACY RISKS ===")

        for finding in findings:
            print(
                f"- {finding.get('category')} "
                f"({finding.get('severity')})"
            )

        self.assertGreaterEqual(
            len(findings),
            4,
            "Expected at least 4 privacy findings."
        )


if __name__ == "__main__":
    unittest.main()
