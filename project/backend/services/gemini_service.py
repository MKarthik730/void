"""
VOID Backend — Groq Vision Service
Uses Groq API (free) for image/screenshot understanding
"""
import base64
from groq import Groq
from config import GROQ_API_KEY

_client = Groq(api_key=GROQ_API_KEY)
MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

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
        "If there is code, explain what it does."
    ),
    "translate": (
        "Extract ALL text visible in this screenshot and translate it to English. "
        "Preserve the structure and context of the original text."
    ),
}


def analyze(screenshot_b64: str, action: str) -> str:
    """Send screenshot to Groq Vision and get analysis based on action type."""
    prompt_text = ACTION_PROMPTS.get(action, ACTION_PROMPTS["explain"])
    full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt_text}"

    response = _client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{screenshot_b64}"
                        },
                    },
                    {"type": "text", "text": full_prompt},
                ],
            }
        ],
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()


def describe_image(screenshot_b64: str, user_question: str = "") -> str:
    """General purpose image description with optional user question."""
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        "Look at this screen carefully and provide a thorough explanation. "
        "Describe text content, visual elements, charts, code, or anything visible. "
        f"{'User question: ' + user_question if user_question else ''}"
    )

    response = _client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{screenshot_b64}"
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()