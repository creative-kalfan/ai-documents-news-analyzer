# modules/ocr/ocr_service.py

from paddleocr import PaddleOCR
from modules.ocr.preprocess import preprocess_pil_image
from modules.ocr.layout import analyze_layout
from modules.ocr.handwriting import handwriting_ocr
from modules.ocr.idcard_extractor import extract_fields
from core.utils import bytes_to_pil
from pdf2image import convert_from_bytes
import tempfile


# Main OCR engine
ocr_engine = PaddleOCR(
    use_angle_cls=True,
    lang='en',
    use_gpu=False,
    show_log=False
)


def ocr_image_bytes(file_bytes: bytes) -> dict:
    """Full enhanced OCR for images."""
    pil_img = preprocess_pil_image(bytes_to_pil(file_bytes))

    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        pil_img.save(tmp.name)
        result = ocr_engine.ocr(tmp.name, cls=True)

    text = " ".join([txt for block in result for box, (txt, conf) in block])

    layout = analyze_layout(file_bytes)
    handwriting = handwriting_ocr(file_bytes)
    id_fields = extract_fields(text)

    return {
        "text": text.strip(),
        "layout": layout,
        "handwriting": handwriting,
        "id_fields": id_fields
    }


def ocr_pdf_bytes(file_bytes: bytes) -> dict:
    """Full enhanced OCR for multipage PDFs."""
    pages = convert_from_bytes(file_bytes, dpi=180)
    full_text = ""
    combined_layout = []
    all_handwriting = []
    id_fields_collected = {}

    for page in pages:
        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            page.save(tmp.name)

            result = ocr_engine.ocr(tmp.name, cls=True)
            if result:
                page_text = " ".join([txt for block in result for box, (txt, conf) in block])
                full_text += page_text + "\n"

            combined_layout.append(analyze_layout(open(tmp.name, 'rb').read()))
            all_handwriting.append(handwriting_ocr(open(tmp.name, 'rb').read()))

    id_fields_collected = extract_fields(full_text)

    return {
        "text": full_text.strip(),
        "layout": combined_layout,
        "handwriting": all_handwriting,
        "id_fields": id_fields_collected
    }


def extract_text_from_upload(file_bytes, filename):
    ext = filename.lower().split(".")[-1]

    if ext == "pdf":
        return ocr_pdf_bytes(file_bytes)
    return ocr_image_bytes(file_bytes)
