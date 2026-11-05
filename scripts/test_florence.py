import torch
from PIL import Image
from transformers import AutoProcessor, Florence2ForConditionalGeneration

MODEL_ID = "florence-community/Florence-2-base-ft"

device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if device == "cuda" else torch.float32


print("Device:", device)
print("Loading Florence-2...")

processor = AutoProcessor.from_pretrained(
    MODEL_ID
)

model = Florence2ForConditionalGeneration.from_pretrained(
    MODEL_ID,
    dtype=dtype,
    attn_implementation="eager"
).to(device)

model.eval()

image = Image.open("guangyang_pe.png").convert("RGB")


def analyse(task):
    inputs = processor(
        text=task,
        images=image,
        return_tensors="pt"
    )

    inputs = {
        key: value.to(device)
        for key, value in inputs.items()
    }

    if device == "cuda":
        inputs["pixel_values"] = inputs["pixel_values"].to(dtype)

    with torch.inference_mode():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=512,
            num_beams=3
        )

    generated_text = processor.batch_decode(
        generated_ids,
        skip_special_tokens=False
    )[0]

    result = processor.post_process_generation(
        generated_text,
        task=task,
        image_size=image.size
    )

    return result


print("\n=== IMAGE DESCRIPTION ===")
print(analyse("<MORE_DETAILED_CAPTION>"))

print("\n=== OBJECT DETECTION ===")
print(analyse("<OD>"))

print("\n=== OCR ===")
print(analyse("<OCR_WITH_REGION>"))
