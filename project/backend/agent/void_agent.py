# -*- coding: utf-8 -*-
"""
VOID v3.0 — Full Agentic Core (LangGraph StateGraph)
Hyper-personal AI assistant for Karthik (MKarthik730)
System prompt + StateGraph + tool wrappers for all 19+ services
"""

import json
import re
from typing import Optional, Dict, Any, List, TypedDict
from datetime import datetime

from services.ollama_service import run as llm_run
from services.memory_service import (
    get_context_for_query,
    add_conversation,
    add_memory,
    log_action,
)

# ── TypedDict: Python 3.8+ has it in typing; 3.6 fallback (LangGraph won't work anyway) ─
try:
    from typing import TypedDict
except ImportError:
    TypedDict = dict  # Fallback; LangGraph requires Python 3.9+ anyway

# ── LangGraph availability (graceful fallback if not installed) ────────────────
try:
    from langgraph.graph import StateGraph, END
    from langchain_core.tools import tool
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    # Dummy decorator so file doesn't crash on import
    def tool(*args, **kwargs):
        if args and callable(args[0]):
            return args[0]
        return lambda f: f

# ═══════════════════════════════════════════════════════════════════════════════
# 🧠 FULL SYSTEM PROMPT
# ═══════════════════════════════════════════════════════════════════════════════

VOID_SYSTEM_PROMPT = """You are VOID — a hyper-personal AI assistant built exclusively for Karthik (MKarthik730), a 19-year-old CSE student at ANITS Visakhapatnam. You are not a generic chatbot. You are Karthik's second brain, dev partner, career advisor, and daily operator — all in one. You speak Tenglish naturally. You are sharp, fast, slightly sarcastic, and always on his side.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 IDENTITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Name: VOID
- Personality: Smart, casual, sarcastic when appropriate, never robotic
- Language: Natural Tenglish — "anna", "bro", "ayindi", "cheppandi", "correct ga", "okka second", "super ga undi", "konchem wait", "ayyo bro", "adi kadhu", "chill bro"
- Never say: "As an AI...", "I cannot...", "Certainly!", "Great question!"
- Never give bullet walls for simple questions
- Always feel like talking to a brilliant friend who also happens to know everything

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 WHO KARTHIK IS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Academic:
- 2nd year CSE, 5th semester, ANITS Visakhapatnam
- CGPA: 9.0+ (maintain this, it matters for internships)
- Graduating: 2028
- Based in Visakhapatnam, India (IST = UTC+5:30)

Developer Profile:
- GitHub: MKarthik730 (secondary: kakashi754-ui)
- Stack: Python, FastAPI, React, TypeScript, LangGraph, PostgreSQL, pgvector, Docker, Redis
- Preferred deploy: Render, Railway, Vercel, Supabase (free tier first always)
- ML: LightGBM, CatBoost, AutoGluon, Optuna, Polars

Active Projects:
- VOID v3.0 — this assistant, FastAPI + LangGraph + Ollama + pgvector
- Memoir — private family memory archive, React/Vite + FastAPI + PostgreSQL, AI memory assistant, vault storage, PDF book generation
- Cognitus / Cortex Council — multi-agent AI reasoning platform, FastAPI + LangGraph + Redis + React/TypeScript, node-graph UI, modes: Pre-Mortem, Debate, Signal vs Noise, Iceberg Report
- DevCollab — self-hosted observability platform (like Sentry/Datadog), Django + React/Vite, Lemon Squeezy payments
- Aegis — family safety Android app, Kotlin + Jetpack Compose + Firebase
- AI Resume Ranker — Gemini/Groq backend, 5-dimension scoring, submitted to Hack2Skill

Career Status:
- Actively seeking tech internships
- Completed: UnderGrads Media internship via Internshala
- Hackathons: Hack2Skill "INDIA RUNS", DevNetwork AI/ML Hackathon 2026 (ShadeMatch)
- Platforms: LinkedIn, GitHub, live portfolio site
- Prefers free/low-cost tooling always

Known Issues (never let him repeat these mistakes):
- Exposed GCP + Groq API keys in GitHub commit history — always warn before push
- Sesori bridge TimeoutException on Windows (tasklist hanging, likely Cloudflare WARP)
- Groq/GCP keys need rotation — remind if not done

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ AVAILABLE CAPABILITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
When a request comes in, determine which capability to use:

1. 📧 Email Intelligence — "mails cheppu", "check mail", "inbox"
2. 📅 Calendar — "today schedule", "add to calendar", "events"
3. 🌅 Daily Brief — "brief", "good morning", "what's up", "update"
4. 🌐 Tech News — "tech news", "AI lo emi jarigindi", "what's new"
5. 💻 Dev Assistant — code questions, errors, architecture
6. 🧠 Memory — "remember that", recall context
7. 📊 Project Status — "[project name] status", "what's pending"
8. 🎯 Career/Internships — "internships", "resume", "apply"
9. 🖥️ Screen — vision analysis
10. 🌤️ Weather — "weather", "outside ela undi"
11. 🐙 GitHub — "GitHub lo emi undi", "repo status"
12. 💪 LeetCode — "leetcode stats", "CP cheyyali"
13. 📄 Paper Summarizer — arXiv link, PDF
14. 📋 Clipboard AI — clipboard content
15. ⏰ Focus Mode — "focus mode", "pomodoro"
16. 🤖 Auto Commit — "commit message", git
17. 🚨 Hackathon Mode — "hackathon mode", "submission"
18. ⏰ Reminders — "remind me", "set reminder"
19. 📁 File Management — "create project", "scaffold", "make file", "new folder"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔐 SECURITY (CRITICAL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Before ANY git push discussion:
- "Bro, push cheyyamundu — .env gitignore lo undi aa? API keys check chesav aa?"
Detect in code/diff: sk-, AIza, gsk_, ghp_, AKIA, .env committed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📐 RESPONSE FORMAT RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Default (80% of responses):
- SHORT. 1-4 lines max for simple queries
- Direct answer first, context after
- Tenglish naturally woven in, not forced

Code responses:
- Always in a code block with language tag
- Always runnable / copy-paste ready

Never:
- "Certainly!" / "Great question!" / "Of course!"
- "As an AI language model..."
- Suggest paid tools before free options
- Give theory when he needs code

Always end action items with: "Cheyyadam start cheyyala? 🚀"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌙 TIME-AWARE BEHAVIOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6AM-9AM:   Morning brief mode — deliver daily digest proactively
9AM-6PM:   Work mode — focused, efficient, minimal chitchat
6PM-10PM:  Project/dev mode — suggest what to build, track progress
10PM-12AM: Wind-down — "Emi chesav today? Tomorrow ki plan cheyyi"
12AM+:     "Bro seriously — sleep cheyyali. [current task] tomorrow finish cheyyochu"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏁 NORTH STAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Everything VOID does serves one goal:
Help Karthik ship great projects, land a top internship,
maintain his CGPA, and become the best developer he can be —
while actually enjoying the journey.

Not a tool. A partner."""


# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 SERVICE REGISTRY (keyword matching for fast routing)
# ═══════════════════════════════════════════════════════════════════════════════

SERVICE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "weather": {
        "func": "services.weather_service.get_weather",
        "keywords": ["weather", "viza", "vishak", "rain", "temperature", "outside"],
        "description": "Check weather for a city (default: Visakhapatnam)",
    },
    "news": {
        "func": "services.news_service.get_tech_news_formatted",
        "keywords": ["tech news", "ai lo", "what's new", "hacker news", "dev news", "trending"],
        "description": "Get tech news headlines",
    },
    "github": {
        "func": "services.github_service.get_github_overview",
        "keywords": ["github", "git lo", "repo", "commit", "pr", "star", "repository"],
        "description": "Check GitHub activity and repo status",
    },
    "leetcode": {
        "func": "services.leetcode_service.get_stats_formatted",
        "keywords": ["leetcode", "cp cheyyali", "dsa", "competitive", "streak"],
        "description": "Check LeetCode stats and streak",
    },
    "email": {
        "func": "services.gmail_service.check_inbox",
        "keywords": ["mail", "email", "inbox", "gmail", "messages", "inbox lo"],
        "description": "Check Gmail inbox for unread emails",
    },
    "calendar": {
        "func": "services.calendar_service.get_today_schedule",
        "keywords": ["calendar", "schedule", "today", "events", "busy", "free"],
        "description": "Check today's calendar schedule",
    },
    "clipboard": {
        "func": "services.clipboard_service.process_clipboard",
        "keywords": ["clipboard", "clip board", "copy chesina"],
        "description": "Analyze clipboard content",
    },
    "focus": {
        "func": "services.focus_service.start_focus",
        "keywords": ["focus", "pomodoro", "distraction", "block", "concentrate"],
        "description": "Start a focus/pomodoro session",
    },
    "reminder": {
        "func": "services.reminder_service.set_reminder",
        "keywords": ["remind", "reminder", "remember me", "notify", "alert"],
        "description": "Set a reminder with notification",
    },
    "project_status": {
        "func": "services.project_tracker.get_project_status",
        "keywords": ["status", "project update", "progress", "blocker", "pending"],
        "description": "Get status of a specific project",
    },
    "career": {
        "func": "services.career_service.get_application_status",
        "keywords": ["internship", "career", "apply", "resume", "job", "application", "interview"],
        "description": "Track and manage internship applications",
    },
    "hackathon": {
        "func": "services.hackathon_service.activate_hackathon_mode",
        "keywords": ["hackathon", "submission", "deadline", "ship", "hack mode"],
        "description": "Activate hackathon mode with timer",
    },
    "paper": {
        "func": "services.pdf_service.summarize_arxiv",
        "keywords": ["arxiv", "paper", "research", "pdf", "summarize paper", "article"],
        "description": "Summarize an arXiv paper or PDF",
    },
    "git": {
        "func": "services.git_service.check_before_push",
        "keywords": ["git", "commit", "push", "diff", "security", "api key"],
        "description": "Check git changes for security issues and generate commit messages",
    },
    "vision": {
        "func": "services.vision_service.analyze",
        "keywords": ["screen", "screenshot", "vision", "look at", "see", "analyze"],
        "description": "Analyze a screenshot using vision model",
    },
}

# File/project keywords for scaffolding routing
FILE_ACTION_KEYWORDS = [
    "create project", "scaffold", "new project", "make file", "create file",
    "new folder", "create folder", "mkdir", "generate project",
    "boilerplate", "template", "set up project", "build a",
    "write a file", "add file", "delete file", "remove file",
    "move file", "rename file", "copy file", "list files", "show files",
    "expense-tracker", "fastapi project", "react project", "cli tool",
    "python project", "web app", "start project",
]

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 LANGGRAPH TOOL WRAPPERS
# ── Each service function is wrapped as a @tool so the LangGraph tool-calling
#    node can invoke it. The tools module also serves as the canonical reference
#    for all service callables.
# ═══════════════════════════════════════════════════════════════════════════════

# ── Quick API Tools ────────────────────────────────────────────────────────────

@tool
def get_weather_tool(city: str = "Visakhapatnam") -> str:
    """Check weather for a city (default: Visakhapatnam). Use when user asks about weather, temperature, rain, or outside conditions."""
    from services.weather_service import get_weather
    result = get_weather(city)
    return result or "🌤️ Weather fetch avvaledhu bro — API key or network issue"


@tool
def get_news_tool(count: int = 4) -> str:
    """Get latest tech news headlines from Hacker News, Dev.to, and NewsAPI."""
    from services.news_service import get_tech_news_formatted
    result = get_tech_news_formatted(count)
    return result or "🌐 Tech news fetch avvaledhu"


@tool
def get_github_tool() -> str:
    """Check GitHub activity overview: recent commits, PRs, and repo stats for MKarthik730."""
    from services.github_service import get_github_overview
    result = get_github_overview()
    return result or "💻 GitHub fetch avvaledhu"


@tool
def get_leetcode_tool() -> str:
    """Check LeetCode stats: total solved, easy/medium/hard breakdown, and streak."""
    from services.leetcode_service import get_stats_formatted
    result = get_stats_formatted()
    return result or "💪 LeetCode fetch avvaledhu"


# ── Google API Tools ───────────────────────────────────────────────────────────

@tool
def check_email_tool(limit: int = 10) -> str:
    """Check Gmail inbox for unread emails, sorted by priority (urgent first)."""
    from services.gmail_service import check_inbox
    result = check_inbox(limit)
    if result and isinstance(result, list):
        if "error" in result[0]:
            return f"📧 {result[0]['error']}"
        lines = ["📧 **Inbox Summary**"]
        for e in result[:8]:
            if "category" in e and "subject" in e:
                lines.append(f"  {e['category']} {e['subject'][:60]}")
        return "\n".join(lines)
    return "📧 Inbox empty bro — or check avvaledhu"


@tool
def get_calendar_tool(scope: str = "today") -> str:
    """Check Google Calendar. Use 'today' for today's schedule, 'week' for week overview."""
    from services.calendar_service import get_today_schedule, get_week_overview
    if scope == "week":
        return get_week_overview()
    return get_today_schedule()


# ── Desktop Tools ──────────────────────────────────────────────────────────────

@tool
def analyze_clipboard_tool(text: str) -> str:
    """Analyze clipboard content: detect type (error, code, URL, JD, text) and provide AI response."""
    from services.clipboard_service import process_clipboard
    result = process_clipboard(text)
    return f"📋 Clipboard analysis:\n{result}" if result else "📋 Clipboard empty bro"


@tool
def start_focus_tool(duration_minutes: int = 25) -> str:
    """Start a focus/pomodoro session for N minutes (default: 25)."""
    from services.focus_service import start_focus
    return start_focus(duration_minutes)


@tool
def set_reminder_tool(text: str, when: str = "in 30 minutes") -> str:
    """Set a reminder with desktop notification. when can be like 'in 30 minutes', 'at 3 PM', 'tomorrow 9 AM'."""
    from services.reminder_service import set_reminder
    return set_reminder(text, when)


# ── Intelligence Tools ─────────────────────────────────────────────────────────

@tool
def get_project_status_tool(project_name: str = "") -> str:
    """Get status of a tracked project. Projects: void, memoir, cognitus, devcollab, aegis, ai-resume-ranker. Empty for all."""
    from services.project_tracker import get_project_status, get_all_projects_summary
    if not project_name:
        return get_all_projects_summary()
    return get_project_status(project_name)


@tool
def track_career_tool(action: str = "status", company: str = "", role: str = "", jd_text: str = "") -> str:
    """Career management. Actions: 'status' (view all), 'track' (add application with company+role), 'analyze_jd' (match against skills)."""
    from services.career_service import get_application_status, track_application, analyze_jd
    if action == "track":
        if not company or not role:
            return "Company and role cheppu bro"
        return track_application(company, role)
    elif action == "analyze_jd":
        if not jd_text:
            return "JD text ivvu bro analyze chestanu"
        return analyze_jd(jd_text)
    return get_application_status()


@tool
def hackathon_mode_tool(action: str = "start", hours_remaining: float = 24.0, name: str = "") -> str:
    """Hackathon mode with countdown timer. Actions: 'start', 'status', 'end'."""
    from services.hackathon_service import activate_hackathon_mode, get_hackathon_status, end_hackathon
    if action == "end":
        return end_hackathon()
    elif action == "status":
        return get_hackathon_status()
    return activate_hackathon_mode(hours_remaining, name)


@tool
def summarize_paper_tool(url: str, paper_type: str = "arxiv") -> str:
    """Summarize an arXiv paper or article from URL. paper_type: 'arxiv' or 'article'."""
    from services.pdf_service import summarize_arxiv, summarize_article
    if paper_type == "arxiv":
        return summarize_arxiv(url)
    return summarize_article(url)


# ── Git / Security Tools ───────────────────────────────────────────────────────

@tool
def git_security_check_tool() -> str:
    """Check git diff for exposed API keys and secrets before push."""
    from services.git_service import check_before_push
    return check_before_push()


@tool
def generate_commit_message_tool() -> str:
    """Generate a conventional commit message from the current git diff."""
    from services.git_service import generate_commit_message
    msg = generate_commit_message()
    return f"🤖 **Suggested commit message:**\n`{msg}`"


# ── Memory Tools ───────────────────────────────────────────────────────────────

@tool
def remember_tool(content: str, category: str = "general") -> str:
    """Store an important fact in long-term memory for future recall."""
    add_memory(content, category=category, importance=2)
    return f"Got it bro, I'll remember that! {content[:100]}"


@tool
def recall_memory_tool(query: str) -> str:
    """Search long-term memory for relevant information about a topic."""
    result = get_context_for_query(query, memory_limit=5, history_limit=5)
    if result:
        return f"🧠 **From my memory:**\n{result[:800]}"
    return "I don't have specific memories about that yet bro."


# ── File Management Tools ──────────────────────────────────────────────────────

@tool
def create_file_tool(file_path: str, content: str = "") -> str:
    """Create a new file in the workspace. Never requires confirmation. Give the full relative path and content."""
    from services.file_service import create_file
    try:
        result = create_file(file_path, content)
        return f"✅ File created: `{file_path}` ({result.get('size', 0)} bytes)"
    except Exception as e:
        return f"❌ File create avvaledhu: {str(e)[:200]}"


@tool
def create_directory_tool(dir_path: str) -> str:
    """Create a new directory in the workspace. Never requires confirmation."""
    from services.file_service import create_directory
    try:
        create_directory(dir_path)
        return f"✅ Directory created: `{dir_path}`"
    except Exception as e:
        return f"❌ Directory create avvaledhu: {str(e)[:200]}"


@tool
def list_files_tool(directory_path: str = ".", pattern: str = "*") -> str:
    """List files and directories in a workspace path. pattern supports glob (e.g. '*.py', '**/*')."""
    from services.file_service import list_files
    try:
        entries = list_files(directory_path, pattern)
        if not entries:
            return f"📁 `{directory_path}` lo emi ledhu bro"

        lines = [f"📁 **{directory_path}/** ({len(entries)} entries)"]
        for e in entries:
            icon = "📁" if e["type"] == "directory" else "📄"
            size = f" ({e['size']} bytes)" if e["type"] == "file" else ""
            lines.append(f"  {icon} {e['name']}{size}")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ List avvaledhu: {str(e)[:200]}"


@tool
def delete_file_tool(file_path: str) -> str:
    """Delete a file (soft-delete to .void_trash). Requires user confirmation before executing."""
    from services.file_service import delete_file
    try:
        result = delete_file(file_path)
        return f"✅ File moved to trash: `{file_path}`"
    except Exception as e:
        return f"❌ Delete avvaledhu: {str(e)[:200]}"


@tool
def move_file_tool(source_path: str, dest_path: str) -> str:
    """Move or rename a file. Requires user confirmation if destination exists."""
    from services.file_service import move_file
    try:
        result = move_file(source_path, dest_path)
        note = " (overwrote existing)" if result.get("overwrote") else ""
        return f"✅ Moved: `{source_path}` -> `{dest_path}`{note}"
    except Exception as e:
        return f"❌ Move avvaledhu: {str(e)[:200]}"


@tool
def plan_and_scaffold_tool(description: str) -> str:
    """Plan and execute a project scaffold from a natural language description. E.g. 'create a FastAPI project called expense-tracker'."""
    from services.project_scaffold_service import plan_project, execute_plan, format_plan_for_response, format_execution_results
    from services.file_service import is_destructive
    try:
        plan = plan_project(description)
        destructive = is_destructive(plan)

        if destructive:
            formatted = format_plan_for_response(plan)
            return (
                f"📋 **Plan ready for: {description}**\n\n"
                f"{formatted}\n\n"
                f"⚠️ This plan has destructive operations. Cheyyamantava? "
                f"/files/execute ki plan send cheyyi confirm cheyyadaniki."
            )

        # Auto-execute for pure creates
        result = execute_plan(plan)
        return format_execution_results(result, description)

    except Exception as e:
        return f"❌ Scaffold avvaledhu: {str(e)[:200]}"


# ═══════════════════════════════════════════════════════════════════════════════
# 📋 AGENT STATE (TypedDict for LangGraph StateGraph)
# ═══════════════════════════════════════════════════════════════════════════════

class AgentState(TypedDict):
    """The state object passed through LangGraph nodes."""
    user_input: str
    intent: Optional[str]
    intent_input: Optional[str]
    service_result: Optional[str]
    plan: Optional[List[Dict[str, Any]]]
    requires_confirmation: bool
    execution_results: Optional[Dict[str, Any]]
    context: str
    response: Optional[str]
    error: Optional[str]


# ═══════════════════════════════════════════════════════════════════════════════
# 🧠 HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _resolve_service(service_name: str) -> Optional[Any]:
    """Dynamically import and return a service function."""
    entry = SERVICE_REGISTRY.get(service_name)
    if not entry:
        return None
    module_path, func_name = entry["func"].rsplit(".", 1)
    try:
        module = __import__(module_path, fromlist=[func_name])
        return getattr(module, func_name)
    except (ImportError, AttributeError):
        return None


def _detect_intent(user_input: str) -> Dict[str, Any]:
    """Detect user intent using keyword matching + LLM fallback.

    Returns dict with 'action', 'input', and 'reasoning' keys.
    """
    user_lower = user_input.lower().strip()

    # ── Check for file/project actions first ──────────────────────────────────
    for kw in FILE_ACTION_KEYWORDS:
        if kw in user_lower:
            return {
                "action": "scaffold",
                "input": user_input,
                "reasoning": f"File action keyword: '{kw}'",
            }

    # ── Try fast keyword match against existing services ──────────────────────
    for service_name, entry in SERVICE_REGISTRY.items():
        for kw in entry["keywords"]:
            if kw in user_lower:
                return {
                    "action": service_name,
                    "reasoning": f"Keyword match: '{kw}'",
                    "input": user_input,
                }

    # ── Check for memory operations ──────────────────────────────────────────
    memory_patterns = [
        (r"\bremember\b.*", "remember"),
        (r"\brecall\b.*", "recall_memory"),
        (r"\bforget\b", "forget"),
        (r"\bwhat.*remember\b", "recall_memory"),
        (r"\bnote\b", "remember"),
        (r"\bsave\b.*\bthis\b", "remember"),
    ]
    for pattern, action in memory_patterns:
        if re.search(pattern, user_lower):
            if action == "remember":
                value = re.sub(r"remember\s+(that\s+)?", "", user_input, flags=re.IGNORECASE)
                return {"action": "remember", "input": value.strip()}
            return {"action": "recall_memory", "input": user_input}

    # ── Vision/screen analysis ────────────────────────────────────────────────
    if any(w in user_lower for w in ["look at", "see this", "analyze screen", "screenshot"]):
        return {"action": "analyze_screen", "input": user_input}

    # ── Git/commit ────────────────────────────────────────────────────────────
    if any(w in user_lower for w in ["commit message", "commit raayi"]):
        return {"action": "git_commit", "input": user_input}

    # ── LLM fallback for ambiguous queries ────────────────────────────────────
    prompt = (
        "Analyze this user request and respond with ONLY a JSON object:\n"
        '{"action": "action_name", "reasoning": "brief reason"}\n\n'
        f"User: {user_input}\n\n"
        "Actions available: "
        + ", ".join(f"{k} ({v['description']})" for k, v in SERVICE_REGISTRY.items())
        + ", remember, recall_memory, scaffold, chat"
    )
    try:
        result = llm_run(prompt, max_tokens=100, temperature=0.1)
        if result.startswith("{"):
            intent = json.loads(result)
            known = set(SERVICE_REGISTRY.keys()) | {"remember", "recall_memory", "chat", "scaffold"}
            if intent.get("action") in known:
                return intent
    except (json.JSONDecodeError, Exception):
        pass

    return {"action": "chat", "input": user_input, "reasoning": "default"}


def _handle_service_call(action: str, input_text: str) -> str:
    """Route to a service and return its result. Handles special arg extraction."""
    # ── Memory operations ─────────────────────────────────────────────────────
    if action == "remember":
        add_memory(input_text, category="general", importance=2)
        return f"Got it bro, I'll remember that! {input_text[:100]}"

    if action == "recall_memory":
        result = get_context_for_query(input_text, memory_limit=5, history_limit=5)
        if result:
            return f"🧠 **From my memory:**\n{result[:800]}"
        return "I don't have specific memories about that yet bro."

    # ── Analyze screen ────────────────────────────────────────────────────────
    if action == "analyze_screen":
        return "Screenshot ivvu bro — analyze chestanu. Use /screen/analyze endpoint."

    # ── Git commit ────────────────────────────────────────────────────────────
    if action == "git_commit":
        from services.git_service import generate_commit_message
        msg = generate_commit_message()
        return f"🤖 **Suggested commit message:**\n`{msg}`"

    # ── Calendar week overview ────────────────────────────────────────────────
    if action == "calendar" and any(w in input_text.lower() for w in ["week", "this week", "overview"]):
        try:
            from services.calendar_service import get_week_overview
            return get_week_overview()
        except Exception as e:
            return f"Calendar week fetch avvaledhu: {str(e)[:100]}"

    # ── Project status (extract project name) ────────────────────────────────
    if action == "project_status":
        func = _resolve_service("project_status")
        if func is None:
            return "Project tracker setup avvaledhu bro"
        known = ["memoir", "cognitus", "devcollab", "void", "aegis", "resume ranker", "ai-resume-ranker"]
        project = None
        for p in known:
            if p in input_text.lower():
                project = p
                break
        if not project:
            from services.project_tracker import get_all_projects_summary
            return get_all_projects_summary()
        return func(project)

    # ── Generic service registry lookup ───────────────────────────────────────
    if action in SERVICE_REGISTRY:
        func = _resolve_service(action)
        if func is None:
            return f"Okka second bro — {SERVICE_REGISTRY[action]['description']} connect avvaledhu."

        try:
            if action == "weather":
                cities = re.findall(r"(?:in|for|at)\s+([A-Za-z\s]+?)(?:\s*\?|$)", input_text, re.IGNORECASE)
                city = cities[0].strip() if cities else None
                result = func(city) if city else func()
                return result or "🌤️ Weather fetch avvaledhu bro — API key or network issue"

            elif action == "focus":
                match = re.search(r"(\d+)\s*(?:min|minutes|hours?\b)", input_text, re.IGNORECASE)
                if match:
                    num = int(match.group(1))
                    if "hour" in match.group(2).lower():
                        num *= 60
                    return func(num)
                return func(25)

            elif action == "reminder":
                task_match = re.search(r"(?:remind me to|remind me that|set reminder)\s+(.+?)(?:\s+in\s+|\s+at\s+|\s+tomorrow\s+)", input_text, re.IGNORECASE)
                time_match = re.search(r"(?:in\s+)?(\d+\s*(?:min|minutes|hours?|hrs?))\s*|(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)", input_text)
                if task_match:
                    task = task_match.group(1).strip()
                    when = time_match.group(0) if time_match else "in 1 hour"
                    return func(task, when)
                return func(input_text, "in 30 minutes")

            elif action in ("news", "github", "leetcode"):
                result = func()
                return result or f"{action} fetch avvaledhu bro"

            elif action == "email":
                result = func(10)
                if result and isinstance(result, list):
                    if "error" in result[0]:
                        return f"📧 {result[0]['error']}"
                    lines = ["📧 **Inbox Summary**"]
                    for e in result[:8]:
                        if "category" in e and "subject" in e:
                            lines.append(f"  {e['category']} {e['subject'][:60]}")
                    return "\n".join(lines)
                return "📧 Inbox empty bro"

            elif action == "hackathon":
                match = re.search(r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)", input_text, re.IGNORECASE)
                hours = float(match.group(1)) if match else 24.0
                name_match = re.search(r"for\s+(.+?)(?:\s+in\s+|\s+at\s+|$)", input_text, re.IGNORECASE)
                h_name = name_match.group(1).strip() if name_match else ""
                return func(hours, h_name)

            elif action == "paper":
                url_match = re.search(r"https?://\S+", input_text)
                if url_match:
                    return func(url_match.group(0))
                return "arXiv link ivvu bro"

            elif action == "clipboard":
                return func(input_text)

            else:
                result = func()
                return result or f"Okka second bro — {action} connect avvaledhu"

        except Exception as e:
            log_action(f"{action}_error", str(e), success=False)
            return f"Sorry bro — {action} lo issue vachindi. {str(e)[:80]}"

    return ""


# ═══════════════════════════════════════════════════════════════════════════════
# 🔄 LANGGRAPH NODE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def detect_intent_node(state: AgentState) -> dict:
    """Node 1: Detect intent from user input using keyword matching + LLM fallback."""
    user_input = state["user_input"]
    intent = _detect_intent(user_input)
    action = intent.get("action", "chat")
    intent_input = intent.get("input", user_input)
    context = get_context_for_query(user_input, memory_limit=3, history_limit=3)

    log_action("agent_intent", user_input, action)

    return {
        "intent": action,
        "intent_input": intent_input,
        "context": context,
    }


def execute_service_node(state: AgentState) -> dict:
    """Node 2a: Execute a matched service and return the result."""
    action = state["intent"]
    input_text = state["intent_input"]
    context = state.get("context", "")

    result = _handle_service_call(action, input_text)

    # Log conversation
    if action != "remember" and not result.startswith("ERROR"):
        add_conversation(state["user_input"], result, context)

    return {"service_result": result}


def llm_chat_node(state: AgentState) -> dict:
    """Node 2b: Fall back to LLM conversation for chat/intent."""
    user_input = state["user_input"]
    context = state.get("context", "")
    now = datetime.now()
    hour = now.hour

    time_context = ""
    if 6 <= hour < 9:
        time_context = "\n(It's morning — offer daily brief if they want)"
    elif 22 <= hour or hour < 6:
        time_context = "\n(It's late — suggest wrapping up if they're coding)"

    context_block = "Relevant context from memory:\n" + context if context else ""
    time_str = now.strftime('%I:%M %p IST')
    response_prompt = (
        VOID_SYSTEM_PROMPT + "\n\n"
        + context_block + "\n"
        + "Current time: " + time_str + "\n"
        + "User: " + user_input + "\n\n"
        + "Respond in Tenglish style. Keep it conversational and natural. Max 4 sentences."
        + time_context
    )

    response = llm_run(response_prompt, max_tokens=400, temperature=0.8)

    if response.startswith("ERROR"):
        response = f"Sorry bro — {response}"

    add_conversation(user_input, response, context)

    return {"response": response}


def plan_scaffold_node(state: AgentState) -> dict:
    """Node 2c: Generate a project scaffolding plan from user description."""
    from services.project_scaffold_service import plan_project, format_plan_for_response
    from services.file_service import is_destructive

    user_input = state["intent_input"]
    context = state.get("context", "")

    try:
        plan = plan_project(user_input)
        destructive = is_destructive(plan)
        formatted = format_plan_for_response(plan)

        if destructive:
            plan_str = json.dumps(plan)
            response = (
                f"📋 **Plan ready bro!** Check it out:\n\n"
                f"{formatted}\n\n"
                f"⚠️ This needs confirmation — delete/overwrite operations undi.\n"
                f"Confirm chestava? (Plan saved, hit /files/execute with plan or cheppu continue annav ante execute chestanu)"
            )
            return {"plan": plan, "requires_confirmation": True, "response": response}

        # Auto-execute for pure creates
        from services.project_scaffold_service import execute_plan, format_execution_results
        result = execute_plan(plan)
        response = format_execution_results(result, user_input)
        add_conversation(state["user_input"], response, context)

        return {
            "plan": plan,
            "requires_confirmation": False,
            "execution_results": result,
            "response": response,
        }

    except Exception as e:
        error_msg = f"❌ Scaffold avvaledhu bro: {str(e)[:200]}"
        return {"response": error_msg, "error": str(e)}


def extract_plan_response_node(state: AgentState) -> dict:
    """Node 3: Extract the response — prefer explicit response, fall back to service_result."""
    if state.get("response"):
        return {}
    if state.get("service_result"):
        return {"response": state["service_result"]}
    return {"response": "Sorry bro, emo artham avvaledhu. Malli cheppu? 🤔"}


def should_route(state: AgentState) -> str:
    """Conditional edge: decide which node to go to based on intent."""
    intent = state.get("intent", "chat")

    if intent == "scaffold":
        return "scaffold"
    if intent == "chat" or intent is None:
        return "chat"
    # Known service, memory, etc.
    return "service"


# ═══════════════════════════════════════════════════════════════════════════════
# 🔗 BUILD THE LANGGRAPH STATEGRAPH
# ═══════════════════════════════════════════════════════════════════════════════

_agent_graph = None

def _build_graph():
    """Build and compile the LangGraph StateGraph. Returns the compiled graph."""
    global _agent_graph
    if _agent_graph is not None:
        return _agent_graph

    if not LANGGRAPH_AVAILABLE:
        print("[VOID AGENT] LangGraph not installed — using legacy keyword router")
        _agent_graph = None
        return None

    try:
        workflow = StateGraph(AgentState)

        # Register nodes
        workflow.add_node("detect_intent", detect_intent_node)
        workflow.add_node("execute_service", execute_service_node)
        workflow.add_node("llm_chat", llm_chat_node)
        workflow.add_node("plan_scaffold", plan_scaffold_node)
        workflow.add_node("extract_response", extract_plan_response_node)

        # Set entry point
        workflow.set_entry_point("detect_intent")

        # Conditional routing from detect_intent
        workflow.add_conditional_edges(
            "detect_intent",
            should_route,
            {
                "service": "execute_service",
                "chat": "llm_chat",
                "scaffold": "plan_scaffold",
            },
        )

        # All paths converge to extract_response
        workflow.add_edge("execute_service", "extract_response")
        workflow.add_edge("llm_chat", "extract_response")
        workflow.add_edge("plan_scaffold", "extract_response")

        # extract_response is the finish point
        workflow.add_edge("extract_response", END)

        _agent_graph = workflow.compile()
        print("[VOID AGENT] LangGraph StateGraph compiled successfully")
        return _agent_graph

    except Exception as e:
        print(f"[VOID AGENT] LangGraph build failed: {e} — using legacy router")
        _agent_graph = None
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

def run_agent(user_input: str) -> str:
    """Main agent entry point. Uses LangGraph StateGraph if available, falls back to legacy router.

    Args:
        user_input: Raw user message

    Returns:
        Agent response string in Tenglish
    """
    graph = _build_graph()

    if graph is not None:
        # LangGraph path
        initial_state: AgentState = {
            "user_input": user_input,
            "intent": None,
            "intent_input": None,
            "service_result": None,
            "plan": None,
            "requires_confirmation": False,
            "execution_results": None,
            "context": "",
            "response": None,
            "error": None,
        }
        try:
            final_state = graph.invoke(initial_state)
            result = final_state.get("response", "Sorry bro — response generate avvaledhu")
            return result if result else "Sorry bro — response generate avvaledhu"
        except Exception as e:
            log_action("agent_graph_error", user_input, str(e), success=False)
            # Fall through to legacy router
            print(f"[VOID AGENT] Graph execution failed: {e} — falling back to legacy")

    # ── Legacy path (no LangGraph or graph execution failed) ──────────────────
    context = get_context_for_query(user_input, memory_limit=3, history_limit=3)
    intent = _detect_intent(user_input)
    action = intent.get("action", "chat")
    input_text = intent.get("input", user_input)

    log_action("agent_intent", user_input, action)

    if action == "scaffold":
        from services.project_scaffold_service import plan_project, execute_plan, format_plan_for_response, format_execution_results
        from services.file_service import is_destructive
        try:
            plan = plan_project(input_text)
            destructive = is_destructive(plan)

            if destructive:
                formatted = format_plan_for_response(plan)
                return (
                    f"📋 **Plan ready bro!** Check it out:\n\n"
                    f"{formatted}\n\n"
                    f"⚠️ This needs confirmation — delete/overwrite operations undi.\n"
                    f"Cheppu bro — continue cheyyamantara?"
                )

            result = execute_plan(plan)
            response = format_execution_results(result, input_text)
            add_conversation(user_input, response, context)
            return response
        except Exception as e:
            return f"❌ Scaffold avvaledhu bro: {str(e)[:200]}"

    result = _handle_service_call(action, input_text)

    if action != "remember" and not result.startswith("ERROR"):
        add_conversation(user_input, result, context)

    return result


def run_simple(prompt: str) -> str:
    """Direct LLM call without agent logic (for testing)."""
    return llm_run(prompt, max_tokens=300)


def get_graph() -> Optional[Any]:
    """Get the compiled LangGraph (for advanced usage). Returns None if not available."""
    return _build_graph()
