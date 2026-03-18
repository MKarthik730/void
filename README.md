<p align="center">
  <img src="assets/void_logo.svg" width="180" alt="VOID">
</p>

# VOID — AI Screen Assistant
> A floating AI desktop assistant that reads your screen, understands Telugu, and helps you reply, summarize, translate, and draft — powered entirely by local models.

---

## Overview

VOID runs as a frameless floating widget on your Windows desktop. It uses **Qwen2.5-3B** (GGUF, CPU-only) for all text tasks and **Groq Vision** for screen understanding. No cloud LLM dependency for text generation — everything runs on your machine.

---

## Features

| Action | Description |
|---|---|
| WhatsApp Reply | Captures the active chat, extracts messages, generates 3 Tenglish reply suggestions |
| Screenshot | Saves a timestamped PNG to `~/Pictures/VOID/` |
| Voice Type | Transcribes mic input via Whisper and types it into the active window |
| Explain Screen | Sends a screenshot to Groq Vision for full content explanation |
| Translate | Extracts and translates on-screen text to English |
| Summarize | Summarizes screen content into bullet points |
| Email Draft | Converts a voice note into a structured professional email |
| Ask VOID | Persistent chat window backed by Qwen |

---

## Architecture

```
void/
├── project/
│   ├── backend/
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── config.py                # Loads .env, exports constants
│   │   ├── database.py              # SQLAlchemy engine + session
│   │   ├── models.py                # ORM models (ActionLog, VoiceLog, etc.)
│   │   ├── routers/
│   │   │   ├── text_router.py       # POST /text/*
│   │   │   ├── screen_router.py     # POST /screen/*
│   │   │   └── meeting_router.py    # POST /meeting/*, GET /history/*
│   │   └── services/
│   │       ├── qwen_service.py      # llama-cpp-python wrapper for Qwen
│   │       └── gemini_service.py    # Groq Vision API client
│   └── frontend/
│       └── void_ball.py             # PyQt5 floating HUD
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Qwen2.5-3B-Instruct Q4\_K\_M (GGUF) via llama-cpp-python, CPU only |
| Vision | Groq API — llama-4-scout-17b-16e-instruct |
| ASR | OpenAI Whisper tiny, runs locally |
| TTS | pyttsx3 |
| Backend | FastAPI, SQLAlchemy, PostgreSQL, psycopg2 |
| Frontend | PyQt5, pyautogui, Pillow |

---

## Requirements

- Windows 10/11
- Python 3.12
- PostgreSQL running locally
- Qwen2.5-3B GGUF model file
- Groq API key — free tier at [console.groq.com](https://console.groq.com)

---

## Setup

### 1. Clone

```bash
git clone https://github.com/MKarthik730/void.git
cd void/project
```

### 2. Backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Frontend dependencies

```bash
pip install PyQt5 pyautogui pyttsx3 openai-whisper sounddevice scipy requests Pillow
```

### 4. Download the model

Get `qwen2.5-3b-instruct-q4_k_m.gguf` from HuggingFace and place it at:

```
D:\models\qwen2.5-3b-instruct-q4_k_m.gguf
```

Update `QWEN_GGUF_PATH` in `.env` if you use a different path.

### 5. Configure environment

Create `project/backend/.env`. Do not commit this file.

```env
QWEN_GGUF_PATH=D:\models\qwen2.5-3b-instruct-q4_k_m.gguf
GROQ_API_KEY=your_groq_key_here

POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=void
```

### 6. Database setup

```sql
CREATE DATABASE void;
GRANT ALL ON SCHEMA public TO postgres;
ALTER SCHEMA public OWNER TO postgres;
```

### 7. Start the backend

```bash
cd project/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 8. Start the frontend

```bash
cd project/frontend
python void_ball.py
```

---

## API Reference

| Method | Route | Description |
|---|---|---|
| POST | `/text/suggest` | Generate a reply from input text |
| POST | `/text/summarize` | Summarize input text |
| POST | `/text/translate` | Translate between Telugu and English |
| POST | `/text/voice-log` | Persist a voice transcription |
| POST | `/screen/analyze` | Screenshot analysis — suggest, summarize, or translate |
| POST | `/screen/explain` | Deep explanation of screenshot via Groq Vision |
| POST | `/screen/whatsapp-suggest` | Extract chat from screenshot, return Tenglish replies |
| POST | `/screen/save-screenshot` | Write screenshot PNG to disk |
| POST | `/meeting/summarize` | Summarize meeting transcript, extract action items |
| GET | `/history/actions` | Last N action logs |
| GET | `/history/voice` | Last N voice transcription logs |
| GET | `/history/meetings` | Last N meeting summaries |
| GET | `/health` | Service health and model status |

Full interactive docs at `http://localhost:8000/docs`.

---

## WhatsApp Reply — How It Works

1. Open WhatsApp Desktop to an active chat
2. Click the WhatsApp button on the VOID ball
3. Click **SCAN WHATSAPP CHAT**
4. VOID hides, takes a screenshot, re-shows
5. Groq Vision extracts the last few messages
6. Qwen generates 3 context-aware Tenglish replies
7. Click a reply — VOID focuses WhatsApp, pastes, and sends

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `QWEN_GGUF_PATH` | Absolute path to the GGUF model file | `D:\models\qwen2.5-3b-instruct-q4_k_m.gguf` |
| `GROQ_API_KEY` | Groq API key for vision inference | required |
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | required |
| `POSTGRES_HOST` | Database host | `localhost` |
| `POSTGRES_PORT` | Database port | `5432` |
| `POSTGRES_DB` | Database name | `void` |

---

## Notes

- `.env` must be in `.gitignore`. Never push API keys or passwords.
- Qwen runs fully on CPU. 4-8 GB RAM is sufficient for the Q4 quantized model.
- Whisper `tiny` prioritizes speed. Switch to `base` or `small` for better accuracy at the cost of load time.
- Groq free tier enforces per-minute rate limits. If vision calls fail, wait 30-60 seconds and retry.
- The WhatsApp auto-send clicks at the bottom-center of the screen. Keep the WhatsApp input box in its default position.

---

## Dependencies

- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
- [Qwen2.5](https://huggingface.co/Qwen)
- [Groq](https://console.groq.com)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [FastAPI](https://fastapi.tiangolo.com)
- [PyQt5](https://pypi.org/project/PyQt5/)

---

*VOID — local-first AI assistant for Telugu users.*