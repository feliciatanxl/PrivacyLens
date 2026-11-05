"""Comprehensive unit tests for PII detector covering all required categories."""
import pytest
from backend.detectors.pii_detector import detect_pii


def fake_ocr(*lines):
    labels = list(lines)
    # Generate non-overlapping 8-point quads for each line
    quad_boxes = [
        [10, i * 40, 400, i * 40, 400, i * 40 + 30, 10, i * 40 + 30]
        for i in range(len(lines))
    ]
    return {'labels': labels, 'quad_boxes': quad_boxes}


class TestPIIDetector:

    # 1. Emails
    def test_email_positive(self):
        ocr = fake_ocr("Contact us at test.user@example.com for help")
        findings = detect_pii(ocr)
        cats = [f['category'] for f in findings]
        assert 'Email address' in cats
        assert findings[0]['severity'] == 'high'
        assert findings[0]['box'] == [10, 0, 400, 30]

    def test_email_edge_cases(self):
        ocr = fake_ocr(
            "student_123+newsletter@sub.domain.edu.sg",
            "not-an-email",
            "@missinguser.com",
            "user@domain"
        )
        findings = detect_pii(ocr)
        assert len(findings) == 1
        assert findings[0]['category'] == 'Email address'

    # 2. Phone Numbers (Singapore & International)
    def test_sg_phone_numbers(self):
        ocr = fake_ocr(
            "Mobile: 9123 4567",
            "Home: +65 6123-4567",
            "Office: 81234567",
            "Not a phone: 1234 5678",
            "Random digits: 5123 4567"
        )
        findings = detect_pii(ocr)
        sg_phones = [f for f in findings if 'phone number' in f['category'].lower()]
        assert len(sg_phones) >= 3

    def test_international_phone_numbers(self):
        ocr = fake_ocr(
            "US: +1 (415) 555-2671",
            "UK: +44 20 7946 0919",
            "Direct: (800) 555-0199",
            "Not phone: 2026-11-06"
        )
        findings = detect_pii(ocr)
        intl_phones = [f for f in findings if 'phone number' in f['category'].lower()]
        assert len(intl_phones) >= 2

    # 3. National ID Numbers (NRIC / FIN / SSN)
    def test_sg_nric_fin(self):
        ocr = fake_ocr(
            "NRIC: S1234567A",
            "FIN: T7654321B",
            "Foreign: G1234567X",
            "Invalid: X1234567A",
            "Short: S123456A"
        )
        findings = detect_pii(ocr)
        nric_finds = [f for f in findings if 'Possible Singapore ID number' in f['category']]
        assert len(nric_finds) == 3

    def test_us_ssn(self):
        ocr = fake_ocr(
            "SSN: 123-45-6789",
            "Invalid SSN: 000-12-3456",
            "Fake SSN: 987-00-1234"
        )
        findings = detect_pii(ocr)
        ssn_finds = [f for f in findings if 'SSN' in f['category']]
        assert len(ssn_finds) == 1

    # 4. Payment Cards with Luhn Checksum
    def test_payment_cards_luhn(self):
        ocr = fake_ocr(
            "Visa: 4111 1111 1111 1111",      # Passes Luhn
            "Mastercard: 5500 0000 0000 0004", # Passes Luhn
            "Amex: 3782 822463 10005",        # Passes Luhn
            "Invalid: 4111 1111 1111 1112",    # Fails Luhn
            "Not a card: 1234 5678 9012"      # Too short (12 digits)
        )
        findings = detect_pii(ocr)
        cards = [f for f in findings if 'Possible payment card' in f['category']]
        assert len(cards) == 3

    # 5. IP Addresses (IPv4 and IPv6)
    def test_ipv4_addresses(self):
        ocr = fake_ocr(
            "Public: 8.8.8.8",
            "Router: 192.168.1.1",
            "Invalid octet: 256.100.0.1",
            "Not IP: 1.2.3"
        )
        findings = detect_pii(ocr)
        ips = [f for f in findings if 'IP address' in f['category']]
        assert len(ips) == 2
        assert any(f['category'] == 'Public IP address' for f in ips)
        assert any(f['category'] == 'IP address' for f in ips)

    def test_ipv6_addresses(self):
        ocr = fake_ocr(
            "Server IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "Loopback: ::1",
            "Invalid: 1200::ABXX::1"
        )
        findings = detect_pii(ocr)
        ipv6_finds = [f for f in findings if 'IPv6' in f['category']]
        assert len(ipv6_finds) >= 1

    # 6. Residential Addresses
    def test_addresses(self):
        ocr = fake_ocr(
            "Delivery to: Blk 456 Jurong West Ave 1, #10-123",
            "Address: 123 Orchard Road, Singapore 238801",
            "Random: Just talking about roads in general"
        )
        findings = detect_pii(ocr)
        addrs = [f for f in findings if 'address' in f['category'].lower()]
        assert len(addrs) >= 2

    # 7. Personal Names
    def test_personal_names(self):
        ocr = fake_ocr(
            "Recipient: Jennifer Tan",
            "Student Name: Johnathan Doe",
            "Cardholder: Sarah Lee",
            "Dr. Marcus Wong attended the clinic."
        )
        findings = detect_pii(ocr)
        names = [f for f in findings if 'name' in f['category'].lower()]
        assert len(names) >= 4
