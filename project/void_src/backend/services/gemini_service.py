"""
VOID Backend — Gemini Vision Service
Handles all image/screenshot understanding tasks
"""
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import base64
from config import GEMINI_API_KEY

# ── Configure Gemini ──────────────────────────────────────────────────────────
genai.configure(api_key=GEMINI_API_KEY)
_vision = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = "You are VOID, an intelligent AI screen assistant. Be concise, clear, and helpful."

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
        "If there is code, explain what it does. "
        "If there is an image or photo, describe it thoroughly."
    ),
    "translate": (
        "Extract ALL text visible in this screenshot and translate it to English. "
        "Preserve the structure and context of the original text."
    ),
}


def decode_image(b64_string: str) -> Image.Image:
    """Decode base64 string to PIL Image"""
    img_bytes = base64.b64decode(b64_string)
    return Image.open(BytesIO(img_bytes))


def analyze(screenshot_b64: str, action: str) -> str:
    """
    Send screenshot to Gemini Vision and get analysis based on action type.
    action: suggest | summarize | explain | translate
    """
    img = decode_image(screenshot_b64)
    prompt_text = ACTION_PROMPTS.get(action, ACTION_PROMPTS["explain"])
    full_prompt  = f"{SYSTEM_PROMPT}\n\n{prompt_text}"

    response = _vision.generate_content([full_prompt, img])
    return response.text


def describe_image(screenshot_b64: str, user_question: str = "") -> str:
    """
    General purpose image description with optional user question.
    Used for the PDF/document explain feature with follow-up questions.
    """
    img = decode_image(screenshot_b64)
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        "Look at this screen carefully and provide a thorough explanation. "
        "Describe text content, visual elements, charts, code, or anything visible. "
        f"{'User question: ' + user_question if user_question else ''}"
    )
    response = _vision.generate_content([prompt, img])
    return response.text
