"""Unit tests for secret and password detector."""
import pytest
from backend.detectors.secret_detector import detect_secrets
from tests.test_pii import fake_ocr


class TestSecretDetector:

    def test_api_keys(self):
        sample_keys = [
            "ghp_" + "a" * 36,
            "AKIAIOSFODNN7EXAMPLE",
            "sk-proj-" + "b" * 40,
            "AIzaSyD" + "x" * 32,
            "xoxb-1234567890-abcdefghij",
            "sk_live_" + "k" * 24,
        ]
        ocr = fake_ocr(*[f"key = {k}" for k in sample_keys])
        findings = detect_secrets(ocr)
        assert len(findings) >= len(sample_keys)

        # Security check: Ensure secret strings are NOT printed in explanations or recommendations!
        for f in findings:
            for k in sample_keys:
                assert k not in f['explanation'], f"Raw secret leaked in explanation: {k}"
                assert k not in f['recommendation'], f"Raw secret leaked in recommendation: {k}"

    def test_passwords_and_credentials(self):
        ocr = fake_ocr(
            "password = SuperSecretPass123!",
            "passwd: myAdminPassword#",
            "pwd = TemporaryPass2026",
            "pin = 9876",
            "User: admin Password: LoginPass321"
        )
        findings = detect_secrets(ocr)
        pw_finds = [f for f in findings if 'credential' in f['category'].lower() or 'password' in f['category'].lower()]
        assert len(pw_finds) >= 4

        # Verify no password values are leaked in the findings
        passwords = ["SuperSecretPass123!", "myAdminPassword#", "TemporaryPass2026", "9876", "LoginPass321"]
        for f in findings:
            for p in passwords:
                assert p not in f['explanation']
                assert p not in f['recommendation']

    def test_private_key_header(self):
        ocr = fake_ocr("-----BEGIN RSA PRIVATE KEY-----", "MIIEowIBAAKCAQEA04r...", "-----END RSA PRIVATE KEY-----")
        findings = detect_secrets(ocr)
        assert any('Private key' in f['category'] for f in findings)
