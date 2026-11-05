# PrivacyLens — AI Privacy Protection & Exposure Reconstruction

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.11](https://img.shields.io/badge/Python-3.11-brightgreen.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg)]()
[![React: 19](https://img.shields.io/badge/React-19-61DAFB.svg)]()
[![Vite](https://img.shields.io/badge/Vite-8-646CFF.svg)]()
[![Vision: Florence--2](https://img.shields.io/badge/Vision-Florence--2--base-orange.svg)]()

> **Hackathon Theme:** Spot It! Stop It! — Problem Statement 01: Set Boundaries Online  
> **Mission:** Empower youths to identify sensitive personal information in screenshots, photos, documents, and social media posts **before they share them online**.

---

## 1. Executive Summary & Core USP

Privacy harms rarely happen from a single isolated clue. Instead, online predators, identity thieves, and malicious actors practice **The Mosaic Effect**: assembling seemingly benign fragments (a school sports jersey, a street sign in the background, a class timetable, and a partial phone number) to construct an individual's real-world identity, daily commute, and home location.

**PrivacyLens's Core USP is AI Exposure Reconstruction:**
Rather than simply tagging bounding boxes with arbitrary risk scores, PrivacyLens:
1. **Detects 15 distinct privacy categories** across visual objects, optical characters, biometrics, barcodes, and metadata.
2. **Synthesizes multi-clue exposure scenarios**, explaining to youths *how* specific combinations of clues compromise safety.
3. **Provides interactive solid-opaque redaction and automated EXIF/GPS stripping** with one-click export.

---

## 2. Supported Detection Categories Matrix

PrivacyLens combines Microsoft Florence-2 with specialized computer vision, optical character recognition, and cryptographic heuristics:

| No. | Category | Detection Mechanism | Severity | Threat Vector / Exposure |
|:---:|:---|:---|:---:|:---|
| **1** | **School Uniforms** | Florence-2 OD + OCR contextual heuristics | Review | Identifies educational affiliation & student attire |
| **2** | **School Badges / Logos** | Vision grounding + Institutional NER | High | Pinpoints the specific school attended |
| **3** | **API Keys & Tokens** | High-entropy regex + Prefix signatures (GitHub, AWS, OpenAI, Google, Slack, Stripe, JWT) | High | Account takeover, credential leaks, and data breaches |
| **4** | **Passwords & Credentials** | Key-value contextual assignment patterns | High | Account compromise & unauthorized access |
| **5** | **Email Addresses** | RFC 5322 regex extraction | High | Phishing, spam, and identity linkage |
| **6** | **Phone Numbers** | Singapore (+65 / 8xxx / 9xxx / 6xxx) & E.164 International | High | Harassment, scam calls, and SIM swap vectors |
| **7** | **Personal Names** | Labelled prefixes (`Recipient:`, `Cardholder:`) & Honorific NER | Review | Direct individual identification |
| **8** | **Residential Addresses** | Blk/Street/Unit parsing, SG 6-digit postal codes, & shipping labels | High | Discloses private home & residence location |
| **9** | **National Identifiers** | Singapore NRIC/FIN + US SSN + Passport formats | High | Identity theft, fraud, and impersonation |
| **10** | **Payment Cards** | 13–19 digit detection validated by **Luhn checksum** | High | Financial fraud and unauthorized billing |
| **11** | **Faces** | OpenCV Haar cascades (frontal + profile) + Vision fallback | Review | Biometric facial identification |
| **12** | **QR Codes** | OpenCV QRCodeDetector (Aruco + multi-thresholding) | Review | Hidden URLs, auth sessions, and payment links |
| **13** | **IP Addresses** | Public IPv4, internal IPv4 (RFC 1918), and IPv6 | Review | Exposes network topology and device endpoints |
| **14** | **Street Signs & Transit** | OCR road suffixes (`Rd`, `Ave`, `St`) + Singapore Expressways & MRTs | Review | Physical transit corridors and neighborhood tracking |
| **15** | **GPS & EXIF Metadata** | Pillow IFD 34853 parsing + ExifRead | High | Covert GPS geotagging embedded in photo headers |

---

## 3. System Architecture

```mermaid
flowchart TD
    User["Youth / User"] -->|Uploads Image| WebUI["React 19 + Vite Frontend"]
    WebUI -->|POST /analyze| FastAPIServer["FastAPI Backend (Port 8000)"]
    
    subgraph PrivacyLens_Engine["PrivacyLens Detection & Reasoning Engine"]
        FastAPIServer --> Orientation["EXIF Orientation Normalization"]
        Orientation --> Dispatcher["Parallel Scanner Dispatcher"]
        
        Dispatcher --> F2_OCR["Florence-2 <OCR_WITH_REGION>"]
        Dispatcher --> F2_OD["Florence-2 <OD> Objects"]
        Dispatcher --> CV_Face["OpenCV Haar Cascades (Face)"]
        Dispatcher --> CV_QR["OpenCV Aruco Multi-QR"]
        Dispatcher --> EXIF_Meta["Pillow EXIF / GPS Inspector"]
        
        F2_OCR --> PII_Engine["PII Detector (Email, Phone, NRIC, SSN, Cards, IP, Address, Name)"]
        F2_OCR --> Secret_Engine["Secret Detector (API Keys, Passwords, Tokens)"]
        F2_OCR & F2_OD --> Visual_Engine["Visual Clues (School Badges, Uniforms, Street Signs, Schedules)"]
        
        PII_Engine & Secret_Engine & Visual_Engine & CV_Face & CV_QR & EXIF_Meta --> BoxMerge["Box Normalizer & Spatial Deduplicator (IoU)"]
        BoxMerge --> ExposureEngine["AI Exposure Reconstruction Engine"]
    end
    
    ExposureEngine -->|JSON Findings + Scenarios| WebUI
    
    subgraph Redaction_Workflow["Redaction & Export Pipeline"]
        WebUI -->|Selective Highlights + Manual Boxes| Viewport["Interactive Canvas (Inspection / Redacted Preview)"]
        Viewport -->|POST /redact| RedactionService["Redaction Service"]
        RedactionService --> SolidOpaque["Solid Opaque Blackout Overlay"]
        RedactionService --> StripEXIF["Cryptographic EXIF / GPS Metadata Stripping"]
        RedactionService --> PixelVerify["Pixel Overwrite Verification"]
        PixelVerify -->|Sanitized PNG Stream| User
    end
```

---

## 4. Key Capabilities & Implementation Highlights

1. **Independent Detector Execution & Fault Isolation:**  
   Every detector executes in its own isolated exception block. If an individual computer vision scanner fails, it flags `partial_scan` with an advisory note, rather than silently marking the image as clean.
2. **Sub-Pixel Coordinate Normalization & Quad Conversion:**  
   Florence-2 8-point quadrilateral coordinates and multi-word spans are dynamically grouped into enclosing integer bounding boxes clamped to image dimensions `[x1, y1, x2, y2]`.
3. **Zero Credential / PII Leaks in Logs:**  
   Detector output and logs intentionally omit raw matched secret strings, API keys, or identification numbers.
4. **Interactive Manual Box Selection:**  
   Users can click and drag directly on the image viewport in the frontend to draw custom redaction boxes over any subtle or unique items the AI missed.
5. **Solid Opaque Redaction with Metadata Obliteration:**  
   Unlike fragile client-side blurring (which can be reversed with deblurring AI), PrivacyLens renders 100% solid opaque black blocks (with 4px protective padding) and completely eliminates the EXIF header.

---

## 5. Getting Started

### Prerequisites
- Windows, macOS, or Linux
- Python 3.10+ (tested on Python 3.11)
- Node.js 18+ and npm

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/feliciatanxl/PrivacyLens.git
cd PrivacyLens

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

The API will be available at `http://127.0.0.1:8000` with Swagger docs at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 6. Automated Testing & Benchmark Evaluation

PrivacyLens includes a comprehensive test suite covering unit tests, negative controls, synthetic staged images, and end-to-end integration tests.

### Running the Tests
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run full test suite
python -m pytest tests/ -v
```

### Measured Benchmark Accuracy
Evaluated across a benchmark dataset of 8 diverse ground-truth multi-exposure scenarios (Delivery labels, Student ID cards, School clothing, Street signs, API credentials, Passwords, Payment forms, and Benign negative controls):

| Metric | Measured Value | Standard Target | Status |
|---|:---:|:---:|:---:|
| **Precision** | **86.36%** | ≥ 85.0% | Pass |
| **Recall** | **100.00%** | ≥ 90.0% | Pass |
| **F1-Score** | **92.68%** | ≥ 85.0% | Pass |
| **Scan Latency** | **197.6 ms** (CPU) | < 500 ms | Pass |
| **Metadata Stripping Verification** | **100.0%** | 100.0% | Pass |
| **Total Test Suite** | **35 / 35 Passed** | 100% Pass | Pass |

---

## 7. API Reference

### `GET /health`
Returns API readiness and active vision model status.
```json
{
  "status": "ready",
  "device": "cpu",
  "model": "florence-community/Florence-2-base-ft",
  "model_loaded": true,
  "version": "1.0.0"
}
```

### `POST /analyze`
Accepts `multipart/form-data` with an image file (`file`).
Returns:
- `image_size`: `{ width, height }`
- `privacy`: `{ status, findings, total_findings, scanners_executed, disclaimer }`
- `exposure`: `{ risk_level, possible_connections, exposure_scenarios, actionable_recommendations, educational_takeaways, summary }`

### `POST /redact`
Accepts `multipart/form-data`:
- `file`: Original image
- `boxes`: JSON string array of bounding boxes `[[x1, y1, x2, y2], ...]`
- `margin`: Integer pixel padding (default: 4)

Returns: Cleaned `image/png` binary stream with all selected boxes obscured in solid black and EXIF metadata stripped.

---

## 8. Known Limitations & Roadmap

1. **Florence-2 CPU Inference Time:**  
   On low-end CPU-only environments, running Florence-2 `<OCR_WITH_REGION>` and `<OD>` takes ~2–4 seconds per image. A future upgrade will introduce a lightweight local ONNX OCR pipeline (e.g. RapidOCR/PaddleOCR lightweight) for instantaneous local previews.
2. **Obscured or Stylized Badges:**  
   School badges on heavily wrinkled fabric or viewed from sharp angles may require manual box selection. The user drawing tool was added specifically to give users 100% confidence.
3. **Multi-Image Cross-Post Analysis:**  
   Future versions will support correlating clues across a user's entire social profile feed (e.g. linking a school badge from Photo A with a street sign from Photo B).

---

## 9. License

This project is licensed under the MIT License. Developed for the **Spot It! Stop It! Hackathon**.
