"""
Generate synthetic / staged test images for all 12 benchmark test cases.
Uses purely synthetic / fictional data. No real personal identities, numbers, or credentials.
"""
import os
import cv2
import numpy as np
from PIL import ExifTags, Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'test_images')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _draw_text_box(draw, text, x, y, font_size=18, text_color=(20, 20, 20), bg_color=None):
    if bg_color:
        draw.rectangle([x - 4, y - 4, x + len(text) * 11, y + 26], fill=bg_color)
    draw.text((x, y), text, fill=text_color)


def generate_all():
    print(f"Generating synthetic test images in {OUTPUT_DIR}...")

    # 1. Delivery Label
    img1 = Image.new('RGB', (500, 350), (245, 245, 240))
    d1 = ImageDraw.Draw(img1)
    d1.rectangle([10, 10, 490, 340], outline=(100, 100, 100), width=2)
    _draw_text_box(d1, "PARCEL DELIVERY EXPRESS", 30, 30, text_color=(10, 10, 80))
    _draw_text_box(d1, "Recipient: Jordan Tan", 30, 80)
    _draw_text_box(d1, "Phone: +65 9123 4567", 30, 120)
    _draw_text_box(d1, "Address: Blk 789 Clementi Ave 3, #12-34", 30, 160)
    _draw_text_box(d1, "Singapore 120789", 30, 200)
    _draw_text_box(d1, "Tracking: SG-EXP-889900", 30, 250, text_color=(120, 120, 120))
    img1.save(os.path.join(OUTPUT_DIR, "01_delivery_label.png"))

    # 2. Student ID Card
    img2 = Image.new('RGB', (500, 300), (230, 240, 250))
    d2 = ImageDraw.Draw(img2)
    d2.rectangle([10, 10, 490, 290], outline=(40, 80, 160), width=3)
    d2.rectangle([30, 60, 150, 220], fill=(200, 210, 225), outline=(100, 100, 100))
    _draw_text_box(d2, "[PHOTO]", 65, 130, text_color=(100, 100, 100))
    _draw_text_box(d2, "SINGAPORE HIGH SCHOOL", 170, 35, text_color=(20, 40, 120))
    _draw_text_box(d2, "STUDENT IDENTIFICATION CARD", 170, 65, text_color=(80, 80, 80))
    _draw_text_box(d2, "Student Name: Alex Morgan", 170, 110)
    _draw_text_box(d2, "Student ID: S9876543A", 170, 150)
    _draw_text_box(d2, "Grade: Secondary 3 / Class 3B", 170, 190)
    _draw_text_box(d2, "Valid Thru: Dec 2027", 170, 230, text_color=(100, 100, 100))
    img2.save(os.path.join(OUTPUT_DIR, "02_student_id.png"))

    # 3. School Related Clothing (PE Shirt)
    img3 = Image.new('RGB', (450, 400), (40, 120, 80)) # Green shirt
    d3 = ImageDraw.Draw(img3)
    _draw_text_box(d3, "GUANGYANG", 140, 140, text_color=(255, 255, 255))
    _draw_text_box(d3, "PRIMARY SCHOOL", 115, 180, text_color=(255, 255, 255))
    _draw_text_box(d3, "PE ATTIR - FALCON HOUSE", 100, 220, text_color=(255, 240, 100))
    img3.save(os.path.join(OUTPUT_DIR, "03_school_clothing.png"))

    # 4. School Badge & Generic Emblem
    img4 = Image.new('RGB', (400, 400), (250, 250, 250))
    d4 = ImageDraw.Draw(img4)
    # Draw crest emblem
    d4.polygon([(200, 60), (320, 120), (300, 280), (200, 340), (100, 280), (80, 120)], outline=(160, 20, 40), width=4, fill=(255, 245, 245))
    _draw_text_box(d4, "VICTORIA", 160, 150, text_color=(160, 20, 40))
    _draw_text_box(d4, "JUNIOR COLLEGE", 130, 190, text_color=(160, 20, 40))
    _draw_text_box(d4, "NIL SINE LABORE", 145, 240, text_color=(100, 100, 100))
    img4.save(os.path.join(OUTPUT_DIR, "04_school_badge.png"))

    # 5. Street Sign / Location Marker
    img5 = Image.new('RGB', (500, 300), (200, 210, 215))
    d5 = ImageDraw.Draw(img5)
    # Green street sign
    d5.rectangle([40, 50, 460, 140], fill=(20, 120, 60), outline=(255, 255, 255), width=3)
    _draw_text_box(d5, "ORCHARD ROAD", 140, 75, text_color=(255, 255, 255))
    # Bus stop sign
    d5.rectangle([80, 180, 420, 260], fill=(220, 100, 20), outline=(255, 255, 255), width=2)
    _draw_text_box(d5, "Bus Stop 09048 · Orchard Stn", 100, 205, text_color=(255, 255, 255))
    img5.save(os.path.join(OUTPUT_DIR, "05_street_sign.png"))

    # 6. Screenshot with API Credentials
    img6 = Image.new('RGB', (550, 350), (24, 24, 28)) # Dark IDE
    d6 = ImageDraw.Draw(img6)
    _draw_text_box(d6, "# config/secrets.env", 25, 25, text_color=(120, 120, 140))
    _draw_text_box(d6, 'GITHUB_TOKEN = "ghp_' + 'a'*36 + '"', 25, 75, text_color=(230, 200, 100))
    _draw_text_box(d6, 'AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"', 25, 125, text_color=(230, 200, 100))
    _draw_text_box(d6, 'OPENAI_API_KEY = "sk-proj-' + 'x'*36 + '"', 25, 175, text_color=(230, 200, 100))
    _draw_text_box(d6, 'GOOGLE_API_KEY = "AIzaSyD' + 'w'*32 + '"', 25, 225, text_color=(230, 200, 100))
    _draw_text_box(d6, "# WARNING: Do not commit secrets", 25, 285, text_color=(220, 80, 80))
    img6.save(os.path.join(OUTPUT_DIR, "06_api_credentials.png"))

    # 7. Screenshot with Emails and Passwords
    img7 = Image.new('RGB', (500, 300), (32, 34, 40))
    d7 = ImageDraw.Draw(img7)
    _draw_text_box(d7, "Account Credentials", 30, 30, text_color=(180, 180, 220))
    _draw_text_box(d7, "Email: developer_student@school.edu.sg", 30, 85, text_color=(240, 240, 240))
    _draw_text_box(d7, "password = SecretPassword2026!", 30, 135, text_color=(240, 240, 240))
    _draw_text_box(d7, "pin = 8492", 30, 185, text_color=(240, 240, 240))
    _draw_text_box(d7, "Server IP: 10.0.1.45", 30, 235, text_color=(200, 200, 200))
    img7.save(os.path.join(OUTPUT_DIR, "07_passwords.png"))

    # 8. Document with Identity Fields
    img8 = Image.new('RGB', (500, 350), (255, 255, 252))
    d8 = ImageDraw.Draw(img8)
    _draw_text_box(d8, "OFFICIAL VERIFICATION FORM", 120, 30, text_color=(20, 20, 20))
    _draw_text_box(d8, "Full Name: Jamie Lee Chen", 40, 80)
    _draw_text_box(d8, "NRIC: T0512345A", 40, 125)
    _draw_text_box(d8, "Residential Address: Blk 321 Bedok North St 1, #08-99", 40, 170)
    _draw_text_box(d8, "Contact Phone: 8123 4567", 40, 215)
    _draw_text_box(d8, "Card Number: 4111 1111 1111 1111", 40, 260)
    img8.save(os.path.join(OUTPUT_DIR, "08_identity_fields.png"))

    # 9. Face Drawing (Synthesized face illustration)
    img9 = Image.new('RGB', (400, 400), (240, 240, 245))
    d9 = ImageDraw.Draw(img9)
    # Draw stylized oval face
    d9.ellipse([100, 80, 300, 320], fill=(250, 220, 195), outline=(120, 80, 50), width=3)
    # Eyes
    d9.ellipse([140, 150, 175, 175], fill=(50, 40, 30))
    d9.ellipse([225, 150, 260, 175], fill=(50, 40, 30))
    # Nose
    d9.line([(200, 180), (195, 220), (210, 220)], fill=(120, 80, 50), width=3)
    # Smile
    d9.arc([160, 230, 240, 270], start=10, end=170, fill=(180, 60, 60), width=4)
    img9.save(os.path.join(OUTPUT_DIR, "09_face.png"))

    # 10. Multiple QR Codes
    enc = cv2.QRCodeEncoder_create()
    qr1 = enc.encode("https://privacylens.test/qr1")
    qr2 = enc.encode("https://privacylens.test/qr2")
    qr1_resized = cv2.resize(qr1, (120, 120), interpolation=cv2.INTER_NEAREST)
    qr2_resized = cv2.resize(qr2, (120, 120), interpolation=cv2.INTER_NEAREST)

    canvas10 = np.full((320, 450), 255, dtype=np.uint8)
    canvas10[100:220, 60:180] = qr1_resized
    canvas10[100:220, 270:390] = qr2_resized
    img10 = Image.fromarray(canvas10).convert('RGB')
    d10 = ImageDraw.Draw(img10)
    _draw_text_box(d10, "Registration Pass QRs", 130, 35, text_color=(30, 30, 30))
    img10.save(os.path.join(OUTPUT_DIR, "10_multiple_qr.png"))

    # 11. Image with Embedded EXIF GPS Metadata
    img11 = Image.new('RGB', (400, 300), (180, 210, 230))
    d11 = ImageDraw.Draw(img11)
    _draw_text_box(d11, "Scenic Park Photo", 120, 130, text_color=(40, 60, 80))
    exif11 = img11.getexif()
    gps_ifd = exif11.get_ifd(ExifTags.IFD.GPSInfo)
    gps_ifd[1] = 'N'
    gps_ifd[2] = (1.0, 21.0, 12.34)  # Singapore coordinates
    gps_ifd[3] = 'E'
    gps_ifd[4] = (103.0, 50.0, 34.56)
    exif11[34853] = gps_ifd
    exif11[305] = "PrivacyLens Test Camera"
    exif11[306] = "2026:11:06 08:30:00"
    img11.save(os.path.join(OUTPUT_DIR, "11_exif_metadata.jpg"), exif=exif11)

    # 12. Multi-Exposure Composite Image (Contains 6+ privacy categories)
    img12 = Image.new('RGB', (600, 500), (245, 245, 250))
    d12 = ImageDraw.Draw(img12)
    _draw_text_box(d12, "STUDENT PORTAL PROFILE", 190, 25, text_color=(20, 40, 100))

    # Badge/School name
    _draw_text_box(d12, "Raffles Institution Secondary School", 40, 75, text_color=(10, 80, 40))

    # PII Fields
    _draw_text_box(d12, "Recipient: Marcus Tan", 40, 120)
    _draw_text_box(d12, "NRIC: S9912345Z", 40, 160)
    _draw_text_box(d12, "Email: marcus.tan@student.edu.sg", 40, 200)
    _draw_text_box(d12, "Phone: +65 9123 4567", 40, 240)
    _draw_text_box(d12, "Address: Blk 100 Bishan St 12, #05-20", 40, 280)

    # Credentials
    _draw_text_box(d12, "password = Bishan2026Secret!", 40, 330, text_color=(180, 40, 40))
    _draw_text_box(d12, "API: ghp_" + "m"*36, 40, 370, text_color=(180, 40, 40))

    # Timetable / routine
    _draw_text_box(d12, "Daily Class Timetable · Period 1 to 8", 40, 420, text_color=(100, 100, 100))

    # Paste QR code on the right side
    qr_comp = enc.encode("https://privacylens.test/student/profile")
    qr_comp_resized = cv2.resize(qr_comp, (110, 110), interpolation=cv2.INTER_NEAREST)
    qr_pil = Image.fromarray(qr_comp_resized).convert('RGB')
    img12.paste(qr_pil, (450, 100))
    _draw_text_box(d12, "[PORTAL QR]", 455, 220, text_color=(100, 100, 100))

    img12.save(os.path.join(OUTPUT_DIR, "12_multi_exposure_composite.png"))

    print("All 12 synthetic test images generated successfully.")


if __name__ == '__main__':
    generate_all()
