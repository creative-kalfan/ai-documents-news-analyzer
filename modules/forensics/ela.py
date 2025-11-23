# modules/forensics/ela.py
from PIL import Image, ImageChops, ImageEnhance
import io

def perform_ela(image_bytes: bytes, quality=85):
    """Perform Error Level Analysis and return ELA image + score."""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except:
        return None, 0

    # recompress
    tmp = io.BytesIO()
    img.save(tmp, 'JPEG', quality=quality)
    tmp.seek(0)
    compressed = Image.open(tmp)

    # Difference
    ela_img = ImageChops.difference(img, compressed)
    extrema = ela_img.getextrema()

    # Compute max difference for scoring
    max_diff = max([ex[1] for ex in extrema])
    score = min(100, max_diff * 2)  # normalize score

    # Enhance for visualization
    enhancer = ImageEnhance.Brightness(ela_img)
    ela_highlight = enhancer.enhance(30)

    return ela_highlight, score
