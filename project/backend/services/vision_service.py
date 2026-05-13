"""
VOID Backend — Local Vision Service via Ollama
Uses llava or moondream for screen understanding - fully offline
"""

import base64
import requests
from config import OLLAMA_HOST, VISION_MODEL

ACTION_PROMPTS = {
    "suggest": (
        "Look at this chat screenshot. Understand the conversation context "
        "and suggest the single best next reply message. Be natural and friendly."
    ),
    "summarize": (
        "Summarize the key information shown in this screenshot in 3-5 bullet points. "
        "Be concise and capture only the most important information."
    ),
    "explain": (
        "Explain everything you see in this screenshot in simple, clear language. "
        "If there is text, explain what it means. "
        "If there is a chart or diagram, describe the data and insights. "
        "If there is code, explain what it does."
    ),
    "translate": (
        "Extract ALL text visible in this screenshot and translate it to English. "
        "Preserve the structure and context of the original text."
    ),
}


def _is_ollama_running() -> bool:
    """Check if Ollama server is running."""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def analyze(screenshot_b64: str, action: str) -> str:
    """Send screenshot to Ollama Vision model and get analysis."""
    if not _is_ollama_running():
        return "ERROR: Ollama is not running. Start with 'ollama serve'"

    prompt_text = ACTION_PROMPTS.get(action, ACTION_PROMPTS["explain"])

    payload = {
        "model": VISION_MODEL,
        "prompt": prompt_text,
        "images": [screenshot_b64],
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 500},
    }

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate", json=payload, timeout=60
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.RequestException as e:
        return f"ERROR: Vision analysis failed - {str(e)}"


def describe_image(screenshot_b64: str, user_question: str = "") -> str:
    """General purpose image description with optional user question."""
    if not _is_ollama_running():
        return "ERROR: Ollama is not running. Start with 'ollama serve'"

    prompt = (
        "Look at this screen carefully and provide a thorough explanation. "
        "Describe text content, visual elements, charts, code, or anything visible."
    )
    if user_question:
        prompt += f"\n\nUser question: {user_question}"

    payload = {
        "model": VISION_MODEL,
        "prompt": prompt,
        "images": [screenshot_b64],
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 500},
    }

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate", json=payload, timeout=60
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.RequestException as e:
        return f"ERROR: Image description failed - {str(e)}"
