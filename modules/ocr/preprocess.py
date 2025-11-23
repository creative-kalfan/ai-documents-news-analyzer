# modules/ocr/preprocess.py
from PIL import Image
import numpy as np
import cv2

def preprocess_pil_image(pil_img, resize_max=2000):
    img = pil_img.convert("RGB")
    w, h = img.size
    max_dim = max(w, h)

    # resize large images
    if max_dim > resize_max:
        scale = resize_max / max_dim
        img = img.resize((int(w * scale), int(h * scale)))

    arr = np.array(img)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

    # Denoise
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # Adaptive threshold for better OCR
    try:
        th = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
    except:
        _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return Image.fromarray(th)
