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
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
VISION_MODEL = os.getenv("VISION_MODEL", "llava")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

SCREENSHOTS_ROOT = os.path.join(os.path.expanduser("~"), "Pictures", "VOID")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'void_memory.db')}",
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'void_memory.db')}",
)
