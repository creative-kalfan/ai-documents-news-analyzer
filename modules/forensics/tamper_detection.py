# modules/forensics/tamper_detection.py
import numpy as np
import cv2
from PIL import Image
import io


def generate_heatmap(mask):
    """Convert mask to color heatmap (red = suspicious)."""
    heatmap = cv2.applyColorMap(mask.astype(np.uint8), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    return Image.fromarray(heatmap)


def block_hash(img_gray, block_size=16):
    """
    Simple block-hash based copy-move detection.
    Divides image into blocks, hashes blocks, finds duplicates.
    """
    h, w = img_gray.shape
    blocks = {}
    matches = np.zeros((h, w), dtype=np.uint8)

    for y in range(0, h - block_size, block_size):
        for x in range(0, w - block_size, block_size):
            block = img_gray[y:y+block_size, x:x+block_size]
            b_hash = hash(block.tobytes())

            if b_hash in blocks:
                # Mark suspicious blocks
                matches[y:y+block_size, x:x+block_size] = 255
                prev_y, prev_x = blocks[b_hash]
                matches[prev_y:prev_y+block_size, prev_x:prev_x+block_size] = 255
            else:
                blocks[b_hash] = (y, x)

    return matches


def detect_edges_inconsistency(img_gray):
    """Detect sharp inconsistencies (possible splicing)."""
    lap = cv2.Laplacian(img_gray, cv2.CV_64F)
    lap_abs = np.abs(lap)

    # Normalize to 0–255
    if lap_abs.max() != 0:
        lap_norm = (lap_abs / lap_abs.max()) * 255
    else:
        lap_norm = lap_abs

    thresh = np.where(lap_norm > 180, 255, 0).astype(np.uint8)
    return thresh


def detect_tampering(image_bytes: bytes):
    """
    Hybrid tamper detection combining:
    - Copy-move (block hashing)
    - Edge inconsistency (splicing)
    Returns:
        heatmap (PIL Image)
        tamper_score (0–100)
        details (dict)
    """
    # Load image
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except:
        return None, 0, {"error": "Cannot read image"}

    arr = np.array(img)
    img_gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

    # 1. Copy-move detection
    copy_move_mask = block_hash(img_gray, block_size=16)

    # 2. Splicing detection
    splice_mask = detect_edges_inconsistency(img_gray)

    # Combine masks
    combined = np.maximum(copy_move_mask, splice_mask)

    # Compute tamper score
    tamper_pixels = np.sum(combined > 0)
    total_pixels = combined.size
    tamper_ratio = tamper_pixels / total_pixels

    tamper_score = min(100, int(tamper_ratio * 180))  # scaled

    # Create heatmap
    heatmap = generate_heatmap(combined)

    details = {
        "copy_move_pixels": int(np.sum(copy_move_mask > 0)),
        "splice_pixels": int(np.sum(splice_mask > 0)),
        "tamper_ratio": float(tamper_ratio)
    }

    return heatmap, tamper_score, details
