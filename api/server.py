from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from modules.ocr.ocr_service import extract_text_from_upload
from modules.forensics.forensic_pipeline import analyze_document_forensics
from modules.genai.llm_engine import run_llm

app = FastAPI(title="Document & News AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    content = await file.read()
    text = extract_text_from_upload(content, file.filename)
    return {"text": text}

@app.post("/forensics")
async def forensics_endpoint(file: UploadFile = File(...)):
    content = await file.read()
    forensic = analyze_document_forensics(content)
    return forensic

@app.post("/chat")
async def chat_endpoint(payload: dict):
    prompt = payload.get("prompt", "")
    reply = run_llm(prompt)
    return {"reply": reply}
