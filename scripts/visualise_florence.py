import torch
from backend.privacy_engine import analyse_privacy
import json
from PIL import Image, ImageDraw, ImageFont
from transformers import (
    AutoProcessor,
    Florence2ForConditionalGeneration
)

MODEL_ID = "florence-community/Florence-2-base-ft"
# IMAGE_PATH = "guangyang_pe.png"
IMAGE_PATH = "privacy_test.png"

device = "cuda" if torch.cuda.is_available() else "cpu"

print("Loading Florence-2...")

processor = AutoProcessor.from_pretrained(MODEL_ID)

model = Florence2ForConditionalGeneration.from_pretrained(
    MODEL_ID,
    attn_implementation="eager"
).to(device)

model.eval()

image = Image.open(IMAGE_PATH).convert("RGB")
output_image = image.copy()
draw = ImageDraw.Draw(output_image)


def run_task(task):
    inputs = processor(
        text=task,
        images=image,
        return_tensors="pt"
    ).to(device)

    with torch.inference_mode():
        ids = model.generate(
            **inputs,
            max_new_tokens=512,
            num_beams=3
        )

    text = processor.batch_decode(
        ids,
        skip_special_tokens=False
    )[0]

    return processor.post_process_generation(
        text,
        task=task,
        image_size=image.size
    )


# Detect objects
objects = run_task("<OD>")["<OD>"]

for box, label in zip(
    objects["bboxes"],
    objects["labels"]
):
    draw.rectangle(
        box,
        outline="blue",
        width=4
    )

    draw.text(
        (box[0], max(0, box[1] - 20)),
        label,
        fill="blue"
    )


# Detect text
ocr = run_task("<OCR_WITH_REGION>")[
    "<OCR_WITH_REGION>"
]

for quad, label in zip(
    ocr["quad_boxes"],
    ocr["labels"]
):
    # OCR returns a quadrilateral.
    points = [
        (quad[i], quad[i + 1])
        for i in range(0, 8, 2)
    ]

    draw.line(
        points + [points[0]],
        fill="red",
        width=4
    )

    print("Detected text:", label)


output_image.save("detected_output.png")

print("Saved detected_output.png")

# Analyse potential privacy exposure
privacy_result = analyse_privacy(objects, ocr)

print("\n=== PRIVACYLENS RESULTS ===")
print(json.dumps(privacy_result, indent=2))

# Save structured results for future React integration
with open("privacy_results.json", "w", encoding="utf-8") as file:
    json.dump(
        privacy_result,
        file,
        indent=2,
        ensure_ascii=False
    )

print("\nSaved privacy_results.json")

