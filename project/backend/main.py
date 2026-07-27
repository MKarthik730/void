# -*- coding: utf-8 -*-
"""
VOID AI Assistant v3.0 — FastAPI Backend with Full Agentic Core
Hyper-personal AI assistant for Karthik (MKarthik730)
"""

import config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

# ── Existing Services ─────────────────────────────────────────────────────────
from services.memory_service import (
    init_memory_db,
    get_recent_conversations,
    get_action_history,
    log_action,
    add_conversation,
    add_memory,
)
from services.vision_service import (
    analyze as vision_analyze,
    describe_image as vision_describe,
)
from services.ollama_service import run as llm_run
from agent.void_agent import run_agent, run_simple

# ── Routers ───────────────────────────────────────────────────────────────────
from routers.screen_router import router as screen_router
from routers.text_router import router as text_router
from routers.meeting_router import router as meeting_router
from routers.file_router import router as file_router

app = FastAPI(
    title="VOID AI Assistant API",
    description="Hyper-personal AI assistant with LangGraph + 19 integrated capabilities",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ──────────────────────────────────────────────────────────
app.include_router(screen_router)
app.include_router(text_router)
app.include_router(meeting_router)
app.include_router(file_router)

# ── Initialize ────────────────────────────────────────────────────────────────
init_memory_db()


# ═══════════════════════════════════════════════════════════════════════════════
# 📦 REQUEST MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class AgentQuery(BaseModel):
    text: str

class VisionRequest(BaseModel):
    screenshot_b64: str
    action: str = "explain"
    question: str = ""

class ScreenshotSave(BaseModel):
    screenshot_b64: str

class WhatsAppSuggest(BaseModel):
    screenshot_b64: str

class MemoryRememberRequest(BaseModel):
    key: str
    value: str
    category: str = "general"

class MemoryRecallRequest(BaseModel):
    query: str

# ── Weather ──────────────────────────────────────────────────────────────────
class WeatherRequest(BaseModel):
    city: Optional[str] = "Visakhapatnam"

# ── News ─────────────────────────────────────────────────────────────────────
class NewsRequest(BaseModel):
    count: Optional[int] = 5

# ── GitHub ───────────────────────────────────────────────────────────────────
class GitHubRequest(BaseModel):
    repo: Optional[str] = None

# ── LeetCode ─────────────────────────────────────────────────────────────────
class LeetCodeRequest(BaseModel):
    username: Optional[str] = "MKarthik730"

# ── Gmail ────────────────────────────────────────────────────────────────────
class EmailRequest(BaseModel):
    action: str = "inbox"  # inbox, read, draft
    message_id: Optional[str] = None
    reply_text: Optional[str] = None

# ── Calendar ─────────────────────────────────────────────────────────────────
class CalendarRequest(BaseModel):
    action: str = "today"  # today, week, add
    summary: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

# ── Focus ────────────────────────────────────────────────────────────────────
class FocusRequest(BaseModel):
    duration_minutes: Optional[int] = 25
    action: str = "start"  # start, status, end

# ── Reminder ─────────────────────────────────────────────────────────────────
class ReminderRequest(BaseModel):
    text: str
    when: str = "in 30 minutes"

# ── Project Tracker ──────────────────────────────────────────────────────────
class ProjectRequest(BaseModel):
    project: str
    action: str = "status"  # status, update
    field: Optional[str] = None
    value: Optional[str] = None

# ── Career ───────────────────────────────────────────────────────────────────
class CareerRequest(BaseModel):
    action: str = "status"  # status, track, analyze_jd, draft
    company: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = "applied"
    jd_text: Optional[str] = None

# ── Hackathon ────────────────────────────────────────────────────────────────
class HackathonRequest(BaseModel):
    action: str = "start"  # start, status, end
    hours_remaining: Optional[float] = 24.0
    name: Optional[str] = ""

# ── Git ──────────────────────────────────────────────────────────────────────
class GitRequest(BaseModel):
    action: str = "security_check"  # security_check, commit_message

# ── Paper ────────────────────────────────────────────────────────────────────
class PaperRequest(BaseModel):
    url: str
    action: str = "arxiv"  # arxiv, article

# ── Clipboard ────────────────────────────────────────────────────────────────
class ClipboardRequest(BaseModel):
    text: str

# ── Voice ────────────────────────────────────────────────────────────────────
class VoiceRequest(BaseModel):
    action: str = "transcribe"  # transcribe, speak
    audio_path: Optional[str] = None
    text: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 STARTUP
# ═══════════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    print("=" * 60)
    print("  VOID v3.0 — Hyper-Personal AI Assistant")
    print("  Agent: LangGraph + Ollama Qwen3")
    print("  Memory: PostgreSQL + pgvector RAG")
    print("  Vision: Ollama llava/moondream")
    print("  Capabilities: 19 integrated services")
    print("  File Workspace: " + config.FILE_WORKSPACE_ROOTS.split(";")[0])
    print("=" * 60)
    print("Starting services...")

    # Start background scheduler
    try:
        from scheduler import start_scheduler
        start_scheduler()
    except Exception as e:
        print(f"[WARN] Scheduler not started: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# 🏠 CORE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {
        "name": "VOID AI Assistant",
        "version": "3.0.0",
        "docs": "/docs",
        "status": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "VOID is alive",
        "version": "3.0.0",
        "agent": "LangGraph + Ollama Qwen3",
        "vision": "Ollama llava/moondream",
        "memory": "PostgreSQL + pgvector RAG",
        "services": {
            "weather": bool(config.OPENWEATHER_API_KEY),
            "gmail": bool(os.path.exists(config.GOOGLE_TOKEN_PATH) or os.path.exists(config.GOOGLE_CLIENT_SECRET_PATH)),
            "github": True,
            "leetcode": True,
            "news": True,
            "file_workspace": bool(config.FILE_WORKSPACE_ROOTS),
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 🤖 AGENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/agent/query")
def agent_query(request: AgentQuery):
    """Main agent endpoint — full intent detection + service routing."""
    try:
        response = run_agent(request.text)
        log_action("agent_query", request.text, response, success=True)
        return {"response": response}
    except Exception as e:
        log_action("agent_query_error", request.text, str(e), success=False)
        return {"error": str(e), "response": "Agent failed to respond bro — try again?"}


@app.post("/agent/simple")
def simple_query(request: AgentQuery):
    """Direct LLM query without agent planning."""
    try:
        response = llm_run(request.text, max_tokens=300)
        add_conversation(request.text, response)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# 🌤️ WEATHER
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/weather")
def get_weather(city: str = "Visakhapatnam"):
    """Get current weather for a city."""
    from services.weather_service import get_weather
    result = get_weather(city)
    if result:
        return {"weather": result}
    return {"weather": "Weather fetch avvaledhu bro"}, 503


# ═══════════════════════════════════════════════════════════════════════════════
# 🌐 TECH NEWS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/news")
def get_news(count: int = 5):
    """Get latest tech news."""
    from services.news_service import get_tech_news_formatted
    result = get_tech_news_formatted(count)
    return {"news": result}


# ═══════════════════════════════════════════════════════════════════════════════
# 🐙 GITHUB
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/github")
def get_github():
    """Get GitHub activity overview."""
    from services.github_service import get_github_overview
    result = get_github_overview()
    return {"github": result}


@app.get("/github/repo/{repo_name}")
def get_repo(repo_name: str):
    """Get status of a specific repo."""
    from services.github_service import get_repo_status
    result = get_repo_status(repo_name)
    if result:
        return {"repo": result}
    return {"repo": "Repo dorakaledhu"}, 404


# ═══════════════════════════════════════════════════════════════════════════════
# 💪 LEETCODE
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/leetcode")
def get_leetcode(username: str = "MKarthik730"):
    """Get LeetCode stats."""
    from services.leetcode_service import get_stats_formatted
    result = get_stats_formatted()
    return {"leetcode": result}


# ═══════════════════════════════════════════════════════════════════════════════
# 📧 EMAIL
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/email/inbox")
def email_inbox(limit: int = 10):
    """Check Gmail inbox."""
    from services.gmail_service import check_inbox
    result = check_inbox(limit)
    return {"emails": result}


@app.post("/email/read")
def email_read(request: EmailRequest):
    """Read a specific email."""
    from services.gmail_service import read_email
    if not request.message_id:
        return {"error": "message_id required"}, 400
    result = read_email(request.message_id)
    return {"email": result}


@app.post("/email/reply")
def email_reply(request: EmailRequest):
    """Draft and send a reply to an email."""
    from services.gmail_service import draft_reply
    if not request.message_id or not request.reply_text:
        return {"error": "message_id and reply_text required"}, 400
    result = draft_reply(request.message_id, request.reply_text)
    return {"result": result}


# ═══════════════════════════════════════════════════════════════════════════════
# 📅 CALENDAR
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/calendar/today")
def calendar_today():
    """Get today's schedule."""
    from services.calendar_service import get_today_schedule
    result = get_today_schedule()
    return {"schedule": result}


@app.get("/calendar/week")
def calendar_week():
    """Get week overview."""
    from services.calendar_service import get_week_overview
    result = get_week_overview()
    return {"schedule": result}


@app.post("/calendar/add")
def calendar_add(request: CalendarRequest):
    """Add an event to calendar."""
    from services.calendar_service import add_event
    if not request.summary or not request.start_time or not request.end_time:
        return {"error": "summary, start_time, end_time required"}, 400
    result = add_event(request.summary, request.start_time, request.end_time)
    return {"result": result}


# ═══════════════════════════════════════════════════════════════════════════════
# ⏰ FOCUS MODE
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/focus/start")
def focus_start(request: FocusRequest):
    """Start a focus session."""
    from services.focus_service import start_focus
    result = start_focus(request.duration_minutes)
    return {"focus": result}


@app.get("/focus/status")
def focus_status():
    """Get focus session status."""
    from services.focus_service import get_focus_status
    result = get_focus_status()
    return {"focus": result}


@app.post("/focus/end")
def focus_end():
    """End focus session."""
    from services.focus_service import end_focus
    result = end_focus()
    return {"focus": result}


# ═══════════════════════════════════════════════════════════════════════════════
# ⏰ REMINDERS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/reminder/set")
def reminder_set(request: ReminderRequest):
    """Set a reminder."""
    from services.reminder_service import set_reminder
    result = set_reminder(request.text, request.when)
    return {"reminder": result}


@app.get("/reminder/list")
def reminder_list():
    """List all reminders."""
    from services.reminder_service import list_reminders
    result = list_reminders()
    return {"reminders": result}


# ═══════════════════════════════════════════════════════════════════════════════
# 📊 PROJECT TRACKER
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/project/{project_name}")
def project_status(project_name: str):
    """Get project status."""
    from services.project_tracker import get_project_status
    result = get_project_status(project_name)
    return {"project": result}


@app.post("/project/update")
def project_update(request: ProjectRequest):
    """Update project status."""
    from services.project_tracker import update_project_status
    if not request.field or not request.value:
        return {"error": "field and value required"}, 400
    result = update_project_status(request.project, request.field, request.value)
    return {"result": result}


@app.get("/projects")
def all_projects():
    """Get all projects summary."""
    from services.project_tracker import get_all_projects_summary
    result = get_all_projects_summary()
    return {"projects": result}


# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 CAREER
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/career/applications")
def career_applications():
    """Get all tracked applications."""
    from services.career_service import get_application_status
    result = get_application_status()
    return {"career": result}


@app.post("/career/track")
def career_track(request: CareerRequest):
    """Track a new application."""
    from services.career_service import track_application
    if not request.company or not request.role:
        return {"error": "company and role required"}, 400
    result = track_application(request.company, request.role, request.status or "applied")
    return {"result": result}


@app.post("/career/analyze-jd")
def career_analyze_jd(request: CareerRequest):
    """Analyze a job description."""
    from services.career_service import analyze_jd
    if not request.jd_text:
        return {"error": "jd_text required"}, 400
    result = analyze_jd(request.jd_text)
    return {"analysis": result}


@app.get("/career/platforms")
def career_platforms():
    """Suggest application platforms."""
    from services.career_service import suggest_platforms
    result = suggest_platforms()
    return {"platforms": result}


# ═══════════════════════════════════════════════════════════════════════════════
# 🚨 HACKATHON
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/hackathon/start")
def hackathon_start(request: HackathonRequest):
    """Activate hackathon mode."""
    from services.hackathon_service import activate_hackathon_mode
    result = activate_hackathon_mode(request.hours_remaining, request.name or "")
    return {"hackathon": result}


@app.get("/hackathon/status")
def hackathon_status():
    """Get hackathon status."""
    from services.hackathon_service import get_hackathon_status
    result = get_hackathon_status()
    return {"hackathon": result}


@app.post("/hackathon/end")
def hackathon_end():
    """End hackathon mode."""
    from services.hackathon_service import end_hackathon
    result = end_hackathon()
    return {"hackathon": result}


# ═══════════════════════════════════════════════════════════════════════════════
# 🤖 GIT / SECURITY
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/git/security-check")
def git_security_check():
    """Check git diff for security issues."""
    from services.git_service import check_before_push
    result = check_before_push()
    return {"security": result}


@app.get("/git/commit-message")
def git_commit_message():
    """Generate commit message from diff."""
    from services.git_service import generate_commit_message
    result = generate_commit_message()
    return {"commit_message": result}


# ═══════════════════════════════════════════════════════════════════════════════
# 📄 PAPER SUMMARIZER
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/paper/summarize")
def paper_summarize(request: PaperRequest):
    """Summarize an arXiv paper or article from URL."""
    from services.pdf_service import summarize_arxiv, summarize_article
    if request.action == "arxiv":
        result = summarize_arxiv(request.url)
    else:
        result = summarize_article(request.url)
    return {"summary": result}


# ═══════════════════════════════════════════════════════════════════════════════
# 📋 CLIPBOARD
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/clipboard/analyze")
def clipboard_analyze(request: ClipboardRequest):
    """Analyze clipboard content."""
    from services.clipboard_service import process_clipboard
    result = process_clipboard(request.text)
    return {"analysis": result}


# ═══════════════════════════════════════════════════════════════════════════════
# 🎤 VOICE
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/voice/transcribe")
def voice_transcribe(request: VoiceRequest):
    """Transcribe audio file using faster-whisper."""
    from services.voice_service import transcribe
    if not request.audio_path:
        return {"error": "audio_path required"}, 400
    result = transcribe(request.audio_path)
    return {"transcription": result}


@app.post("/voice/speak")
def voice_speak(request: VoiceRequest):
    """Speak text using pyttsx3 TTS."""
    from services.voice_service import speak
    if not request.text:
        return {"error": "text required"}, 400
    success = speak(request.text)
    return {"spoken": success}


# ═══════════════════════════════════════════════════════════════════════════════
# 🌅 DAILY BRIEF
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/brief/morning")
def morning_brief():
    """Generate morning brief."""
    from scheduler import generate_morning_brief
    result = generate_morning_brief()
    return {"brief": result}


@app.get("/brief/digest")
def daily_digest():
    """Generate evening daily digest."""
    from scheduler import generate_daily_digest
    result = generate_daily_digest()
    return {"digest": result}


# ═══════════════════════════════════════════════════════════════════════════════
# 👁️ VISION & 🧠 MEMORY — These are served by screen_router.py, text_router.py,
# and meeting_router.py which are registered above. No duplicate endpoints here.
# ═══════════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
