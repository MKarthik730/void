"""
VOID v3.0 — Full Agentic Core
Hyper-personal AI assistant for Karthik (MKarthik730)
System prompt + service registry + intelligent intent routing
"""

import json
import re
from typing import Optional, Dict, Any
from datetime import datetime

from services.ollama_service import run as llm_run
from services.memory_service import (
    get_context_for_query,
    add_conversation,
    add_memory,
    log_action,
)

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
# 🔧 SERVICE REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

SERVICE_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ── Quick APIs ────────────────────────────────────────────────────────────
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
    # ── Google APIs ───────────────────────────────────────────────────────────
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
    # ── Desktop ───────────────────────────────────────────────────────────────
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
    # ── Intelligence ──────────────────────────────────────────────────────────
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
    # ── Git / Security ────────────────────────────────────────────────────────
    "git": {
        "func": "services.git_service.check_before_push",
        "keywords": ["git", "commit", "push", "diff", "security", "api key"],
        "description": "Check git changes for security issues and generate commit messages",
    },
    # ── Vision ─────────────────────────────────────────────────────────────────
    "vision": {
        "func": "services.vision_service.analyze",
        "keywords": ["screen", "screenshot", "vision", "look at", "see", "analyze"],
        "description": "Analyze a screenshot using vision model",
    },
}


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
    """Detect user intent using keyword matching + LLM fallback."""
    user_lower = user_input.lower().strip()

    # Try fast keyword match first
    for service_name, entry in SERVICE_REGISTRY.items():
        for kw in entry["keywords"]:
            if kw in user_lower:
                return {
                    "action": service_name,
                    "reasoning": f"Keyword match: '{kw}'",
                    "input": user_input,
                }

    # Check for memory operations
    memory_patterns = [
        (r"\bremember\b", "remember"),
        (r"\brecall\b", "recall"),
        (r"\bforget\b", "forget"),
        (r"\bwhat.*remember\b", "recall"),
        (r"\bnote\b", "remember"),
        (r"\bsave\b.*\bthis\b", "remember"),
    ]
    for pattern, action in memory_patterns:
        if re.search(pattern, user_lower):
            if action == "remember":
                # Extract what to remember after the keyword
                value = re.sub(r"remember\s+(that\s+)?", "", user_input, flags=re.IGNORECASE)
                return {"action": "remember", "input": value.strip()}
            return {"action": "recall_memory", "input": user_input}

    # Vision/screen analysis
    if any(w in user_lower for w in ["look at", "see this", "analyze screen", "screenshot"]):
        return {"action": "analyze_screen", "input": user_input}

    # Git/commit
    if any(w in user_lower for w in ["commit message", "commit raayi"]):
        return {"action": "git_commit", "input": user_input}

    # LLM fallback for ambiguous queries
    prompt = (
        "Analyze this user request and respond with ONLY a JSON object:\n"
        "{\"action\": \"action_name\", \"reasoning\": \"brief reason\"}\n\n"
        f"User: {user_input}\n\n"
        "Actions available: "
        + ", ".join(f"{k} ({v['description']})" for k, v in SERVICE_REGISTRY.items())
        + ", remember, recall_memory, chat"
    )
    try:
        result = llm_run(prompt, max_tokens=100, temperature=0.1)
        if result.startswith("{"):
            intent = json.loads(result)
            if intent.get("action") in SERVICE_REGISTRY or intent.get("action") in [
                "remember", "recall_memory", "chat"
            ]:
                return intent
    except (json.JSONDecodeError, Exception):
        pass

    return {"action": "chat", "input": user_input, "reasoning": "default"}


def run_agent(user_input: str) -> str:
    """Main agent entry point. Detects intent, routes to service, returns response."""
    # Get context from memory
    context = get_context_for_query(user_input, memory_limit=3, history_limit=3)

    # Detect intent
    intent = _detect_intent(user_input)
    action = intent.get("action", "chat")
    input_text = intent.get("input", user_input)

    log_action("agent_intent", user_input, action)

    # ── Route to service ──────────────────────────────────────────────────────
    result = _route_action(action, input_text)

    # Add conversation to memory (unless it's a system action)
    if action != "remember" and not result.startswith("ERROR"):
        add_conversation(user_input, result, context)

    return result


def _route_action(action: str, input_text: str) -> str:
    """Route to the appropriate service based on detected intent."""

    # ── Memory operations ─────────────────────────────────────────────────────
    if action == "remember":
        add_memory(input_text, category="general", importance=2)
        return f"Got it bro, I'll remember that! {input_text[:100]}"

    if action == "recall_memory":
        result = get_context_for_query(input_text, memory_limit=5, history_limit=5)
        if result:
            return f"🧠 **From my memory:**\n{result[:800]}"
        return "I don't have specific memories about that yet bro. But I can help you with whatever you're working on!"

    # ── Calendar week overview ────────────────────────────────────────────────
    if action == "calendar" and any(w in input_text.lower() for w in ["week", "this week", "overview"]):
        func = _resolve_service("calendar")
        if func is None:
            return "Calendar service setup avvaledhu bro — credentials.json check cheyyi"
        # Use week overview instead
        try:
            from services.calendar_service import get_week_overview
            return get_week_overview()
        except Exception as e:
            return f"Calendar week fetch avvaledhu: {str(e)[:100]}"

    # ── Project status (extract project name) ─────────────────────────────────
    if action == "project_status":
        func = _resolve_service("project_status")
        if func is None:
            return "Project tracker setup avvaledhu bro"

        # Try to extract project name
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

    # ── Service registry lookup ───────────────────────────────────────────────
    if action in SERVICE_REGISTRY:
        func = _resolve_service(action)
        if func is None:
            return f"Okka second bro — {SERVICE_REGISTRY[action]['description']} connect avvaledhu. Manual ga check cheyyi ippudu, fix chestaanu"

        try:
            # Special handling for services with specific args
            if action == "weather":
                # Extract city if mentioned
                cities = re.findall(r"(?:in|for|at)\s+([A-Za-z\s]+?)(?:\s*\?|$)", input_text, re.IGNORECASE)
                city = cities[0].strip() if cities else None
                result = func(city) if city else func()
                if result is None:
                    return "🌤️ Weather fetch avvaledhu bro — API key or network issue"
                return result

            elif action == "focus":
                # Extract minutes
                match = re.search(r"(\d+)\s*(?:min|minutes|hours?\b)", input_text, re.IGNORECASE)
                if match:
                    num = int(match.group(1))
                    if "hour" in match.group(2).lower():
                        num *= 60
                    return func(num)
                return func(25)  # Default 25 min

            elif action == "reminder":
                # Try to parse "remind me to [task] in/at [time]"
                task_match = re.search(r"(?:remind me to|remind me that|set reminder)\s+(.+?)(?:\s+in\s+|\s+at\s+|\s+tomorrow\s+)", input_text, re.IGNORECASE)
                time_match = re.search(r"(?:in\s+)?(\d+\s*(?:min|minutes|hours?|hrs?))\s*|(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)", input_text)
                if task_match:
                    task = task_match.group(1).strip()
                    when = time_match.group(0) if time_match else "in 1 hour"
                    return func(task, when)
                return func(input_text, "in 30 minutes")

            elif action in ("news", "github", "leetcode"):
                result = func()
                return result if result else f"{action} fetch avvaledhu bro"

            elif action in ("email",):
                result = func(10)
                if result and isinstance(result, list):
                    if "error" in result[0]:
                        return f"📧 {result[0]['error']}"
                    # Format email results
                    lines = ["📧 **Inbox Summary**"]
                    for e in result[:8]:
                        if "category" in e and "subject" in e:
                            lines.append(f"  {e['category']} {e['subject'][:60]}")
                    return "\n".join(lines)
                return "📧 Inbox empty bro — or check avvaledhu"

            elif action == "hackathon":
                # Extract hours
                match = re.search(r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)", input_text, re.IGNORECASE)
                hours = float(match.group(1)) if match else 24.0
                name = re.search(r"for\s+(.+?)(?:\s+in\s+|\s+at\s+|$)", input_text, re.IGNORECASE)
                hackathon_name = name.group(1).strip() if name else ""
                return func(hours, hackathon_name)

            elif action == "paper":
                # Extract URL
                url_match = re.search(r"https?://\S+", input_text)
                if url_match:
                    return func(url_match.group(0))
                return "arXiv link ivvu bro — URL ivvu summarize chestanu"

            elif action == "clipboard":
                # Pass the input as clipboard content
                return func(input_text)

            else:
                result = func()
                return result if result else f"Okka second bro — {action} connect avvaledhu"

        except Exception as e:
            log_action(f"{action}_error", str(e), success=False)
            return f"Sorry bro — {action} lo issue vachindi. {str(e)[:80]}"

    # ── Git commit ────────────────────────────────────────────────────────────
    if action == "git_commit":
        from services.git_service import generate_commit_message
        msg = generate_commit_message()
        return f"🤖 **Suggested commit message:**\n`{msg}`"

    # ── Default: Chat via LLM ─────────────────────────────────────────────────
    # Fall back to conversational response
    now = datetime.now()
    hour = now.hour

    # Time-aware greeting
    time_context = ""
    if 6 <= hour < 9:
        time_context = "\n(It's morning — offer daily brief if they want)"
    elif 22 <= hour or hour < 6:
        time_context = "\n(It's late — suggest wrapping up if they're coding)"

    response_prompt = (
        f"{VOID_SYSTEM_PROMPT}\n\n"
        f"{'Relevant context from memory:\\n' + context if context else ''}\n"
        f"Current time: {now.strftime('%I:%M %p IST')}\n"
        f"User: {input_text}\n\n"
        f"Respond in Tenglish style. Keep it conversational and natural. Max 4 sentences.{time_context}"
    )

    response = llm_run(response_prompt, max_tokens=400, temperature=0.8)

    if response.startswith("ERROR"):
        return f"Sorry bro — {response}"

    return response


def run_simple(prompt: str) -> str:
    """Direct LLM call without agent logic (for testing)."""
    return llm_run(prompt, max_tokens=300)
