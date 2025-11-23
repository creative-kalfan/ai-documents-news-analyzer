# modules/forensics/metadata_check.py
from PIL import Image
from PIL.ExifTags import TAGS
import io

SUSPICIOUS_SOFTWARE = ["Photoshop", "GIMP", "Snapseed", "PicsArt", "PixelLab"]

def extract_metadata(image_bytes: bytes):
    """Extract EXIF metadata as a readable dict."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        exif_data = img.getexif()
    except Exception:
        return {"error": "Cannot read EXIF metadata"}

    metadata = {}
    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        metadata[tag] = str(value)

    return metadata


def analyze_metadata(metadata: dict):
    """Detect suspicious EXIF signs."""
    if "error" in metadata:
        return {
            "metadata_valid": False,
            "issues": ["No EXIF metadata found"],
            "score_penalty": 40
        }

    issues = []
    penalty = 0

    # 1. Check for editing software
    software = metadata.get("Software", "").lower()
    if any(sw.lower() in software for sw in SUSPICIOUS_SOFTWARE):
        issues.append(f"Edited using software: {software}")
        penalty += 40

    # 2. Missing timestamps
    if "DateTime" not in metadata:
        issues.append("Missing DateTime metadata")
        penalty += 15

    # 3. Check camera model
    if "Model" not in metadata and "Make" not in metadata:
        issues.append("Missing Camera Model/Make — likely edited or scanned")
        penalty += 20

    return {
        "metadata_valid": len(issues) == 0,
        "issues": issues,
        "score_penalty": penalty
    }
