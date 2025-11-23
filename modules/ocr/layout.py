import io
import cv2
import numpy as np
from PIL import Image

# NEW paddleocr imports for PPStructureV3
from paddleocr import PPStructureV3

# NEW location of draw function (works for PaddleOCR 2.7+)
try:
    from paddleocr.ppstructure.utility import draw_structure_result
except:
    # fallback for other versions
    from paddleocr.ppstructure.recovery.recovery_to_doc import convert_info_docx as draw_structure_result


# Initialize the advanced layout + OCR engine
engine = PPStructureV3(show_log=False)


def analyze_layout(file_bytes):
    # Convert bytes → PIL → OpenCV
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # Run the full layout engine
    result = engine(img_np)

    # Try to draw visual layout output
    vis = None
    try:
        vis = draw_structure_result(img_np, result)
    except Exception:
        pass  # safe fallback

    return result, vis
