# modules/genai/explain_news.py

import os
from modules.genai.llm_engine import run_llm

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "news_prompt.txt")

def load_prompt():
    try:
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "You are a fact-checking assistant. Evaluate the news text."

def explain_news(text: str, claims, classifier_output, evidence):
    base_prompt = load_prompt()
    full_prompt = (
        base_prompt
        + "\n\nNEWS TEXT:\n"
        + text
        + "\n\nCLAIMS:\n"
        + str(claims)
        + "\n\nML OUTPUT:\n"
        + str(classifier_output)
        + "\n\nEVIDENCE:\n"
        + str(evidence)
    )
    return run_llm(full_prompt)
