# modules/ocr/handwriting.py
from paddleocr import PaddleOCR
import tempfile
from core.utils import bytes_to_pil

htr_engine = PaddleOCR(
    det_model_dir=None,  # use recognition only
    rec_model_dir="ch_ppocr_mobile_v2.0_rec",  # handwriting-capable model
    use_gpu=False,
    lang="en",
    show_log=False
)

def handwriting_ocr(file_bytes):
    pil_img = bytes_to_pil(file_bytes)

    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        pil_img.save(tmp.name)
        result = htr_engine.ocr(tmp.name)

    text = ""
    if result:
        for line in result:
            for box, (txt, conf) in line:
                text += txt + " "

    return text.strip()
