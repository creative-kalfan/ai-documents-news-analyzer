# modules/genai/llm_engine.py

import requests
import json

print("DEBUG: LLM Engine Loaded -> USING OLLAMA (IPv4 + STREAMING FIX)")

# Always use local Ollama
USE_OLLAMA = True
OLLAMA_MODEL = "llama3"      # Make sure you ran: ollama pull llama3


def call_ollama(prompt, model=OLLAMA_MODEL):
    """
    Correct streaming implementation for Ollama API.
    Forces IPv4 (127.0.0.1) and handles streaming token-by-token JSON safely.
    """

    try:
        # Stream response from local Ollama server (IPv4)
        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": True},
            timeout=60,
            stream=True,
        )

        full_output = ""

        # Iterate over streamed chunks
        for line in response.iter_lines():
            if not line:
                continue
            try:
                data = json.loads(line.decode("utf-8"))
                chunk = data.get("response", "")
                full_output += chunk
            except json.JSONDecodeError:
                # Ignore incomplete JSON chunks to prevent crashes
                continue

        return full_output.strip()

    except requests.exceptions.ConnectionError:
        return (
            "[Ollama Error] Cannot connect to Ollama at 127.0.0.1:11434.\n"
            "Make sure the Ollama server is running.\n"
            "Try: `ollama serve` or restart Ollama Desktop."
        )

    except Exception as e:
        return f"[Ollama Error] {e}"


def run_llm(prompt):
    """
    Unified LLM function — ALWAYS uses Ollama now.
    """
    return call_ollama(prompt)
