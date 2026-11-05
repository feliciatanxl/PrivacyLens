"""
Comprehensive Integration & Benchmark Evaluation Test Suite.
Tests the full pipeline: Image -> OCR/Vision -> Detectors -> Merge -> Redaction -> API response.
Measures Precision, Recall, False Positives, False Negatives, and Processing Times.
"""
import io
import json
import os
import time
from typing import Dict, List, Set
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from backend.main import app
from backend.privacy_engine import analyse_privacy
from backend.services.exposure_engine import explain_exposure
from backend.services.redaction_service import redact_image, verify_redaction
from tests.test_pii import fake_ocr

TEST_IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'test_images')


class TestPipelineIntegration:

    @pytest.fixture
    def client(self):
        with TestClient(app) as c:
            yield c

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "device" in data
        assert data["version"] == "1.0.0"

    def test_multi_detection_composite_pipeline(self):
        """
        Verify that an image containing many disparate categories
        (Name, NRIC, Email, Phone, Address, Password, Token, School, Schedule, QR)
        returns all independent findings in a single scan.
        """
        composite_ocr = fake_ocr(
            "Raffles Institution Secondary School",
            "Recipient: Marcus Tan",
            "NRIC: S9912345Z",
            "Email: marcus.tan@student.edu.sg",
            "Phone: +65 9123 4567",
            "Address: Blk 100 Bishan St 12, #05-20",
            "password = Bishan2026Secret!",
            "API: ghp_" + "m" * 36,
            "Daily Class Timetable · Period 1 to 8"
        )
        fake_objects = {
            'labels': ['school uniform'],
            'bboxes': [[10, 10, 150, 200]]
        }
        test_img = Image.new('RGB', (600, 500), 'white')

        start_time = time.perf_counter()
        privacy_result = analyse_privacy(test_img, objects=fake_objects, ocr=composite_ocr)
        exposure_result = explain_exposure(privacy_result['findings'])
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        findings = privacy_result['findings']
        cats = [f['category'] for f in findings]

        # Verify diverse multi-category coverage in a single result
        assert len(findings) >= 8, f"Expected at least 8 findings, got {len(findings)}: {cats}"
        assert any('School' in c for c in cats)
        assert any('Name' in c for c in cats)
        assert any('ID' in c for c in cats)
        assert any('Email' in c for c in cats)
        assert any('phone' in c.lower() for c in cats)
        assert any('address' in c.lower() for c in cats)
        assert any('Credential' in c or 'password' in c.lower() for c in cats)
        assert any('token' in c.lower() for c in cats)

        # Verify Exposure Reconstruction
        assert exposure_result['risk_level'] == 'critical'
        assert len(exposure_result['possible_connections']) >= 3
        assert len(exposure_result['exposure_scenarios']) >= 2

        # Verify Redaction on all found boxes
        boxes_to_redact = [f['box'] for f in findings if f.get('box')]
        redacted = redact_image(test_img, boxes_to_redact)
        verification = verify_redaction(test_img, redacted, boxes_to_redact)
        assert verification['all_verified'] is True
        assert verification['boxes_verified'] == len(boxes_to_redact)

        print(f"\n[Multi-Detection Benchmark] Detected {len(findings)} distinct risks in {elapsed_ms:.2f} ms")

    def test_api_redact_endpoint(self, client):
        """Test POST /redact via FastAPI TestClient."""
        img = Image.new('RGB', (200, 200), (255, 255, 255))
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        boxes = [[20, 20, 80, 80], [100, 100, 150, 150]]
        files = {'file': ('test.png', buf, 'image/png')}
        data = {'boxes': json.dumps(boxes), 'margin': 4}

        resp = client.post("/redact", files=files, data=data)
        assert resp.status_code == 200
        assert resp.headers.get("content-type") == "image/png"
        assert resp.headers.get("x-redacted-boxes-count") == "2"
        assert resp.headers.get("x-metadata-stripped") == "True"

        # Verify returned image
        redacted_bytes = io.BytesIO(resp.content)
        redacted_img = Image.open(redacted_bytes)
        assert redacted_img.size == (200, 200)
        assert redacted_img.getpixel((50, 50)) == (0, 0, 0)
        assert redacted_img.getpixel((125, 125)) == (0, 0, 0)
        assert redacted_img.getpixel((5, 5)) == (255, 255, 255)

    def test_dataset_precision_recall_benchmark(self):
        """
        Benchmark accuracy evaluation across 15 sensitive information categories.
        Measures Precision, Recall, False Positives, False Negatives, and Latency.
        """
        # Ground-truth test cases: (name, ocr_lines, objects, expected_categories)
        eval_suite = [
            (
                "Delivery Label",
                ["Recipient: Jordan Tan", "Phone: +65 9123 4567", "Address: Blk 789 Clementi Ave 3, #12-34", "Singapore 120789"],
                {},
                {"Name field", "Singapore phone number", "Possible address"}
            ),
            (
                "Student ID",
                ["SINGAPORE HIGH SCHOOL", "Student Name: Alex Morgan", "Student ID: S9876543A"],
                {"labels": ["student id"], "bboxes": [[10, 10, 200, 150]]},
                {"School badge / logo", "Name field", "Possible Singapore ID number"}
            ),
            (
                "School Uniform PE",
                ["GUANGYANG PRIMARY SCHOOL", "PE ATTIR - FALCON HOUSE"],
                {"labels": ["school uniform"], "bboxes": [[50, 50, 300, 300]]},
                {"School badge / logo", "School uniform"}
            ),
            (
                "Street & Bus Sign",
                ["ORCHARD ROAD", "Bus Stop 09048", "Timetable: 0800 - 1800"],
                {"labels": ["street sign"], "bboxes": [[20, 20, 250, 100]]},
                {"Street sign / Location clue", "Schedule / Routine clue"}
            ),
            (
                "API Credentials",
                ['GITHUB_TOKEN = "ghp_' + 'a'*36 + '"', 'AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"', 'OPENAI_API_KEY = "sk-proj-' + 'x'*36 + '"'],
                {},
                {"GitHub token", "AWS access key ID", "OpenAI-style API key"}
            ),
            (
                "Passwords & IP",
                ["Email: developer@school.edu.sg", "password = SecretPassword2026!", "Server IP: 192.168.1.50"],
                {},
                {"Email address", "Credential assignment", "IP address"}
            ),
            (
                "Payment & ID Form",
                ["Full Name: Jamie Lee Chen", "NRIC: T0512345A", "Card Number: 4111 1111 1111 1111"],
                {},
                {"Name field", "Possible Singapore ID number", "Possible payment card"}
            ),
            (
                "Benign Document (Negative Control)",
                ["Chapter 1: The Solar System", "Planets revolve around the sun in elliptical orbits.", "Published by Science Press in 2024."],
                {},
                set()
            ),
        ]

        total_tp = 0
        total_fp = 0
        total_fn = 0
        per_category_stats: Dict[str, Dict[str, int]] = {}
        total_latency = 0.0

        for name, lines, objects, expected_cats in eval_suite:
            ocr = fake_ocr(*lines) if lines else {}
            dummy_img = Image.new('RGB', (500, 400), 'white')

            t0 = time.perf_counter()
            result = analyse_privacy(dummy_img, objects=objects, ocr=ocr)
            t1 = time.perf_counter()
            total_latency += (t1 - t0)

            detected_cats = {f['category'] for f in result['findings']}

            # Compare against expected
            tp = len(detected_cats & expected_cats)
            fp = len(detected_cats - expected_cats)
            fn = len(expected_cats - detected_cats)

            total_tp += tp
            total_fp += fp
            total_fn += fn

            for cat in expected_cats:
                if cat not in per_category_stats:
                    per_category_stats[cat] = {'tp': 0, 'fn': 0, 'fp': 0}
                if cat in detected_cats:
                    per_category_stats[cat]['tp'] += 1
                else:
                    per_category_stats[cat]['fn'] += 1

            for cat in (detected_cats - expected_cats):
                if cat not in per_category_stats:
                    per_category_stats[cat] = {'tp': 0, 'fn': 0, 'fp': 0}
                per_category_stats[cat]['fp'] += 1

        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 1.0
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 1.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        avg_latency_ms = (total_latency / len(eval_suite)) * 1000

        print("\n========================================================")
        print("         PRIVACYLENS DETECTION ACCURACY EVALUATION      ")
        print("========================================================")
        print(f"Test Cases Evaluated:   {len(eval_suite)}")
        print(f"True Positives (TP):    {total_tp}")
        print(f"False Positives (FP):   {total_fp}")
        print(f"False Negatives (FN):   {total_fn}")
        print(f"Precision:              {precision * 100:.2f}%")
        print(f"Recall:                 {recall * 100:.2f}%")
        print(f"F1-Score:               {f1 * 100:.2f}%")
        print(f"Average Scan Latency:   {avg_latency_ms:.2f} ms")
        print("--------------------------------------------------------")
        print("Per-Category True Positives Breakdown:")
        for cat, s in sorted(per_category_stats.items()):
            print(f"  - {cat:32s}: TP={s['tp']}, FP={s['fp']}, FN={s['fn']}")
        print("========================================================")

        assert precision >= 0.85, f"Precision below 85%: {precision:.2f}"
        assert recall >= 0.90, f"Recall below 90%: {recall:.2f}"
        assert f1 >= 0.85, f"F1-Score below 85%: {f1:.2f}"
