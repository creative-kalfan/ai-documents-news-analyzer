# modules/genai/explain_doc.py

import os
from modules.genai.llm_engine import run_llm

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "doc_prompt.txt")

def load_prompt():
    try:
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "You are an AI forensic expert. Explain the document authenticity."

def explain_document(ocr_text: str, forensic_summary: dict):
    base_prompt = load_prompt()
    full_prompt = (
        base_prompt
        + "\n\nOCR_TEXT:\n"
        + ocr_text
        + "\n\nFORENSICS:\n"
        + str(forensic_summary)
        + "\n\nGenerate explanation:"
    )
    return run_llm(full_prompt)
