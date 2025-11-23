# modules/forensics/forensic_pipeline.py
from modules.forensics.metadata_check import extract_metadata, analyze_metadata
from modules.forensics.noise_analysis import analyze_noise
from modules.forensics.ela import perform_ela
from modules.forensics.tamper_detection import detect_tampering

def analyze_document_forensics(image_bytes: bytes):
    """Runs full hybrid forensic analysis."""
    # 1. Metadata
    metadata = extract_metadata(image_bytes)
    meta_report = analyze_metadata(metadata)

    # 2. Noise Analysis
    noise_report = analyze_noise(image_bytes)

    # 3. ELA
    ela_img, ela_score = perform_ela(image_bytes)

    # 4. Tamper detection
    tamper_heatmap, tamper_score, tamper_details = detect_tampering(image_bytes)

    # Combine scores (weighted)
    total_penalty = (
        meta_report["score_penalty"]
        + noise_report["score_penalty"]
        + int(ela_score * 0.3)
        + int(tamper_score * 0.5)
    )

    fraud_score = min(100, total_penalty)

    return {
        "fraud_score": fraud_score,
        "metadata_report": meta_report,
        "noise_report": noise_report,
        "ela_score": ela_score,
        "ela_image": ela_img,
        "tamper_score": tamper_score,
        "tamper_details": tamper_details,
        "tamper_heatmap": tamper_heatmap
    }
