# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

load_dotenv()

# ── Ollama ────────────────────────────────────────────────────────────────────
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
VISION_MODEL = os.getenv("VISION_MODEL", "llava")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/void",
)

# ── Screenshots ───────────────────────────────────────────────────────────────
SCREENSHOTS_ROOT = os.path.join(os.path.expanduser("~"), "Pictures", "VOID")

# ── Weather ───────────────────────────────────────────────────────────────────
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Visakhapatnam")

# ── Google OAuth ──────────────────────────────────────────────────────────────
GOOGLE_CLIENT_SECRET_PATH = os.getenv(
    "GOOGLE_CLIENT_SECRET_PATH",
    os.path.join(os.path.dirname(__file__), "..", "..", "credentials.json"),
)
GOOGLE_TOKEN_PATH = os.getenv(
    "GOOGLE_TOKEN_PATH",
    os.path.join(os.path.dirname(__file__), "..", "..", "token.json"),
)

# ── GitHub ────────────────────────────────────────────────────────────────────
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "MKarthik730")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# ── News ──────────────────────────────────────────────────────────────────────
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

# ── Voice ─────────────────────────────────────────────────────────────────────
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
TTS_VOICE = os.getenv("TTS_VOICE", "male")

# ── LeetCode ──────────────────────────────────────────────────────────────────
LEETCODE_USERNAME = os.getenv("LEETCODE_USERNAME", "MKarthik730")

# ── User Info ─────────────────────────────────────────────────────────────────
USER_NAME = os.getenv("USER_NAME", "Karthik")
USER_GITHUB = os.getenv("USER_GITHUB", "MKarthik730")
USER_GITHUB_SECONDARY = os.getenv("USER_GITHUB_SECONDARY", "kakashi754-ui")
USER_COLLEGE = os.getenv("USER_COLLEGE", "ANITS Visakhapatnam")
USER_BRANCH = os.getenv("USER_BRANCH", "CSE")
USER_YEAR = os.getenv("USER_YEAR", "2nd Year, 5th Semester")
USER_GRADUATION = os.getenv("USER_GRADUATION", "2028")
USER_CGPA = os.getenv("USER_CGPA", "9.0+")
USER_TIMEZONE = os.getenv("USER_TIMEZONE", "Asia/Kolkata")
USER_IST_OFFSET = os.getenv("USER_IST_OFFSET", "UTC+5:30")

# ── File Workspace ────────────────────────────────────────────────────────────
FILE_WORKSPACE_ROOTS = os.getenv(
    "FILE_WORKSPACE_ROOTS",
    os.path.join(os.path.expanduser("~"), "VOID_Projects"),
)
