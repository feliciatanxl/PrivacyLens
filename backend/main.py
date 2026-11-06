"""PrivacyLens Local MVP: Florence-2 + Specialised Privacy Detectors."""
import io
import json
import threading
import time
from contextlib import asynccontextmanager
from typing import List, Optional

import torch
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image, ImageOps, UnidentifiedImageError
from transformers import AutoProcessor, Florence2ForConditionalGeneration

from .privacy_engine import analyse_privacy
from .detectors.paddle_ocr_detector import detect_text_paddle, is_paddle_ocr_available
from .services.exposure_engine import explain_exposure
from .services.redaction_service import redact_image, verify_redaction

MODEL_ID = 'florence-community/Florence-2-base-ft'
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
MAX_BYTES = 10 * 1024 * 1024
MAX_PIXELS = 12_000_000
processor = None
model = None
model_lock = threading.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global processor, model
    # Tune threads for CPU inference to avoid core thrashing
    try:
        torch.set_num_threads(8)
    except Exception:
        pass
    print('Loading Florence-2 model...')
    try:
        processor = AutoProcessor.from_pretrained(MODEL_ID)
        model = Florence2ForConditionalGeneration.from_pretrained(
            MODEL_ID, attn_implementation='eager'
        ).to(DEVICE)
        model.eval()
        print('PrivacyLens AI engine loaded successfully on', DEVICE)
    except Exception as exc:
        print(f'Warning: Could not load Florence-2 ({exc}). Offline/fallback mode active.')
    yield


app = FastAPI(
    title='PrivacyLens API',
    description='AI-powered sensitive information detection and exposure reconstruction engine.',
    version='1.0.0',
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'OPTIONS'],
    allow_headers=['*'],
)


def florence_task(image: Image.Image, task: str, max_tokens: int = 256):
    """Run an inference task using Florence-2 with greedy search and resolution scaling."""
    if processor is None or model is None:
        return {}

    w, h = image.size
    max_dim = max(w, h)
    scale = 1.0
    infer_img = image
    if max_dim > 768:
        scale = 768.0 / max_dim
        new_w = max(1, int(round(w * scale)))
        new_h = max(1, int(round(h * scale)))
        infer_img = image.resize((new_w, new_h), Image.Resampling.BILINEAR)

    inputs = processor(text=task, images=infer_img, return_tensors='pt').to(DEVICE)
    with torch.inference_mode():
        tokens = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            num_beams=1,
            do_sample=False
        )
    generated = processor.batch_decode(tokens, skip_special_tokens=False)[0]
    result = processor.post_process_generation(generated, task=task, image_size=infer_img.size).get(task, {})

    if scale != 1.0 and result:
        inv_scale = 1.0 / scale
        if 'bboxes' in result:
            result['bboxes'] = [
                [int(round(c * inv_scale)) for c in box]
                for box in result['bboxes']
            ]
        if 'quad_boxes' in result:
            result['quad_boxes'] = [
                [int(round(c * inv_scale)) for c in quad]
                for quad in result['quad_boxes']
            ]
    return result


@app.get('/health')
def health():
    return {
        'status': 'ready' if model is not None else 'offline_mode',
        'device': DEVICE,
        'model': MODEL_ID,
        'model_loaded': model is not None,
        'paddleocr_available': is_paddle_ocr_available(),
        'version': '1.0.0'
    }


def _load_image_safely(file: UploadFile) -> Image.Image:
    """Validate and safely load image bytes."""
    if file.content_type not in ('image/png', 'image/jpeg', 'image/jpg', 'image/webp'):
        raise HTTPException(400, 'Please upload a PNG, JPEG, or WebP image.')
    raw = file.file.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise HTTPException(413, 'Image exceeds maximum 10 MB file size.')
    try:
        original = Image.open(io.BytesIO(raw))
        original.load()
        if original.width * original.height > MAX_PIXELS:
            raise HTTPException(413, 'Image dimensions exceed the 12-megapixel limit.')
        return original
    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(400, 'Invalid or corrupted image file.')


@app.post('/analyze')
def analyze(
    file: UploadFile = File(...),
    scan_mode: Optional[str] = Form('auto')
):
    """Run comprehensive privacy analysis across all 15 categories with hybrid model routing."""
    t_start = time.perf_counter()
    original = _load_image_safely(file)

    # Transpose according to EXIF orientation so boxes align with visual orientation
    transposed = ImageOps.exif_transpose(original)
    image = transposed.convert('RGB')

    objects = {}
    ocr = {}
    ocr_engine_used = 'none'

    mode = (scan_mode or 'auto').strip().lower()

    # 1. Primary OCR: Attempt ultra-fast PaddleOCR
    if is_paddle_ocr_available():
        try:
            paddle_ocr = detect_text_paddle(image)
            if paddle_ocr.get('labels'):
                ocr = paddle_ocr
                ocr_engine_used = 'paddleocr'
        except Exception as exc:
            print('Warning: PaddleOCR failed:', exc)

    # 2. Decide whether Florence-2 OD is needed
    run_od = mode in ('comprehensive', 'deep', 'full')
    if mode == 'auto':
        run_od = True

    if model is not None and run_od:
        with model_lock:
            try:
                objects = florence_task(image, '<OD>', max_tokens=256)
            except Exception as exc:
                print('Warning: Florence-2 <OD> failed:', exc)

    # 3. Fallback to Florence-2 OCR if PaddleOCR didn't find text or was unavailable
    if model is not None and not ocr.get('labels') and mode != 'fast_only':
        with model_lock:
            try:
                florence_ocr = florence_task(image, '<OCR_WITH_REGION>', max_tokens=384)
                if florence_ocr.get('labels'):
                    ocr = florence_ocr
                    ocr_engine_used = 'florence-2'
            except Exception as exc:
                print('Warning: Florence-2 <OCR_WITH_REGION> failed:', exc)

    # Pass original so metadata detector can extract raw EXIF tags
    privacy = analyse_privacy(original, objects=objects, ocr=ocr)
    exposure = explain_exposure(privacy['findings'])
    elapsed_ms = (time.perf_counter() - t_start) * 1000

    return {
        'image_size': {'width': image.width, 'height': image.height},
        'privacy': privacy,
        'exposure': exposure,
        'metadata': {
            'scan_mode': mode,
            'ocr_engine': ocr_engine_used,
            'execution_time_ms': round(elapsed_ms, 1),
            'paddleocr_available': is_paddle_ocr_available(),
            'florence_available': model is not None,
        }
    }


@app.post('/redact')
def redact(
    file: UploadFile = File(...),
    boxes: str = Form('[]'),
    margin: int = Form(4)
):
    """
    Redact specified bounding boxes with solid opaque blackouts
    and return sanitized image with all EXIF metadata stripped.
    """
    original = _load_image_safely(file)
    transposed = ImageOps.exif_transpose(original)
    image = transposed.convert('RGB')

    try:
        box_list = json.loads(boxes)
        if not isinstance(box_list, list):
            box_list = []
    except Exception:
        raise HTTPException(400, 'Invalid boxes format. Must be a JSON array of boxes.')

    redacted_image = redact_image(image, box_list, margin=margin)

    # Verify that redaction succeeded
    verification = verify_redaction(image, redacted_image, box_list)

    buf = io.BytesIO()
    redacted_image.save(buf, format='PNG')
    buf.seek(0)

    headers = {
        'X-Redacted-Boxes-Count': str(verification['boxes_verified']),
        'X-Metadata-Stripped': str(verification['metadata_stripped']),
        'Content-Disposition': 'inline; filename="privacylens_protected.png"'
    }

    return StreamingResponse(buf, media_type='image/png', headers=headers)
