"""
PrivacyLens Benchmark: PaddleOCR vs Florence-2 Inference Latency & Accuracy.
"""
import json
import os
import sys
import time
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import torch
from backend.detectors.paddle_ocr_detector import detect_text_paddle, is_paddle_ocr_available
from backend.detectors.face_detector import detect_faces
from backend.detectors.qr_detector import detect_qr
from backend.detectors.metadata_detector import detect_metadata
from backend.detectors.pii_detector import detect_pii
from backend.detectors.secret_detector import detect_secrets
from backend.detectors.visual_detector import detect_visual_context
from backend.services.exposure_engine import explain_exposure
from backend.services.redaction_service import redact_image
from backend.privacy_engine import analyse_privacy

TEST_IMAGES_DIR = os.path.join(os.path.dirname(__file__), '..', 'tests', 'test_images')
BENCHMARK_IMAGES = [
    '01_delivery_label.png',
    '06_api_credentials.png',
    '07_passwords.png',
]


def run_benchmark():
    print("=" * 65)
    print("      PRIVACYLENS AI PERFORMANCE & PADDLEOCR BENCHMARK      ")
    print("=" * 65)
    print(f"PaddleOCR Available: {is_paddle_ocr_available()}")
    print(f"Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")

    results = []

    for name in BENCHMARK_IMAGES:
        path = os.path.join(TEST_IMAGES_DIR, name)
        if not os.path.exists(path):
            continue
        img = Image.open(path).convert('RGB')
        w, h = img.size

        # 1. PaddleOCR latency
        t0 = time.perf_counter()
        paddle_res = detect_text_paddle(img)
        t_paddle = (time.perf_counter() - t0) * 1000

        # 2. PII extraction from PaddleOCR
        t0 = time.perf_counter()
        pii = detect_pii(paddle_res, img_width=w, img_height=h)
        t_pii = (time.perf_counter() - t0) * 1000

        # 3. Secret extraction
        t0 = time.perf_counter()
        sec = detect_secrets(paddle_res, img_width=w, img_height=h)
        t_sec = (time.perf_counter() - t0) * 1000

        # 4. CV Face & QR
        t0 = time.perf_counter()
        faces = detect_faces(img)
        t_faces = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        qrs = detect_qr(img)
        t_qr = (time.perf_counter() - t0) * 1000

        # 5. Metadata
        t0 = time.perf_counter()
        meta = detect_metadata(img)
        t_meta = (time.perf_counter() - t0) * 1000

        # 6. Exposure Engine
        all_findings = pii + sec + faces + qrs + meta
        t0 = time.perf_counter()
        exposure = explain_exposure(all_findings)
        t_exp = (time.perf_counter() - t0) * 1000

        # 7. Redaction
        boxes = [f['box'] for f in all_findings if f.get('box')]
        t0 = time.perf_counter()
        _ = redact_image(img, boxes)
        t_redact = (time.perf_counter() - t0) * 1000

        total_fast = t_paddle + t_pii + t_sec + t_faces + t_qr + t_meta + t_exp

        print(f"\nImage: {name} ({w}x{h})")
        print(f" - PaddleOCR:           {t_paddle:6.1f} ms (Texts: {len(paddle_res['labels'])})")
        print(f" - PII Classification:  {t_pii:6.1f} ms (Findings: {len(pii)})")
        print(f" - Secrets Scan:        {t_sec:6.1f} ms (Findings: {len(sec)})")
        print(f" - Face Detection:      {t_faces:6.1f} ms")
        print(f" - QR Code Detection:   {t_qr:6.1f} ms")
        print(f" - Metadata Inspection: {t_meta:6.1f} ms")
        risk = exposure.get('exposure_risk', 'low')
        print(f" - Exposure Synthesis:  {t_exp:6.1f} ms (Risk: {risk})")
        print(f" - Redaction & Stripping: {t_redact:6.1f} ms")
        print(f" -> TOTAL FAST SCAN:    {total_fast:6.1f} ms")

        results.append({
            'image': name,
            'dimensions': f"{w}x{h}",
            'paddleocr_ms': round(t_paddle, 1),
            'total_fast_ms': round(total_fast, 1),
            'findings_count': len(all_findings),
            'risk_level': risk
        })

    out_file = os.path.join(os.path.dirname(__file__), 'benchmark_results.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nBenchmark results saved to {out_file}")


if __name__ == '__main__':
    run_benchmark()
