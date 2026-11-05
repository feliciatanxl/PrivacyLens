"""PrivacyLens Local MVP: Florence-2 + Specialised Privacy Detectors."""
import io
import json
import threading
from contextlib import asynccontextmanager
from typing import List, Optional

import torch
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image, ImageOps, UnidentifiedImageError
from transformers import AutoProcessor, Florence2ForConditionalGeneration

from .privacy_engine import analyse_privacy
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


def florence_task(image: Image.Image, task: str):
    """Run an inference task using Florence-2."""
    if processor is None or model is None:
        return {}
    inputs = processor(text=task, images=image, return_tensors='pt').to(DEVICE)
    with torch.inference_mode():
        tokens = model.generate(
            **inputs,
            max_new_tokens=512,
            num_beams=3,
            do_sample=False
        )
    generated = processor.batch_decode(tokens, skip_special_tokens=False)[0]
    return processor.post_process_generation(generated, task=task, image_size=image.size).get(task, {})


@app.get('/health')
def health():
    return {
        'status': 'ready' if model is not None else 'offline_mode',
        'device': DEVICE,
        'model': MODEL_ID,
        'model_loaded': model is not None,
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
def analyze(file: UploadFile = File(...)):
    """Run comprehensive privacy analysis across all 15 categories."""
    original = _load_image_safely(file)

    # Transpose according to EXIF orientation so boxes align with visual orientation
    transposed = ImageOps.exif_transpose(original)
    image = transposed.convert('RGB')

    objects = {}
    ocr = {}

    if model is not None:
        with model_lock:
            try:
                objects = florence_task(image, '<OD>')
            except Exception as exc:
                print('Warning: Florence-2 <OD> failed:', exc)
            try:
                ocr = florence_task(image, '<OCR_WITH_REGION>')
            except Exception as exc:
                print('Warning: Florence-2 <OCR_WITH_REGION> failed:', exc)

    # Pass original so metadata detector can extract raw EXIF tags
    privacy = analyse_privacy(original, objects=objects, ocr=ocr)
    exposure = explain_exposure(privacy['findings'])

    return {
        'image_size': {'width': image.width, 'height': image.height},
        'privacy': privacy,
        'exposure': exposure,
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
