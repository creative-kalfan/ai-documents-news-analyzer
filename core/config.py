# core/config.py
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SAMPLES_DIR = os.path.join(DATA_DIR, "samples")

# HARD SET TESSERACT PATH HERE
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
