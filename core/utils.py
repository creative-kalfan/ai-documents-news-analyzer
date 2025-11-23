# core/utils.py
import io
from PIL import Image
import base64
from typing import List

def bytes_to_pil(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data)).convert("RGB")

def pil_to_bytes(pil_img, fmt="JPEG") -> bytes:
    buf = io.BytesIO()
    pil_img.save(buf, format=fmt)
    buf.seek(0)
    return buf.getvalue()

def image_bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")

def join_text_pages(pages: List[str]) -> str:
    pages_clean = [p.strip() for p in pages if p and p.strip()]
    return "\n\n----- PAGE BREAK -----\n\n".join(pages_clean)
