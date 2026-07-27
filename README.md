
## VOID — AI Screen Assistant + Project Scaffolder
> A floating AI desktop assistant that reads your screen, understands Telugu, scaffolds full projects, manages files, and helps you reply, summarize, translate, and draft — powered entirely by local models

<p align="center">
  <img src="assets/void_logo.svg" width="280" alt="VOID" style="margin-bottom: 20px;">
</p>

## VOID — AI Screen Assistant
> A floating AI desktop assistant that reads your screen, understands Telugu, and helps you reply, summarize, translate, and draft — powered entirely by local models.

---

## Overview

VOID runs as a frameless floating widget on your Windows desktop. It uses **Qwen3:8b** (via Ollama, CPU-only) for all text tasks and **llava** for screen understanding. No cloud LLM dependency for text generation — everything runs on your machine.

New in v3.0: **Actual LangGraph StateGraph** agent with real tool-calling, **file management** (sandboxed project workspace), and **AI project scaffolding** — describe what you want to build and VOID generates the full file structure with idiomatic boilerplate.

---

## Features

| Action | Description |
|---|---|
| LangGraph StateGraph | Real multi-step graph with tool-calling nodes (not just keyword routing) |
| Project Scaffolding | "Create a FastAPI project called expense-tracker" — generates full structure |
| File Management | Create, read, write, delete, move files in a sandboxed workspace |
| WhatsApp Reply | Captures chat, generates 3 Tenglish suggestions via Ollama Vision |
| Screenshot | Saves PNG to `~/Pictures/VOID/` |
| Voice Type | Transcribes mic via Whisper, types into active window |
| Explain Screen | Analyzes screen with local vision model (llava/moondream) |
| Translate | Extracts and translates on-screen text |
| Summarize | Summarizes screen content |
| Email Draft | Voice note to professional email |
| Ask VOID | Persistent chat with memory across sessions (pgvector RAG) |
| Alt+Space Hotkey | Summon VOID from anywhere |

---

## Architecture

```
void/
├── project/
│   ├── backend/
│   │   ├── main.py                  # FastAPI + LangGraph StateGraph
│   │   ├── config.py               # Environment configuration (19+ services)
│   │   ├── agent/
│   │   │   ├── __init__.py         # Exports run_agent, run_simple, get_graph
│   │   │   └── void_agent.py       # REAL LangGraph StateGraph + 19 tool wrappers
│   │   ├── routers/
│   │   │   ├── screen_router.py    # /screen/* endpoints
│   │   │   ├── text_router.py      # /text/* endpoints
│   │   │   ├── meeting_router.py   # /meeting/*, /history/* endpoints
│   │   │   └── file_router.py      # /files/* endpoints (NEW)
│   │   └── services/
│   │       ├── ollama_service.py   # Qwen3:8b via Ollama
│   │       ├── vision_service.py   # llava via Ollama
│   │       ├── memory_service.py   # pgvector RAG memory
│   │       ├── file_service.py     # Sandboxed file ops (NEW)
│   │       ├── project_scaffold_service.py  # AI scaffold planner (NEW)
│   │       └── ... (15 more services)
│   └── frontend/
│       └── void_ball.py            # PyQt6 glassmorphism UI
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent | LangGraph StateGraph — real graph with 5 nodes + conditional edges |
| Tools | langchain-core @tool decorators (19 tool wrappers) |
| LLM | Qwen3:8b via Ollama (local) |
| Vision | Ollama llava or moondream (local) |
| Memory | pgvector RAG — persistent context + vector search |
| ASR | faster-whisper (local) |
| TTS | pyttsx3 |
| Backend | FastAPI + Pydantic + SQLAlchemy |
| Frontend | PyQt6 with glassmorphism |
| File Workspace | Sandboxed to `~/VOID_Projects` by default |

---

## Setup

### 1. Prerequisites

```bash
# Install Ollama
winget install Ollama.Ollama

# Pull models
ollama pull qwen3:8b
ollama pull llava
ollama pull nomic-embed-text
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Ollama (in separate terminal)

```bash
ollama serve
```

### 4. Start backend

```bash
cd project/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Start frontend

```bash
cd project/frontend
python void_ball.py
```

---

## API Endpoints

### Agent
| Method | Route | Description |
|---|---|---|
| POST | `/agent/query` | LangGraph StateGraph agent (intent detection → routing → response) |
| POST | `/agent/simple` | Direct LLM query (no agent routing) |

### Screen / Vision
| Method | Route | Description |
|---|---|---|
| POST | `/screen/analyze` | Analyze screenshot with action (suggest/summarize/explain/translate) |
| POST | `/screen/explain` | Explain screen content with optional question |
| POST | `/screen/whatsapp-suggest` | Extract WhatsApp chat → generate 3 Tenglish replies |
| POST | `/screen/save-screenshot` | Save screenshot to disk |
| GET | `/screen/screenshots` | List saved screenshots |

### Text
| Method | Route | Description |
|---|---|---|
| POST | `/text/suggest` | Suggest best next reply from conversation |
| POST | `/text/summarize` | Summarize text content |
| POST | `/text/translate` | Translate between Telugu and English |
| POST | `/text/voice-log` | Log voice transcription |

### Files & Project Scaffolding (NEW)
| Method | Route | Description |
|---|---|---|
| POST | `/files/plan` | Generate project scaffold plan (dry run) — returns requires_confirmation |
| POST | `/files/execute` | Execute a previously returned scaffold plan |
| POST | `/files/create-file` | Create a new file (never requires confirmation) |
| POST | `/files/write-file` | Write/overwrite/append to a file |
| POST | `/files/delete-file` | Soft-delete a file (moves to .void_trash) |
| POST | `/files/move-file` | Move or rename a file |
| POST | `/files/list` | List files/directories in a workspace path |
| POST | `/files/mkdir` | Create a directory |
| POST | `/files/restore-from-trash` | Restore a file from .void_trash |

### External APIs
| Method | Route | Description |
|---|---|---|
| GET | `/weather` | Current weather (default: Visakhapatnam) |
| GET | `/news` | Latest tech news |
| GET | `/github` | GitHub activity overview |
| GET | `/github/repo/{name}` | Specific repo status |
| GET | `/leetcode` | LeetCode stats |
| GET | `/email/inbox` | Gmail inbox (categorized by priority) |
| GET | `/email/read` | Read a specific email |
| POST | `/email/reply` | Draft and send a reply |
| GET | `/calendar/today` | Today's schedule |
| GET | `/calendar/week` | Week overview |
| POST | `/calendar/add` | Add calendar event |

### Productivity
| Method | Route | Description |
|---|---|---|
| POST | `/focus/start` | Start focus/pomodoro session |
| GET | `/focus/status` | Focus session status |
| POST | `/focus/end` | End focus session |
| POST | `/reminder/set` | Set a reminder |
| GET | `/reminder/list` | List all reminders |
| POST | `/hackathon/start` | Activate hackathon countdown |
| GET | `/hackathon/status` | Hackathon mode status |
| POST | `/hackathon/end` | End hackathon mode |

### Career & Projects
| Method | Route | Description |
|---|---|---|
| GET | `/career/applications` | All tracked applications |
| POST | `/career/track` | Track a new application |
| POST | `/career/analyze-jd` | Analyze job description |
| GET | `/career/platforms` | Recommended platforms |
| GET | `/projects` | All project summaries |
| GET | `/project/{name}` | Specific project status |
| POST | `/project/update` | Update project status |

### Utilities
| Method | Route | Description |
|---|---|---|
| POST | `/paper/summarize` | Summarize arXiv paper or article |
| POST | `/clipboard/analyze` | Analyze clipboard content (detect type + AI) |
| GET | `/git/security-check` | Check git diff for API key leaks |
| GET | `/git/commit-message` | Generate commit message from diff |
| POST | `/voice/transcribe` | Transcribe audio file |
| POST | `/voice/speak` | Speak text via TTS |
| GET | `/brief/morning` | Morning brief |
| GET | `/brief/digest` | Evening daily digest |
| GET | `/meeting/summarize` | Summarize meeting transcription |

### System
| Method | Route | Description |
|---|---|---|
| GET | `/health` | Service status (all integrations) |
| GET | `/` | Root info |

---

## Configuration

Create `project/backend/.env`:

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
VISION_MODEL=llava
EMBED_MODEL=nomic-embed-text

# File workspace (sandboxed project directory)
FILE_WORKSPACE_ROOTS=~/VOID_Projects

# External APIs (optional)
OPENWEATHER_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here
GITHUB_TOKEN=your_token_here

# Google OAuth (for Email + Calendar)
GOOGLE_CLIENT_SECRET_PATH=./credentials.json
GOOGLE_TOKEN_PATH=./token.json

# User profile
USER_NAME=Karthik
USER_GITHUB=MKarthik730
DEFAULT_CITY=Visakhapatnam
```

---

## File Management & Confirmation Gating

VOID's file service runs in a **sandboxed workspace** (`~/VOID_Projects` by default).

- **Create operations** (create_file, mkdir) in new paths never require confirmation
- **Destructive operations** (delete_file, overwrite existing file, move_file that overwrites) return `requires_confirmation: true`
- The PyQt6 frontend shows a confirm dialog before hitting `/files/execute` when `requires_confirmation` is true
- All deleted files go to `.void_trash` for recovery
- Path traversal is blocked — any path resolving outside workspace roots is rejected

### Typical Flow

```
User: "create a FastAPI project called expense-tracker"
  → POST /agent/query → LangGraph detects "scaffold" intent
  → plan_scaffold_node generates plan via LLM
  → If destructive: returns plan + asks user to confirm
  → If clean create: auto-executes and reports result

User confirms:
  → POST /files/execute with plan from /files/plan
  → Returns results per step
```

---

## Dependencies

- [LangGraph](https://langchain-ai.github.io/langgraph/) — StateGraph agent framework
- [langchain-core](https://python.langchain.com/) — @tool decorators for tool binding
- [Ollama](https://ollama.ai) — Local LLM + vision hosting
- [Qwen3](https://huggingface.co/Qwen) — Default LLM model
- [llava](https://llava-vl.github.io/) — Vision model
- [nomic-embed-text](https://ollama.ai/library/nomic-embed-text) — Embeddings model
- [PyQt6](https://pypi.org/project/PyQt6/) — Desktop UI framework
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — Speech-to-text

---

*VOID — local-first AI assistant for Telugu users. Ship fast, stay local, speak Tenglish.* 🚀

