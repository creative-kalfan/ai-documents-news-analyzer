import re
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

URL_RE = re.compile(r'https?://\S+|www\.\S+')
HTML_RE = re.compile(r'<.*?>')
MULTI_WS = re.compile(r'\s+')


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    text = URL_RE.sub('', text)
    text = HTML_RE.sub('', text)
    text = text.replace("\xa0", " ")
    text = MULTI_WS.sub(" ", text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text.strip()


def extract_claims(text: str, max_sentences: int = 5):
    text = clean_text(text)
    if not text:
        return []

    if nlp:
        doc = nlp(text)
        candidates = []
        for sent in doc.sents:
            s = sent.text.strip()
            if len(s) < 15:
                continue
            if len(sent.ents) >= 1:
                candidates.append(s)
        return candidates[:max_sentences] if candidates else [s.text for s in doc.sents][:max_sentences]

    # Fallback simple split
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return sentences[:max_sentences]
