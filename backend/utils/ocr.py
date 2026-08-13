# backend/utils/ocr.py
import easyocr
import numpy as np
from PIL import Image
import io

reader = easyocr.Reader(['en'], gpu=False)  # loaded once at import, like the embedding model


def ocr_pil_image(pil_image: Image.Image) -> str:
    try:
        img_array = np.array(pil_image.convert("RGB"))
        results = reader.readtext(img_array, detail=0)  # detail=0 -> plain text list, no bounding boxes
        return " ".join(results).strip()
    except Exception as e:
        print(f"OCR failed: {e}")
        return ""


def ocr_image_bytes(image_bytes: bytes) -> str:
    try:
        pil_image = Image.open(io.BytesIO(image_bytes))
        return ocr_pil_image(pil_image)
    except Exception as e:
        print(f"OCR failed to open image: {e}")
        return ""