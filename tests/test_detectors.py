from backend.detectors.pii_detector import detect_pii
from backend.detectors.secret_detector import detect_secrets
from backend.services.exposure_engine import explain_exposure


def fake_ocr(*texts):
    return {'labels': list(texts), 'quad_boxes': [
        [10, i*30, 500, i*30, 500, i*30 + 20, 10, i*30 + 20]
        for i in range(len(texts))]}


def test_pii():
    findings = detect_pii(fake_ocr('Recipient: Alex Example',
                                   'Phone: 9123 4567',
                                   'Address: Blk 123, #04-56',
                                   'Email: alex@example.com',
                                   'Visa: 4111 1111 1111 1111',
                                   'Public IP: 8.8.8.8'))
    categories = {f['category'] for f in findings}
    expected = {'Name field', 'Singapore phone number', 'Possible address',
                'Email address', 'Possible payment card', 'Public IP address'}
    assert expected.issubset(categories), expected - categories
    assert all('9123' not in str(f) for f in findings)
    print('PII test passed:', sorted(categories))


def test_secrets():
    findings = detect_secrets(fake_ocr('password = demoPassword123!',
                                      'api_key: sk-' + 'a'*24))
    categories = {f['category'] for f in findings}
    assert 'Credential assignment' in categories
    assert 'OpenAI-style API key' in categories
    print('Secret test passed:', sorted(categories))


def test_exposure():
    example = [{'category': 'Name field'}, {'category': 'Possible address'},
               {'category': 'Possible schedule clue'}]
    assert len(explain_exposure(example)['possible_connections']) == 2
    print('Exposure test passed')


if __name__ == '__main__':
    test_pii()
    test_secrets()
    test_exposure()
