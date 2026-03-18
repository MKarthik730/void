"""
VOID AI Assistant — FastAPI Backend
Entry point: registers all routers and sets up DB
"""
# config.py MUST be imported first — sets HF env vars before torch loads
import config  # noqa: F401

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from database import engine, Base
from routers import text_router, screen_router, meeting_router

DB_INIT_ERROR = None

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="VOID AI Assistant API",
    description="Backend for VOID — Telugu AI Screen Assistant",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ──────────────────────────────────────────────────────────
app.include_router(text_router.router)
app.include_router(screen_router.router)
app.include_router(meeting_router.router)


@app.on_event("startup")
def initialize_database():
    global DB_INIT_ERROR

    try:
        Base.metadata.create_all(bind=engine)
        DB_INIT_ERROR = None
    except SQLAlchemyError as exc:
        DB_INIT_ERROR = str(exc)
        print(f"WARNING: Database initialization skipped: {exc}")


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health():
    return {
        "status":   "VOID is alive ✅",
        "model":    "Qwen2.5-3B (GGUF)",
        "vision":   "Gemini 1.5 Flash",
        "version":  "1.0.0",
        "database": "ready" if DB_INIT_ERROR is None else "unavailable",
        "database_error": DB_INIT_ERROR,
    }


# ── Run ───────────────────────────────────────────────────────────────────────
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload
