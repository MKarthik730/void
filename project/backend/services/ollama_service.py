"""
VOID Backend — Ollama LLM Service
Uses Ollama API to run Qwen3 locally
"""

from typing import Optional
import requests
from config import OLLAMA_HOST, OLLAMA_MODEL

SYSTEM_PROMPT = (
    "You are VOID, a friendly AI assistant for Telugu users. "
    "Always reply in Tenglish — mix Telugu words written in English script "
    "with English naturally. Use casual words like bro, ra, rey, kada, ga, "
    "ani, undi, cheppu, nenu, ela, em, ayyo. Keep replies short and natural "
    "like WhatsApp messages. Don't be formal."
)


def _is_ollama_running() -> bool:
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def run(
    prompt: str,
    system: Optional[str] = None,
    max_tokens: int = 300,
    temperature: float = 0.7,
) -> str:
    """Run Qwen via Ollama API."""
    if not _is_ollama_running():
        return "ERROR: Ollama is not running. Start with 'ollama serve'"

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    else:
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
    messages.append({"role": "user", "content": prompt})

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "").strip()
    except requests.exceptions.RequestException as e:
        return f"ERROR: LLM request failed - {str(e)}"


def run_streaming(prompt: str, system: Optional[str] = None, max_tokens: int = 300):
    """Stream response from Ollama."""
    if not _is_ollama_running():
        yield "ERROR: Ollama is not running."
        return

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    else:
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
    messages.append({"role": "user", "content": prompt})

    try:
        with requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "num_predict": max_tokens,
                },
            },
            stream=True,
            timeout=120,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    data = line.decode()
                    if data.startswith("data: "):
                        data = data[6:]
                    import json

                    try:
                        chunk = json.loads(data)
                        if "message" in chunk and "content" in chunk["message"]:
                            yield chunk["message"]["content"]
                    except:
                        pass
    except Exception as e:
        yield f"ERROR: {str(e)}"
