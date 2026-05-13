
## VOID — AI Screen Assistant
> A floating AI desktop assistant that reads your screen, understands Telugu, and helps you reply, summarize, translate, and draft — powered entirely by local models
<p align="center">
  <img src="assets/void_logo.svg" width="280" alt="VOID" style="margin-bottom: 20px;">
</p>
.

---

## Overview

VOID runs as a frameless floating widget on your Windows desktop. It uses **Qwen2.5-3B** (GGUF, CPU-only) for all text tasks and **Groq Vision** for screen understanding. No cloud LLM dependency for text generation — everything runs on your machine.

---

## Features

| Action | Description |
|---|---|
| LangGraph Agent | Multi-step task planning and execution |
| WhatsApp Reply | Captures chat, generates 3 Tenglish suggestions via Ollama Vision |
| Screenshot | Saves PNG to `~/Pictures/VOID/` |
| Voice Type | Transcribes mic via Whisper, types into active window |
| Explain Screen | Analyzes screen with local vision model (llava/moondream) |
| Translate | Extracts and translates on-screen text |
| Summarize | Summarizes screen content |
| Email Draft | Voice note to professional email |
| Ask VOID | Persistent chat with memory across sessions |
| Alt+Space Hotkey | Summon VOID from anywhere |

---

## Architecture

```
void/
├── project/
│   ├── backend/
│   │   ├── main.py                  # FastAPI + LangGraph agent
│   │   ├── config.py               # Environment configuration
│   │   ├── agent/
│   │   │   └── void_agent.py       # LangGraph agentic core
│   │   └── services/
│   │       ├── ollama_service.py   # Ollama LLM client
│   │       ├── vision_service.py   # Local vision (llava/moondream)
│   │       └── memory_service.py   # SQLite RAG memory
│   └── frontend/
│       └── void_ball.py            # PyQt6 glassmorphism UI
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent | LangGraph 0.0.x — multi-step planning |
| LLM | Qwen2.5 via Ollama (local) |
| Vision | Ollama llava or moondream (local) |
| Memory | SQLite RAG — persistent context |
| ASR | OpenAI Whisper tiny (local) |
| TTS | pyttsx3 |
| Backend | FastAPI + Pydantic |
| Frontend | PyQt6 with glassmorphism |

---

## Setup

### 1. Prerequisites

```bash
# Install Ollama
winget install Ollama.Ollama

# Pull models
ollama pull qwen2.5:3b
ollama pull llava
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

| Method | Route | Description |
|---|---|---|
| POST | `/agent/query` | LangGraph agent (multi-step planning) |
| POST | `/agent/simple` | Direct LLM query |
| POST | `/vision/analyze` | Analyze screenshot |
| POST | `/vision/explain` | Explain screen content |
| POST | `/vision/whatsapp-suggest` | Generate WhatsApp replies |
| POST | `/vision/save-screenshot` | Save screenshot |
| GET | `/memory/history` | Conversation history |
| GET | `/memory/actions` | Action history |
| POST | `/memory/remember` | Store important fact |
| POST | `/memory/recall` | Retrieve relevant memories |
| GET | `/health` | Service status |

---

## Configuration

Create `project/backend/.env`:

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
VISION_MODEL=llava
SCREENSHOTS_ROOT=C:\Users\You\Pictures\VOID
```

---

## Dependencies

- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [Ollama](https://ollama.ai)
- [Qwen2.5](https://huggingface.co/Qwen)
- [llava](https://llava-vl.github.io/)
- [PyQt6](https://pypi.org/project/PyQt6/)
- [OpenAI Whisper](https://github.com/openai/whisper)

---

*VOID — local-first AI assistant for Telugu users.*
```

