"""Unit tests for metadata detector."""
import io
from PIL import ExifTags, Image
from backend.detectors.metadata_detector import detect_metadata


class TestMetadataDetector:

    def test_gps_metadata_detection(self):
        img = Image.new('RGB', (100, 100), 'white')
        exif = img.getexif()
        gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
        gps_ifd[1] = 'N'
        gps_ifd[2] = (1.0, 21.0, 12.34)
        exif[34853] = gps_ifd

        buf = io.BytesIO()
        img.save(buf, format='JPEG', exif=exif)
        buf.seek(0)

        saved_img = Image.open(buf)
        findings = detect_metadata(saved_img)

        assert len(findings) >= 1
        gps_finding = next(f for f in findings if f['category'] == 'Embedded GPS metadata')
        assert gps_finding['severity'] == 'high'
        assert gps_finding['box'] is None
        assert 'GPS' in gps_finding['explanation']

    def test_clean_image_no_metadata(self):
        img = Image.new('RGB', (100, 100), 'white')
        findings = detect_metadata(img)
        assert len(findings) == 0
