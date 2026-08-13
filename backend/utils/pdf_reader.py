# backend/utils/pdf_reader.py
import pdfplumber
from utils.ocr import ocr_pil_image


def extract_text_from_pdf(pdf_file):
    text = ""
    tables_text = ""
    images_text = ""

    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ""
            text += page_text + "\n"

            for table in page.extract_tables():
                tables_text += "\n[TABLE]\n"
                for row in table:
                    clean_row = [cell if cell else "" for cell in row]
                    tables_text += " | ".join(clean_row) + "\n"
                tables_text += "[/TABLE]\n"

            for img in page.images:
                try:
                    bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
                    cropped = page.within_bbox(bbox)
                    pil_image = cropped.to_image(resolution=200).original
                    ocr_text = ocr_pil_image(pil_image)
                    if ocr_text:
                        images_text += f"\n[IMAGE TEXT, page {page_num + 1}]\n{ocr_text}\n"
                except Exception:
                    continue

    return text + "\n" + tables_text + "\n" + images_text