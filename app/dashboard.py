# app/dashboard.py
"""
Stable dashboard with a single sliding chat drawer.
Run from project root:
    streamlit run app/dashboard.py
"""

import os
import sys
from pathlib import Path

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parents[1]
ROOT_STR = str(ROOT)
if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)

# Streamlit config
import streamlit as st
st.set_page_config(page_title="AI Fraud & Document Forensics", layout="wide", initial_sidebar_state="expanded")

# Standard libs
import io
import time
from datetime import datetime
from PIL import Image
import warnings
warnings.filterwarnings("ignore")

# Try importing project modules, provide safe fallbacks
local_forensics = local_ocr = local_news = local_genai = True

# OCR service fallback
try:
    from modules.ocr.ocr_service import extract_text_from_upload
except Exception:
    local_ocr = False

    def extract_text_from_upload(file_bytes, filename=None):
        try:
            import pytesseract
            from PIL import Image
            import io as _io
            header = file_bytes[:4]
            is_pdf = header == b"%PDF"
            if is_pdf:
                return "[PDF OCR not available in fallback. Install pdf2image & pillow]"
            img = Image.open(_io.BytesIO(file_bytes)).convert("RGB")
            return pytesseract.image_to_string(img)
        except Exception as e:
            return f"[OCR fallback not available: {e}]"

# Forensics fallback
try:
    from modules.forensics.forensic_pipeline import analyze_document_forensics
except Exception:
    local_forensics = False

    def analyze_document_forensics(file_bytes):
        return {
            "fraud_score": 0.0,
            "tamper_score": 0.0,
            "tamper_details": "Forensics module not available locally.",
            "tamper_heatmap": None,
            "ela_image": None,
        }

# News fallback
try:
    from modules.news.preprocess import clean_text, extract_claims
    from modules.news.classifier import NewsClassifier
    from modules.news.rag_search import Retriever
except Exception:
    local_news = False

    def clean_text(text):
        return (text or "").strip()

    def extract_claims(text):
        if not text:
            return []
        parts = [p.strip() for p in text.replace("\n", " ").split(".") if p.strip()]
        return parts[:3]

    class NewsClassifier:
        def __init__(self, model_path=None):
            self.model_path = model_path

        def predict(self, texts):
            out = []
            for _ in texts:
                out.append({"label_id": 0, "confidence": 0.6, "probabilities": [0.6, 0.4]})
            return out

    class Retriever:
        def __init__(self, *args, **kwargs):
            pass

        def query(self, q, top_k=3):
            return []

# GenAI fallback
try:
    from modules.genai.llm_engine import run_llm
    from modules.genai.explain_doc import explain_document
    from modules.genai.explain_news import explain_news
except Exception:
    local_genai = False

    def run_llm(prompt):
        return "[LLM not configured]"

    def explain_document(text, forensic):
        return "[GenAI not available]"

    def explain_news(text, claims, classifier_output, evidence):
        return "[GenAI not available]"

# Read query param to toggle chat on/off (floating launcher uses this)
params = st.experimental_get_query_params()
if "chat" in params:
    try:
        val = params.get("chat", ["0"])[0]
        st.session_state.chatbot_open = True if val == "1" else False
    except Exception:
        pass
if "chatbot_open" not in st.session_state:
    st.session_state.chatbot_open = False

# Ensure chat_history exists
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "ai", "content": "Hi — upload a document to analyze or ask a question."}]

# Small CSS for dark polished UI and the drawer
st.markdown(
    """
    <style>
    /* Card & muted */
    .card{background:#0f1720;padding:16px;border-radius:10px;margin-bottom:14px;border:1px solid rgba(255,255,255,0.03)}
    .muted{color:#98a3b3;font-size:13px}

    /* Chat drawer styling */
    .chat-drawer { background:#0b1720; border-left:1px solid rgba(255,255,255,0.02); padding:18px; height:calc(100vh - 120px); overflow:auto; border-radius:12px 0 0 12px; }
    .drawer-bot { background:#14222b; color:#e6eef6; padding:12px; border-radius:12px; margin:8px 0; display:inline-block; max-width:85%; }
    .drawer-user { background:#0A84FF; color:white; padding:12px; border-radius:12px; margin:8px 0; display:inline-block; float:right; clear:both; max-width:85%; }
    .drawer-input { width:100%; padding:12px; border-radius:10px; background:#07121a; color:#e6eef6; border:1px solid rgba(255,255,255,0.03); }

    /* floating launcher */
    .launcher { position: fixed; right: 22px; bottom: 22px; z-index: 9999; }
    .launcher a { text-decoration:none; }
    .launcher .btn { background: linear-gradient(90deg,#0A84FF,#0066FF); color:white; padding:12px 18px; border-radius:999px; font-weight:700; display:flex; align-items:center; gap:10px; box-shadow:0 10px 30px rgba(10,132,255,0.18); }
    </style>
    """,
    unsafe_allow_html=True,
)

# Layout decision
CHAT_OPEN = bool(st.session_state.get("chatbot_open", False))
if CHAT_OPEN:
    left_col, right_col = st.columns([2.6, 1.0])
else:
    left_col = st.container()
    right_col = None

# Left rendering (analyzer) - unchanged features preserved
def render_left(container):
    with container:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Document Analyzer")
        st.markdown('<div class="muted">Upload an image or PDF. Click Analyze Document to run OCR, forensics and quick fake-news checks.</div>', unsafe_allow_html=True)

        uploaded = st.file_uploader("Upload image / PDF", type=["png","jpg","jpeg","bmp","tiff","pdf"])
        use_sample = st.button("Use sample image", key="use_sample_image")
        SAMPLE_PATH = str(ROOT / "data" / "globe-trump-front-page-570.jpg")

        file_bytes = None
        filename = None
        if use_sample:
            if os.path.exists(SAMPLE_PATH):
                with open(SAMPLE_PATH, "rb") as f:
                    file_bytes = f.read()
                filename = os.path.basename(SAMPLE_PATH)
                st.success(f"Loaded sample: {filename}")
            else:
                st.error("Sample image not found at: " + SAMPLE_PATH)

        if uploaded:
            file_bytes = uploaded.read()
            filename = uploaded.name
            st.success(f"File ready: {filename}")

        fast_mode = st.checkbox("FAST MODE (lower DPI, faster OCR)", value=True)

        if st.button("Analyze Document", key="analyze_doc_btn"):
            if not file_bytes:
                st.error("Please upload a file or use sample image.")
            else:
                st.info("Running OCR...")
                t0 = time.time()
                try:
                    ocr_text = extract_text_from_upload(file_bytes, filename)
                except Exception as e:
                    ocr_text = f"[OCR failed: {e}]"

                st.subheader("OCR Output (preview)")
                st.text_area("OCR text", value=(ocr_text or "")[:10000], height=220)

                st.info("Running forensics...")
                try:
                    forensic = analyze_document_forensics(file_bytes)
                except Exception as e:
                    forensic = {"fraud_score": 0.0, "tamper_score": 0.0, "tamper_details": f"Error: {e}", "tamper_heatmap": None, "ela_image": None}

                st.subheader("Forensics")
                st.write("Fraud score:", forensic.get("fraud_score"))
                st.write("Tamper score:", forensic.get("tamper_score"))
                st.write(forensic.get("tamper_details"))
                if forensic.get("tamper_heatmap"):
                    try:
                        st.image(forensic["tamper_heatmap"], caption="Tamper heatmap")
                    except Exception:
                        pass
                if forensic.get("ela_image"):
                    try:
                        st.image(forensic["ela_image"], caption="ELA")
                    except Exception:
                        pass

                st.info("Running fake-news classifier (best-effort)...")
                try:
                    cleaned = clean_text(ocr_text or "")
                    claims = extract_claims(cleaned)
                    st.write("Claims:", claims or "none")
                    clf = NewsClassifier(model_path="distilbert-base-uncased")
                    pred = clf.predict([cleaned])[0]
                    label_map = {0: "REAL / TRUSTWORTHY", 1: "FAKE / MISLEADING"}
                    st.write("Prediction:", label_map.get(pred.get("label_id", 0)))
                    st.write("Confidence:", pred.get("confidence", 0.0))
                    st.json(pred.get("probabilities", []))
                    try:
                        retr = Retriever()
                        evidence = retr.query(claims[0] if claims else cleaned[:200], top_k=3)
                        if evidence:
                            st.write("Evidence found:")
                            for e in evidence:
                                st.write("-", e.get("text","")[:300], f"(score {e.get('score')})")
                        else:
                            st.write("No evidence found in local corpus.")
                    except Exception:
                        st.write("Retriever not available or failed.")
                except Exception as e:
                    st.error("Fake news analysis error: " + str(e))

                st.info("Generating GenAI explanation (best-effort)...")
                try:
                    gen_doc = explain_document(ocr_text or "", forensic)
                except Exception as e:
                    gen_doc = "[GenAI explain_document not available: " + str(e) + "]"
                try:
                    gen_news = explain_news(ocr_text or "", claims if 'claims' in locals() else [], pred if 'pred' in locals() else {}, evidence if 'evidence' in locals() else [])
                except Exception as e:
                    gen_news = "[GenAI explain_news not available: " + str(e) + "]"

                st.subheader("GenAI summaries (if available)")
                st.write("Document explanation:")
                st.write(gen_doc)
                st.write("News explanation:")
                st.write(gen_news)

                st.session_state["last_result"] = {
                    "filename": filename,
                    "timestamp": datetime.utcnow().isoformat(),
                    "ocr_text": ocr_text,
                    "forensic": forensic,
                    "claims": claims if 'claims' in locals() else [],
                    "prediction": pred if 'pred' in locals() else {},
                    "gen_doc": gen_doc,
                    "gen_news": gen_news,
                }
                st.success(f"Analysis completed in {time.time() - t0:.1f}s")
        else:
            st.info("Upload a document or use the sample image and click Analyze Document.")
        st.markdown("</div>", unsafe_allow_html=True)

# Render left
if CHAT_OPEN:
    render_left(left_col)
else:
    render_left(left_col)

# -------------------- RIGHT: Chat drawer (only one chat UI) --------------------
def render_chat_drawer(container):
    with container:
        st.markdown('<div class="chat-drawer">', unsafe_allow_html=True)
        st.subheader("AI Assistant")
        st.markdown('<div style="color:#98a3b3;margin-bottom:6px">Ask about the document, tampering or news. Chat remains active while analysis runs.</div>', unsafe_allow_html=True)

        # Ensure chat_history exists and is list
        if "chat_history" not in st.session_state or not isinstance(st.session_state.chat_history, list):
            st.session_state.chat_history = [{"role": "ai", "content": "Hi — upload a document to analyze or ask a question."}]

        # Messages display (render once)
        for msg in st.session_state.chat_history:
            role = msg.get("role", "ai")
            content = msg.get("content", "")
            if role == "user":
                st.markdown(f'<div class="drawer-user">{content}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="drawer-bot">{content}</div>', unsafe_allow_html=True)

        # Safe input handling (text_input key controls value)
        if "drawer_input" not in st.session_state:
            st.session_state["drawer_input"] = ""

        user_msg = st.text_input(" ", key="drawer_input", placeholder="Ask about the document, tampering or news:")

        send = st.button("Send", key="drawer_send")

        if send and st.session_state["drawer_input"].strip():
            msg = st.session_state["drawer_input"].strip()
            st.session_state.chat_history.append({"role": "user", "content": msg})
            # LLM call (may be local Ollama/OpenAI depending on your modules)
            try:
                reply = run_llm(msg)
            except Exception as e:
                reply = f"[LLM error: {e}]"
            st.session_state.chat_history.append({"role": "ai", "content": reply})
            # clear input safely by removing the session key value
            st.session_state["drawer_input"] = ""
            # rerun to show appended messages
            st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# Render chat drawer only when chat open and right_col present
if CHAT_OPEN and right_col is not None:
    render_chat_drawer(right_col)

# -------------------- Floating toggle launcher (URL param toggles chat) --------------------
launcher_html = f"""
<div class="launcher">
  <a href="?chat={'0' if CHAT_OPEN else '1'}" target="_self">
    <div class="btn">
      <span style="font-size:18px">💬</span>
      <span style="font-size:15px">{'Close Assistant' if CHAT_OPEN else 'Chat with Assistant'}</span>
    </div>
  </a>
</div>
"""
st.markdown(launcher_html, unsafe_allow_html=True)

# Footer / guidance
st.markdown("<hr/>")
st.markdown("<div style='color:#9aa6b2;font-size:12px'>Run Streamlit from the project root (where app/ and modules/ live). Create an empty __init__.py at project root if imports still fail.</div>", unsafe_allow_html=True)
