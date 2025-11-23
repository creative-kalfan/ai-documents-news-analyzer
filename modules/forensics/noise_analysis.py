# modules/forensics/noise_analysis.py
import numpy as np
from PIL import Image
import io
import cv2

def analyze_noise(image_bytes: bytes):
    """Simple noise consistency check using Laplacian variance."""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
    except:
        return {"noise_score": 0, "issue": "Cannot read Image"}

    arr = np.array(img)

    # Laplacian variance - high variance = sharper areas
    lap = cv2.Laplacian(arr, cv2.CV_64F)
    variance = lap.var()

    # heuristic:
    # too low variance → overly smoothed → suspicious editing
    # too high difference across blocks → possible tampering
    if variance < 25:
        issue = "Image overly smooth — possible editing"
        penalty = 20
    else:
        issue = "Noise levels normal"
        penalty = 0

    return {
        "variance": float(variance),
        "issue": issue,
        "score_penalty": penalty
    }
