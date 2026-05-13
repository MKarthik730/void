"""
VOID Backend — Central Configuration
Loads all settings from .env file
"""

import os
from dotenv import load_dotenv

load_dotenv()

HF_HOME = os.getenv("HF_HOME", "D:\\huggingface")
HF_HUB_CACHE = os.getenv("HUGGINGFACE_HUB_CACHE", "D:\\huggingface\\hub")
os.environ["HF_HOME"] = HF_HOME
os.environ["HUGGINGFACE_HUB_CACHE"] = HF_HUB_CACHE

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")
VISION_MODEL = os.getenv("VISION_MODEL", "llava")

QWEN_GGUF_PATH = os.getenv(
    "QWEN_GGUF_PATH", "D:\\models\\qwen2.5-3b-instruct-q4_k_m.gguf"
)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

SCREENSHOTS_ROOT = os.path.join(os.path.expanduser("~"), "Pictures", "VOID")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'void_memory.db')}",
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'void_memory.db')}",
)
