"""
VOID Backend — Central Configuration
Loads all settings from .env file
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── HuggingFace cache ─────────────────────────────────────────────────────────
HF_HOME      = os.getenv("HF_HOME", "D:\\huggingface")
HF_HUB_CACHE = os.getenv("HUGGINGFACE_HUB_CACHE", "D:\\huggingface\\hub")
os.environ["HF_HOME"]               = HF_HOME
os.environ["HUGGINGFACE_HUB_CACHE"] = HF_HUB_CACHE

# ── Qwen GGUF Model (primary) ─────────────────────────────────────────────────
QWEN_GGUF_PATH = os.getenv("QWEN_GGUF_PATH", "D:\\models\\qwen2.5-3b-instruct-q4_k_m.gguf")

# ── Legacy Mistral (keep for reference) ──────────────────────────────────────
BASE_MODEL     = os.getenv("BASE_MODEL",   "mistralai/Mistral-7B-v0.1")
ADAPTER_PATH   = os.getenv("ADAPTER_PATH", "../LLM")
MISTRAL_GGUF_PATH = os.getenv("MISTRAL_GGUF_PATH", "D:\\telugu_mistral_q4.gguf")

# ── Gemini Vision API ─────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("AIzaSyDqgghup3inYWNe7sDVl7u-cIUluKnwatg", "")

# ── PostgreSQL ────────────────────────────────────────────────────────────────
POSTGRES_USER     = os.getenv("POSTGRES_USER",     "void_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "void_password")
POSTGRES_HOST     = os.getenv("POSTGRES_HOST",     "localhost")
POSTGRES_PORT     = os.getenv("POSTGRES_PORT",     "5432")
POSTGRES_DB       = os.getenv("POSTGRES_DB",       "void_db")

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# ── Screenshot storage ────────────────────────────────────────────────────────
SCREENSHOTS_ROOT = os.path.join(os.path.expanduser("~"), "Pictures", "VOID")
