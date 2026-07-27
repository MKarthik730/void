# 🧠 VOID — Hyper-Personal AI Desktop Assistant

> **Version:** 3.0.0  
> **Owner:** Karthik (MKarthik730) — 2nd Year CSE @ ANITS Visakhapatnam  
> **Stack:** FastAPI + LangGraph + Ollama (Qwen3:8b) + pgvector + PyQt6  
> **Language:** Tenglish (Telugu-English code-switching)  
> **Philosophy:** Local-first, hyper-personalized, always free-tier

---

## 📋 Table of Contents

1. [Overview](#-overview)
2. [Project Structure](#-project-structure)
3. [Tech Stack](#-tech-stack)
4. [Architecture](#-architecture)
5. [Agent System](#-agent-system)
6. [Backend (FastAPI)](#-backend-fastapi)
7. [Services Breakdown](#-services-breakdown)
8. [Frontend (PyQt6)](#-frontend-pyqt6)
9. [Database](#-database)
10. [Scheduler](#-scheduler)
11. [API Endpoints](#-api-endpoints)
12. [Configuration](#-configuration)
13. [Security & Error Handling](#-security--error-handling)
14. [Key Observations & Potential Issues](#-key-observations--potential-issues)
15. [Setup Guide](#-setup-guide)

---

## 🌟 Overview

**VOID** is not just another AI assistant — it's a **hyper-personal second brain, dev partner, career advisor, and daily operator** built exclusively for Karthik. It runs as a **floating glassmorphism widget** on the desktop that can:

- **See your screen** (via Ollama vision — llava/moondream)
- **Hear your voice** (via faster-whisper)
- **Speak back** (via pyttsx3 TTS)
- **Read your email** (Gmail API)
- **Check your calendar** (Google Calendar API)
- **Track your GitHub & LeetCode** activity
- **Set focus timers & reminders**
- **Manage hackathon countdowns**
- **Track internship applications**
- **Summarize papers & articles**
- **Scan git diffs for leaked API keys**
- **Remember everything** (pgvector RAG)
- **Respond in Tenglish** (natural Telugu-English mix)

All **AI runs locally** via Ollama — no cloud dependency for text generation.

---

## 📁 Project Structure

```
void/
├── VOID_OVERVIEW.md                          # This file
├── README.md                                 # Project readme
├── .gitignore                                # Git ignore rules
├── project/
│   ├── backend/                              # FastAPI server
│   │   ├── main.py                           # FastAPI app (70+ endpoints)
│   │   ├── config.py                         # 25+ env vars with defaults
│   │   ├── database.py                       # PostgreSQL + pgvector (lazy)
│   │   ├── models.py                         # 6 SQLAlchemy ORM models
│   │   ├── scheduler.py                      # Background daily brief/digest
│   │   ├── dataset.py                        # Synthetic Tenglish data generator
│   │   ├── requirements.txt                  # Python dependencies
│   │   ├── agent/
│   │   │   ├── __init__.py                   # Exports run_agent, run_simple
│   │   │   └── void_agent.py                 # Intent detection + service routing
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── screen_router.py              # /screen/* (analyze, explain, WhatsApp, save)
│   │   │   ├── text_router.py                # /text/* (suggest, summarize, translate)
│   │   │   └── meeting_router.py             # /meeting/*, /history/*
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── ollama_service.py             # LLM via Ollama (Qwen3:8b)
│   │       ├── vision_service.py             # Vision via Ollama (llava)
│   │       ├── memory_service.py             # pgvector RAG + conversation log
│   │       ├── embedding_service.py          # nomic-embed-text embeddings
│   │       ├── gmail_service.py              # Gmail read/send/categorize
│   │       ├── calendar_service.py           # Google Calendar CRUD + conflict detection
│   │       ├── weather_service.py            # OpenWeatherMap
│   │       ├── news_service.py               # HN + Dev.to + NewsAPI
│   │       ├── github_service.py             # GitHub activity + repo stats
│   │       ├── leetcode_service.py           # LeetCode streak + stats tracker
│   │       ├── voice_service.py              # faster-whisper ASR + pyttsx3 TTS
│   │       ├── git_service.py                # Diff analysis + secret scanning
│   │       ├── focus_service.py              # Pomodoro timer
│   │       ├── reminder_service.py           # Desktop notifications (plyer)
│   │       ├── hackathon_service.py          # Timed hackathon mode
│   │       ├── project_tracker.py            # 6 known projects in memory
│   │       ├── career_service.py             # Application tracking + JD analysis
│   │       ├── clipboard_service.py          # Content type detection + AI
│   │       └── pdf_service.py                # arXiv + article summarization
│   └── frontend/
│       └── void_ball.py                      # PyQt6 floating glassmorphism UI
└── void_memory.db                            # SQLite database (fallback/current)
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Agent** | Custom LangGraph-style | Multi-step intent detection & routing |
| **LLM** | Qwen3:8b (via Ollama) | Text generation, chat, analysis |
| **Vision** | llava / moondream (via Ollama) | Screen understanding, OCR |
| **Embeddings** | nomic-embed-text (via Ollama) | Vector embeddings for RAG |
| **Backend** | FastAPI + Pydantic + SQLAlchemy | REST API server |
| **Database** | PostgreSQL + pgvector (768-dim) | Persistent memory, RAG |
| **Frontend** | PyQt6 with glassmorphism | Desktop floating widget |
| **ASR** | faster-whisper (tiny/base) | Speech-to-text |
| **TTS** | pyttsx3 | Text-to-speech |
| **Auth** | Google OAuth 2.0 | Gmail + Calendar access |
| **External APIs** | OpenWeatherMap, NewsAPI, GitHub, LeetCode | Live data fetching |
| **Background Jobs** | threading + schedule | Daily briefs, digests, reminders |

---

## 🏗️ Architecture

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Desktop (User's Machine)                      │
│                                                                      │
│  ┌───────────────────┐    HTTP/JSON    ┌────────────────────────┐   │
│  │                   │ ──────────────> │                         │   │
│  │   PyQt6 Frontend  │                 │    FastAPI Backend      │   │
│  │  (void_ball.py)   │ <────────────── │    (main.py)           │   │
│  │                   │    Responses    │    Port 8000            │   │
│  └───────────────────┘                 │                         │   │
│                                        │  ┌─────────────────┐   │   │
│                                        │  │  void_agent.py  │   │   │
│                                        │  │  (Intent Router)│   │   │
│                                        │  └────────┬────────┘   │   │
│                                        │           │             │   │
│                                        │     ┌─────┴─────┐      │   │
│                                        │     │  Services  │      │   │
│                                        │     │  (19 cap-  │      │   │
│                                        │     │  abilities)│      │   │
│                                        │     └─────┬─────┘      │   │
│                                        └───────────┼────────────┘   │
│                                                    │                │
│                    ┌───────────────────────────────┼───────┐        │
│                    │                               │       │        │
│              ┌─────┴─────┐              ┌──────────┴───┐   │        │
│              │  Ollama   │              │  PostgreSQL  │   │        │
│              │  (Qwen3   │              │  + pgvector  │   │        │
│              │  + llava) │              │  (RAG Store) │   │        │
│              └───────────┘              └──────────────┘   │        │
│                                                             │        │
└─────────────────────────────────────────────────────────────┘        │
```

### Request Lifecycle

1. **User speaks/types** → captured by PyQt6 frontend
2. **Frontend sends** `POST /agent/query` with raw text
3. **FastAPI routes** to `void_agent.run_agent()`
4. **Agent fetches context** from pgvector memory (relevant memories + recent conversations)
5. **Intent detection** pipeline:
   - Fast keyword matching against 17 service registries
   - Regex pattern matching for memory ops (remember/recall)
   - LLM fallback for ambiguous queries
6. **Service routing** → dynamic import + dispatch to appropriate service
7. **Response formatting** → Tenglish-enriched, formatted for the frontend
8. **Conversation logged** to memory for future context

---

## 🤖 Agent System (`void_agent.py`)

The agent is a **custom LangGraph-style system** — not using LangGraph as a library, but implementing the same pattern manually.

### System Prompt (~500 lines)

The system prompt defines VOID's entire personality:

- **Personality**: Smart, casual, slightly sarcastic, never robotic
- **Language**: Tenglish — natural code-switching (`bro`, `ra`, `kada`, `ga`, `ani`, `undi`, `cheppu`)
- **Forbidden phrases**: "As an AI...", "I cannot...", "Certainly!", "Great question!"
- **Karthik's profile**: Academic details, developer stack, active projects, career status, known mistakes
- **Time-aware behavior**: 6-9AM = brief mode, 9-6PM = work mode, 6-10PM = project mode, 10PM-12AM = wind down, 12AM+ = sleep nagging

### Intent Detection Pipeline

```
User Input
    │
    ├── Fast Keyword Match (17 services)
    │   └── e.g., "weather" → weather_service
    │
    ├── Regex Memory Patterns
    │   ├── "remember that..." → add_memory()
    │   └── "what do you remember about..." → recall_memory()
    │
    ├── Screen/Vision Detection
    │   └── "look at this", "analyze screen" → vision_service
    │
    ├── Git/Commit Detection
    │   └── "commit message" → git_service
    │
    └── LLM Fallback
        └── Asks Qwen to classify → returns JSON {action, reasoning}
```

### Service Registry (17 capabilities)

All registered with keywords and descriptions for both fast matching and LLM fallback:

| Key | Function | Keywords |
|---|---|---|
| `weather` | `weather_service.get_weather` | weather, viza, vishak, rain, temperature |
| `news` | `news_service.get_tech_news_formatted` | tech news, ai lo, what's new, trending |
| `github` | `github_service.get_github_overview` | github, repo, commit, pr, star |
| `leetcode` | `leetcode_service.get_stats_formatted` | leetcode, cp cheyyali, dsa, streak |
| `email` | `gmail_service.check_inbox` | mail, email, inbox, gmail |
| `calendar` | `calendar_service.get_today_schedule` | calendar, schedule, today, events |
| `clipboard` | `clipboard_service.process_clipboard` | clipboard, clip board, copy chesina |
| `focus` | `focus_service.start_focus` | focus, pomodoro, distraction, block |
| `reminder` | `reminder_service.set_reminder` | remind, reminder, remember me, notify |
| `project_status` | `project_tracker.get_project_status` | status, project update, progress, blocker |
| `career` | `career_service.get_application_status` | internship, career, apply, resume, job |
| `hackathon` | `hackathon_service.activate_hackathon_mode` | hackathon, submission, deadline, ship |
| `paper` | `pdf_service.summarize_arxiv` | arxiv, paper, research, pdf |
| `git` | `git_service.check_before_push` | git, commit, push, diff, security, api key |
| `vision` | `vision_service.analyze` | screen, screenshot, vision, look at |

---

## 🚀 Backend (FastAPI)

### `main.py` — The Central Hub

The FastAPI application serves as the command center:

- **3 routers** registered: screen, text, meeting
- **70+ direct endpoints** for all services
- **Startup**: Initializes DB, loads memory, starts background scheduler
- **CORS**: Wide open (`allow_origins=["*"]`)
- **All request models** defined centrally with Pydantic

### Router Structure

#### `screen_router.py` (prefix: `/screen`)
| Endpoint | Method | Description |
|---|---|---|
| `/screen/analyze` | POST | Analyze screenshot with action (suggest/summarize/explain/translate) |
| `/screen/explain` | POST | Explain screen with optional question |
| `/screen/whatsapp-suggest` | POST | Extract WhatsApp chat from screenshot → generate 3 Tenglish replies |
| `/screen/save-screenshot` | POST | Save screenshot to disk + DB log |
| `/screen/screenshots` | GET | List saved screenshots |

#### `text_router.py` (prefix: `/text`)
| Endpoint | Method | Description |
|---|---|---|
| `/text/suggest` | POST | Suggest best next reply from conversation |
| `/text/summarize` | POST | Summarize text content |
| `/text/translate` | POST | Translate between Telugu and English |
| `/text/voice-log` | POST | Log voice transcription |

#### `meeting_router.py` (no prefix)
| Endpoint | Method | Description |
|---|---|---|
| `/meeting/summarize` | POST | Summarize meeting transcription + extract action items |
| `/history/actions` | GET | Recent action logs |
| `/history/voice` | GET | Recent voice transcriptions |
| `/history/meetings` | GET | Past meeting summaries |

### Direct Endpoints in `main.py`

| Method | Route | Service |
|---|---|---|
| GET | `/agent/query` | Full agent (intent + routing) |
| POST | `/agent/simple` | Direct LLM (no routing) |
| GET | `/weather?city=` | WeatherService |
| GET | `/news?count=` | NewsService |
| GET | `/github` | GitHubService |
| GET | `/github/repo/{name}` | GitHubService (specific repo) |
| GET | `/leetcode?username=` | LeetCodeService |
| GET | `/email/inbox?limit=` | GmailService |
| POST | `/email/read` | GmailService (read specific email) |
| POST | `/email/reply` | GmailService (draft reply) |
| GET | `/calendar/today` | CalendarService |
| GET | `/calendar/week` | CalendarService (week overview) |
| POST | `/calendar/add` | CalendarService (add event) |
| POST | `/focus/start` | FocusService |
| GET | `/focus/status` | FocusService |
| POST | `/focus/end` | FocusService |
| POST | `/reminder/set` | ReminderService |
| GET | `/reminder/list` | ReminderService |
| GET | `/project/{name}` | ProjectTracker |
| POST | `/project/update` | ProjectTracker |
| GET | `/projects` | ProjectTracker (all) |
| GET | `/career/applications` | CareerService |
| POST | `/career/track` | CareerService |
| POST | `/career/analyze-jd` | CareerService |
| GET | `/career/platforms` | CareerService |
| POST | `/hackathon/start` | HackathonService |
| GET | `/hackathon/status` | HackathonService |
| POST | `/hackathon/end` | HackathonService |
| GET | `/git/security-check` | GitService |
| GET | `/git/commit-message` | GitService |
| POST | `/paper/summarize` | PDFService |
| POST | `/clipboard/analyze` | ClipboardService |
| POST | `/voice/transcribe` | VoiceService |
| POST | `/voice/speak` | VoiceService |
| GET | `/brief/morning` | Scheduler (morning brief) |
| GET | `/brief/digest` | Scheduler (daily digest) |
| GET | `/health` | Health check |
| GET | `/` | Root info |

---

## 📦 Services Breakdown

### Core AI Services

#### `ollama_service.py` — LLM Gateway
- **Model**: Qwen3:8b (configurable via `OLLAMA_MODEL`)
- **Features**: Both synchronous and streaming responses
- **System prompt**: Default Tenglish personality
- **Error handling**: Requires Ollama running; returns `"ERROR: ..."` prefix on failure
- **Timeout**: 120 seconds for long generations

#### `vision_service.py` — Screen Understanding
- **Model**: llava (configurable via `VISION_MODEL`)
- **Actions**: suggest, summarize, explain, translate
- **Custom prompts**: Each action has a tailored system prompt
- **WhatsApp pipeline**: Extract chat from screenshot → generate Tenglish replies
- **Error handling**: Checks `ollama serve` is running before making requests

#### `embedding_service.py` — Vector Embeddings
- **Model**: nomic-embed-text (configurable via `EMBED_MODEL`)
- **Simple**: Single `embed(text)` function → returns 768-dim vector
- **Used by**: `memory_service.py` for RAG

#### `memory_service.py` — pgvector RAG
- **Vector dimension**: 768 (nomic-embed-text)
- **Tables**: `conversations`, `memories`, `action_logs`
- **Operations**:
  - `add_conversation()` — Log user-assistant pairs
  - `get_recent_conversations()` — Last N conversations
  - `add_memory()` — Store with embedding + category + importance
  - `search_memories()` — Cosine similarity via `<=>` operator
  - `get_context_for_query()` — Combined memories + history for agent context
  - `log_action()` — Audit trail for all agent actions
- **Graceful degradation**: Returns empty results if PostgreSQL is unavailable

### Productivity Services

#### `focus_service.py` — Pomodoro Timer
- Default 25-minute sessions (configurable)
- In-memory session tracking (lost on restart)
- Auto-log memory on session completion
- Time-of-day suggestions (morning = deep work, night = wind down)

#### `reminder_service.py` — Desktop Notifications
- Natural language time parsing via `dateutil.parser`
- Desktop notifications via `plyer`
- Threading-based timers
- Persistent memory logging

#### `hackathon_service.py` — Timed Hackathon Mode
- Countdown timer with auto-warnings at: halfway, 3h, 1h, 15min, deadline
- Progress bar visualization (`████▒▒▒▒▒ 40%`)
- Knowledge of past hackathons (Hack2Skill, DevNetwork)
- Memory logging at start/end/progress checks

### Communication Services

#### `gmail_service.py` — Email Intelligence
- **OAuth 2.0** authentication with Google
- **Smart categorization**: Urgent, Internship, Hackathon, Academic, Notification, Newsletter
- **Priority sorting**: Urgent emails first
- **Reply drafting**: Creates replies in thread context
- **Recruiter follow-up detection**: Finds unanswered recruiter emails >24h old

#### `calendar_service.py` — Google Calendar
- **Operations**: Today's schedule, week overview, add events
- **Conflict detection**: Finds overlapping events
- **Focus block suggestions**: Recommends free time gaps between events
- **OAuth**: Shares token with Gmail service

### Data Services

#### `weather_service.py` — OpenWeatherMap
- Metric units, Telugu-friendly city defaults
- Emoji-mapped conditions (☀️ clear, 🌧️ rain, ⛈️ thunder)
- Short one-liner for daily briefs

#### `news_service.py` — Tech News Aggregator
- **Sources**: Hacker News (top stories), Dev.to (trending), NewsAPI (AI/ML query)
- 30-minute cache to avoid rate limiting
- Deduplication across sources

#### `github_service.py` — GitHub Activity
- **Cached**: 10-minute TTL
- **Tracks**: Public events, recent commits, PRs, stars on known repos
- **Known repos**: Memoir, Cognitus, DevCollab, VOID, Aegis, AI-Resume-Ranker

#### `leetcode_service.py` — LeetCode Tracker
- **Cache**: 1-hour TTL
- **Stats**: Total solved, Easy/Medium/Hard breakdown, acceptance rate, streak
- **Source**: leetcode-stats-api (public)

### Developer Services

#### `git_service.py` — Security & Commits
- **Secret patterns detected**:
  - OpenAI keys (`sk-...`)
  - Google API keys (`AIza...`)
  - Groq keys (`gsk_...`)
  - GitHub tokens (`ghp_...`, `gho_...`)
  - AWS keys (`AKIA...`)
  - Private keys (RSA, SSH, OpenSSH)
  - JWT tokens
  - Stripe keys
  - Generic secrets via pattern matching
- **Sensitive files check**: `.env`, `credentials.json`, `*.pem`, `*.key`
- **Commit message generation**: Conventional commits via LLM

#### `clipboard_service.py` — Clipboard AI
- **Content type detection**: error, arxiv, url, job_description, code, text
- **Auto-routing**: Error → debug, arXiv → summarize, JD → match analysis, code → explain
- **Smart pattern matching**: URL extraction, code detection, JD keyword scoring

#### `pdf_service.py` — Paper & Article Summarizer
- **arXiv**: Extracts title + abstract from HTML, then LLM summary
- **Articles**: Extracts text from `<p>` tags, then LLM summary
- **Local PDFs**: Uses `pymupdf` for text extraction

### Career & Project Services

#### `career_service.py` — Internship Tracker
- **Application tracking**: Stored in memory with company, role, status, date
- **Status aggregation**: Applied, Interview, Rejected, Offer counts
- **JD analysis**: Match scoring (1-10), skill gap analysis, project recommendations
- **Email drafting**: Cold email + follow-up templates
- **Platform recommendations**: Internshala, Unstop, LinkedIn, WellFound, YC

#### `project_tracker.py` — Project Status
- **6 known projects**: VOID, Memoir, Cognitus, DevCollab, Aegis, AI-Resume-Ranker
- **Fields**: status, pending, blocker, next_action
- **Fuzzy matching**: Partial name matching for project lookup
- **Memory-backed**: All status stored and retrieved from pgvector

#### `voice_service.py` — Speech I/O
- **ASR**: faster-whisper with Telugu language detection
- **TTS**: pyttsx3 with configurable voice (male/female)
- **Voice formatting**: Removes markdown, bullet symbols, emoji prefixes for natural speech

---

## 🖥️ Frontend (`void_ball.py`)

A **PyQt6 desktop widget** with glassmorphism design. Key features:

- **Floating ball**: Circular, glowing, draggable widget that stays on top
- **Radial menu**: Context-sensitive actions around the ball
- **Hotkey**: `Alt+Space` to summon from anywhere
- **Voice capture**: Records microphone → sends to Whisper for transcription
- **Screenshot capture**: Captures screen → sends to vision service
- **Chat interface**: Persistent conversation UI
- **System tray**: Background operation with tray icon

---

## 💾 Database

### Primary: PostgreSQL + pgvector
- **Purpose**: Persistent RAG memory with vector search
- **Schema**: 6 tables defined in `models.py`
- **Connection**: Lazy — created on first use, not at import time
- **Graceful fallback**: If PG is down, services return empty results

### Schema

```sql
-- Action audit trail
CREATE TABLE action_logs (
    id SERIAL PRIMARY KEY,
    action VARCHAR(50),
    input_text TEXT,
    output_text TEXT,
    language VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Screenshot archive
CREATE TABLE screenshots (
    id SERIAL PRIMARY KEY,
    filepath TEXT,
    folder VARCHAR(255),
    context VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Voice transcription log
CREATE TABLE voice_logs (
    id SERIAL PRIMARY KEY,
    transcription TEXT,
    language VARCHAR(20),
    action_taken VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Meeting summary storage
CREATE TABLE meeting_logs (
    id SERIAL PRIMARY KEY,
    transcription TEXT,
    summary TEXT,
    action_items TEXT,
    duration_secs INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversation history (for agent context)
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_message TEXT,
    assistant_response TEXT,
    context TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vector memory store (RAG)
CREATE TABLE memories (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding VECTOR(768),        -- nomic-embed-text dimension
    category VARCHAR(50),
    importance INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Actual State
A `void_memory.db` (SQLite) file exists in the project root, suggesting the actual running instance uses SQLite as a fallback since PostgreSQL + pgvector may not be available on the current machine.

---

## ⏰ Scheduler (`scheduler.py`)

Background thread that runs alongside the FastAPI server.

### Scheduled Jobs

| Job | Time (IST) | Description |
|---|---|---|
| 🌅 **Morning Brief** | 8:00 AM | Weather + schedule + email + GitHub + LeetCode + daily tip |
| 🌙 **Daily Digest** | 10:00 PM | What was built + LeetCode + sessions + tomorrow's weather |
| 💪 **LeetCode Streak Check** | 9:00 PM | Reminds if streak is broken |

### Morning Brief Components
1. Weather (short) — `weather_service`
2. Today's Schedule — `calendar_service`
3. Email Summary — `gmail_service` (urgent count + unread count)
4. GitHub Activity — `github_service`
5. Tech News (top 3) — `news_service`
6. LeetCode Stats — `leetcode_service`
7. Today's Priority — `focus_service.suggest_pomodoro()`
8. Dev Tip (rotated daily based on day of month)

### Daily Digest Components
1. Code changes detected (from git diff)
2. GitHub activity
3. LeetCode progress
4. Today's schedule
5. Completed sessions
6. Tomorrow's weather
7. Prep list for tomorrow

---

## ⚙️ Configuration (`config.py`)

All configuration via environment variables with sensible defaults:

```env
# ── LLM ──
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
VISION_MODEL=llava
EMBED_MODEL=nomic-embed-text

# ── Database ──
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/void

# ── External APIs ──
OPENWEATHER_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here
GITHUB_TOKEN=your_token_here

# ── Google OAuth ──
GOOGLE_CLIENT_SECRET_PATH=./credentials.json
GOOGLE_TOKEN_PATH=./token.json

# ── User Profile ──
USER_NAME=Karthik
USER_GITHUB=MKarthik730
USER_GITHUB_SECONDARY=kakashi754-ui
USER_COLLEGE=ANITS Visakhapatnam
USER_BRANCH=CSE
USER_YEAR=2nd Year, 5th Semester
USER_GRADUATION=2028
USER_CGPA=9.0+
USER_TIMEZONE=Asia/Kolkata

# ── Defaults ──
DEFAULT_CITY=Visakhapatnam
LEETCODE_USERNAME=MKarthik730
WHISPER_MODEL=base
TTS_VOICE=male
```

---

## 🔒 Security & Error Handling

### Security Features

1. **Git Secret Scanning** (`git_service.py`): Detects 12+ types of API keys/tokens/secrets in diffs
2. **Pre-push Warnings**: Blocks pushes that expose sensitive files (`.env`, `credentials.json`)
3. **Key Rotation Reminders**: Built into system prompt
4. **No Hardcoded Keys**: All credentials via environment variables

### Error Handling Philosophy

Every service is designed to **never crash the app**:

- **Database**: Lazy connection; returns empty results if unavailable
- **External APIs**: Timeouts with fallback messages in Tenglish
- **LLM Errors**: Returns "ERROR: ..." prefix → agent formats friendly message
- **File Operations**: Try/except with descriptive error messages
- **Missing Dependencies**: Checks imports, returns install instructions

### Example Fallbacks

| Failure | User Sees |
|---|---|
| PostgreSQL down | Services work without memory persistence |
| Ollama not running | "Ollama is not running. Start with 'ollama serve'" |
| Weather API key missing | "Weather fetch avvaledhu bro — API key or network issue" |
| Gmail auth missing | "credentials.json ledhu bro — ..." |
| Any service error | "Sorry bro — [service] lo issue vachindi. [error]" |

---

## 🔑 Key Observations & Potential Issues

### ✅ Strengths

1. **Deep personalization**: Everything from system prompt to feature set is tailored to Karthik's specific needs
2. **Local-first**: No cloud dependency for core AI (all via Ollama)
3. **Graceful degradation**: Every failure mode has a friendly Tenglish message
4. **Comprehensive**: 19+ integrated services covering dev, productivity, career, communication
5. **Security-aware**: Secret scanning, key rotation reminders, git pre-push checks
6. **Consistent personality**: Tenglish throughout, never breaks character
7. **Well-modularized**: Clean separation into routers, services, agent

### ⚠️ Potential Issues

1. **Database inconsistency**
   - `main.py` claims "PostgreSQL + pgvector" on startup
   - `config.py` defaults to PostgreSQL connection string
   - But `void_memory.db` (SQLite) exists in project root — suggests PG isn't running
   - The lazy connection code tries PG, fails silently, and services return empty

2. **In-memory state is volatile**
   - Focus sessions, reminders, hackathons use Python dicts
   - All lost on server restart
   - Only memories and conversations persist via DB

3. **No authentication**
   - CORS allows all origins (`allow_origins=["*"]`)
   - No API keys, JWT, or session auth on any endpoint

4. **Many external dependencies**
   - Requires Ollama (Qwen3:8b + llava + nomic-embed-text) running locally
   - Google OAuth for Gmail + Calendar
   - OpenWeatherMap API key for weather
   - NewsAPI key for enriched news
   - GitHub token for authenticated API calls
   - PyQt6 for frontend (only on desktop)
   - faster-whisper (heavy model download)
   - plyer for desktop notifications (platform-dependent)

5. **Monolithic frontend**
   - `void_ball.py` is a single large file handling UI, hotkeys, audio, screenshots, API calls
   - No separation of concerns within the frontend

6. **RAG depends on pgvector**
   - Vector search requires PostgreSQL with `pgvector` extension
   - Without it, memory search returns empty results silently
   - The `database.py` attempts `CREATE EXTENSION IF NOT EXISTS vector` but fails silently

7. **Limited testing**
   - No test files found in the project
   - No CI/CD configuration

8. **Rate limiting**
   - Some services have caching (GitHub: 10min, LeetCode: 1h, News: 30min)
   - But no explicit rate limiting middleware on the FastAPI side

---

## 🚀 Setup Guide

### Prerequisites

```bash
# 1. Install Ollama
# Windows: winget install Ollama.Ollama
# macOS/Linux: curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pull models
ollama pull qwen3:8b         # LLM (or qwen2.5:3b)
ollama pull llava            # Vision
ollama pull nomic-embed-text # Embeddings

# 3. Start Ollama
ollama serve
```

### Backend Setup

```bash
cd project/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Optional: PostgreSQL + pgvector
# (Requires PostgreSQL server with pgvector extension)

# Create .env file with your API keys

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

```bash
cd project/frontend

# Ensure PyQt6 is installed
pip install PyQt6 pyautogui pillow sounddevice scipy

# Launch the floating ball
python void_ball.py
```

### API Keys (Optional — services work without them)

| Service | Key | Where to Get |
|---|---|---|
| Weather | `OPENWEATHER_API_KEY` | https://openweathermap.org/api |
| News | `NEWSAPI_KEY` | https://newsapi.org/register |
| GitHub | `GITHUB_TOKEN` | GitHub Settings → Developer Settings → Personal Access Tokens |
| Gmail + Calendar | Google OAuth `credentials.json` | Google Cloud Console → APIs & Services → Credentials |

---

## 📊 Stats Summary

| Metric | Count |
|---|---|
| Python files | 27 |
| API endpoints | 70+ |
| Services | 19 |
| Router modules | 3 |
| Database tables | 6 |
| External API integrations | 8 (Ollama, OpenWeatherMap, NewsAPI, GitHub, LeetCode, Gmail, Google Calendar, plyer) |
| Secret patterns detected | 12+ |
| Known projects tracked | 6 |
| Lines of code (backend) | ~4,000+ |
| Lines of code (frontend) | ~1,500+ |
| Total dataset topics | 130+ |

---

## 🎯 Bottom Line

VOID is an **impressively complete, production-grade AI assistant** built by a solo developer. It's deeply personalized for Karthik, has excellent error handling with graceful degradation, covers a massive feature surface, and maintains a consistent personality throughout. The architecture is well-modularized with clean separation between routers, services, and the agent core.

The main friction points are: (1) the PostgreSQL dependency that may not be available, (2) the number of third-party API keys needed for full functionality, and (3) the monolithic PyQt6 frontend that could benefit from modularization.

---

*Documentation generated from codebase analysis — July 2026*
