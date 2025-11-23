# run.py
"""
FastAPI backend for AI Fraud & Misinformation System.

Run:
    uvicorn run:app --host 127.0.0.1 --port 8000

Endpoints:
- POST /ocr                 -> multipart file upload -> returns extracted text
- POST /forensics           -> multipart file upload -> returns forensic analysis
- POST /fake-news           -> JSON { "text": "..."} -> returns classifier + evidence
- POST /llm-chat            -> JSON { "message": "..."} -> returns LLM reply (Ollama)
- POST /all-in-one          -> multipart file upload -> runs full pipeline and returns JSON
"""

import io
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from api.server import app

# local modules (reuse your existing code)
from modules.ocr.ocr_service import extract_text_from_upload
from modules.forensics.forensic_pipeline import analyze_document_forensics
from modules.news.preprocess import clean_text, extract_claims
from modules.news.classifier import NewsClassifier
from modules.news.rag_search import Retriever
from modules.genai.explain_doc import explain_document
from modules.genai.explain_news import explain_news
from modules.genai.llm_engine import run_llm

# sample file path (user-provided file saved in session)
SAMPLE_LOCAL_FILE = "/mnt/data/Screenshot 2025-11-22 233923.png"

app = FastAPI(title="AI Fraud & Misinformation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# singletons
_classifier = None
_retriever = None


def get_classifier():
    global _classifier
    if _classifier is None:
        try:
            _classifier = NewsClassifier("models/fake_news/distilbert_news")
        except Exception:
            _classifier = NewsClassifier("distilbert-base-uncased")
    return _classifier


def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


class TextPayload(BaseModel):
    text: str


class ChatPayload(BaseModel):
    message: str
    history: Optional[list] = None


@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    try:
        data = await file.read()
        text = extract_text_from_upload(data, file.filename)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/forensics")
async def forensics_endpoint(file: UploadFile = File(...)):
    try:
        data = await file.read()
        forensic = analyze_document_forensics(data)
        # Note: images (ela/tamper) are not returned as binary here; return metadata + base64 optionally
        return {"forensic": forensic}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/fake-news")
async def fake_news_endpoint(payload: TextPayload):
    try:
        text = payload.text
        cleaned = clean_text(text)
        claims = extract_claims(cleaned)
        clf = get_classifier()
        pred = clf.predict([cleaned])[0]
        retriever = get_retriever()
        evidence = retriever.query(claims[0] if claims else cleaned[:200], top_k=5)
        return {"prediction": pred, "claims": claims, "evidence": evidence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/llm-chat")
async def llm_chat(payload: ChatPayload):
    try:
        message = payload.message
        # Optionally pass history to the LLM prompt; for now send message directly
        reply = run_llm(message)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/all-in-one")
async def all_in_one(file: UploadFile = File(...)):
    """
    Runs OCR -> Forensics -> FakeNews -> GenAI on uploaded file and returns combined JSON.
    """
    try:
        data = await file.read()
        filename = file.filename
        # OCR
        text = extract_text_from_upload(data, filename)
        # Forensics
        forensic = analyze_document_forensics(data)
        # Fake news
        cleaned = clean_text(text)
        claims = extract_claims(cleaned)
        clf = get_classifier()
        pred = clf.predict([cleaned])[0]
        retriever = get_retriever()
        evidence = retriever.query(claims[0] if claims else cleaned[:200], top_k=5)
        # GenAI explanations
        doc_expl = explain_document(text, forensic)
        news_expl = explain_news(cleaned, claims, pred, evidence)
        authenticity = float((pred["confidence"] * 0.5) + (forensic.get("fraud_score", 0) / 100 * 0.5))
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "filename": filename,
            "ocr_text": text,
            "forensic": forensic,
            "fake_news": {"prediction": pred, "claims": claims, "evidence": evidence},
            "genai": {"document_explanation": doc_expl, "news_explanation": news_expl},
            "authenticity": authenticity,
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# convenience endpoint to run sample file (user-provided path)
@app.get("/demo/sample")
async def demo_sample():
    if not os.path.exists(SAMPLE_LOCAL_FILE):
        raise HTTPException(status_code=404, detail="Sample file not found.")
    # mimic multipart upload by reading file
    with open(SAMPLE_LOCAL_FILE, "rb") as f:
        data = f.read()
    # call the same pipeline
    text = extract_text_from_upload(data, os.path.basename(SAMPLE_LOCAL_FILE))
    forensic = analyze_document_forensics(data)
    cleaned = clean_text(text)
    claims = extract_claims(cleaned)
    pred = get_classifier().predict([cleaned])[0]
    evidence = get_retriever().query(claims[0] if claims else cleaned[:200], top_k=5)
    doc_expl = explain_document(text, forensic)
    news_expl = explain_news(cleaned, claims, pred, evidence)
    authenticity = float((pred["confidence"] * 0.5) + (forensic.get("fraud_score", 0) / 100 * 0.5))
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "filename": os.path.basename(SAMPLE_LOCAL_FILE),
        "ocr_text": text,
        "forensic": forensic,
        "fake_news": {"prediction": pred, "claims": claims, "evidence": evidence},
        "genai": {"document_explanation": doc_expl, "news_explanation": news_expl},
        "authenticity": authenticity,
    }
