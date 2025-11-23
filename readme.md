
AI Documents & News Analyzer
Advanced OCR, Image Forensics, Fake News Detection & AI Assistant

A complete AI-powered system for banks, HR teams, legal offices, and verification departments to evaluate document authenticity, extract OCR text, perform tampering forensics, detect fake news, retrieve evidence, and interact with a GenAI assistant using local models (Ollama Llama3).

The project contains:

Streamlit Dashboard (Frontend UI)

FastAPI backend

PaddleOCR + fallback OCR

ELA tampering detection + heatmaps

DistilBERT fake news classifier

RAG search over text corpus

Llama3 local LLM assistant

Modern slide-out chat UI

⭐ Features
✔ Document OCR

Extract text from: PNG, JPG, BMP, TIFF, PDF (multimode support)

✔ Image Forensic Analysis

Error Level Analysis (ELA)

Tamper probability score

Heatmap overlay

Fraud scoring system

✔ Fake News Classification

Claim extraction

DistilBERT prediction

Confidence scoring

Evidence retrieval using RAG search

✔ GenAI Virtual Assistant

Uses Ollama Llama3 (fully offline)

Works during analysis (non-blocking)

Slide-out floating UI

Professional dark theme

✔ Sleek Modern Interface

Clean cards

Professional dark theme

Toggle chatbot

Fast, responsive layout

📁 Project Structure
ai-documents-news-analyzer/
│
├── app/
│   └── dashboard.py
│
├── api/
│   └── server.py
│
├── modules/
│   ├── ocr/
│   │   ├── ocr_service.py
│   │   └── layout.py
│   ├── forensics/
│   │   └── forensic_pipeline.py
│   ├── news/
│   │   ├── preprocess.py
│   │   ├── classifier.py
│   │   └── rag_search.py
│   ├── genai/
│   │   ├── llm_engine.py
│   │   ├── explain_doc.py
│   │   └── explain_news.py
│
├── data/
│   └── sample.jpg
│
├── run.py
├── requirements.txt
└── README.md

🔧 Installation
1. Create Virtual Environment
python -m venv venv
venv\Scripts\activate

2. Install Requirements
pip install -r requirements.txt

🤖 Ollama Setup (REQUIRED)

Install Ollama:
https://ollama.com

Pull the model:

ollama pull llama3


Verify it's running:

ollama run llama3

🚀 Running the Application
Start FastAPI Backend
uvicorn run:app --host 127.0.0.1 --port 8000 --reload


API Docs:

http://127.0.0.1:8000/docs

Start Streamlit Frontend
streamlit run app/dashboard.py

🔗 API Endpoints
Endpoint	Method	Description
/ocr	POST	Extracts OCR text
/forensics	POST	ELA tampering & fraud scoring
/chat	POST	LLM-powered chat via Llama3
/news	POST	Fake news detection
📦 Technology Stack

Python 3.10+

Streamlit (Dashboard UI)

FastAPI (Backend API)

PaddleOCR + PPOCRv4

DistilBERT (Claim classification)

FAISS / Local DB (RAG)

Ollama Llama3 (GenAI assistant)

OpenCV, Pillow, NumPy

🧩 Use Cases

Banking KYC verification

HR background checks

Legal document validation

Fraud detection departments

Media authenticity analysis

📜 License

MIT License

💬 Support

If you need help with deployment, debugging, or feature expansion, open an issue in the repository.