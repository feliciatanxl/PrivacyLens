"""Unit tests for Visual Context clues (School Uniforms, Badges, Street Signs, Schedules)."""
from backend.detectors.visual_detector import detect_visual_context
from tests.test_pii import fake_ocr


class TestVisualContextDetector:

    def test_school_badge_and_uniform_ocr(self):
        ocr = fake_ocr(
            "Guangyang Secondary School",
            "Class of 2026 PE Shirt"
        )
        findings = detect_visual_context(ocr=ocr, img_width=500, img_height=200)
        cats = [f['category'] for f in findings]
        assert 'School badge / logo' in cats
        assert 'School uniform' in cats

    def test_street_sign_and_schedule_ocr(self):
        ocr = fake_ocr(
            "Victoria Street Bus Stop 01012",
            "PIE Exit 15",
            "Daily Routine Timetable"
        )
        findings = detect_visual_context(ocr=ocr, img_width=500, img_height=200)
        cats = [f['category'] for f in findings]
        assert 'Street sign / Location clue' in cats
        assert 'Schedule / Routine clue' in cats

    def test_object_detection_hints(self):
        objects = {
            'labels': ['school uniform', 'street sign'],
            'bboxes': [[10, 10, 100, 200], [300, 50, 450, 150]]
        }
        findings = detect_visual_context(objects=objects, img_width=500, img_height=300)
        cats = [f['category'] for f in findings]
        assert 'School uniform' in cats
        assert 'Street sign / Location clue' in cats
