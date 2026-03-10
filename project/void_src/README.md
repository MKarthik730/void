# ◈ VOID — AI Screen Assistant

> A floating AI ball that sits on your screen, reads it, speaks to you, and helps you reply, summarize, translate, and understand anything — powered by your fine-tuned Telugu Mistral model + Gemini Vision.

---

## Project Structure

```
VOID_Project/
│
├── backend/                        ← FastAPI server
│   ├── main.py                     ← App entry point, registers routers
│   ├── config.py                   ← All settings loaded from .env
│   ├── database.py                 ← PostgreSQL connection (SQLAlchemy)
│   ├── models.py                   ← DB tables: action_logs, screenshots, voice_logs, meeting_logs
│   ├── .env                        ← API keys and config (edit this!)
│   ├── requirements.txt
│   ├── routers/
│   │   ├── text_router.py          ← /text/suggest, /text/summarize, /text/translate, /text/voice-log
│   │   ├── screen_router.py        ← /screen/analyze, /screen/explain, /screen/save-screenshot
│   │   └── meeting_router.py       ← /meeting/summarize, /history/actions, /history/voice
│   └── services/
│       ├── mistral_service.py      ← Loads Mistral-7B + Telugu LoRA, run() helper
│       └── gemini_service.py       ← Gemini Vision API, analyze() + describe_image()
│
├── frontend/
│   ├── void_ball.py                ← PyQt5 floating ball, radial menu, voice I/O, popups
│   └── requirements.txt
│
├── database/
│   └── setup.sql                   ← Run once in PostgreSQL to create DB + user
│
├── scripts/
│   ├── install.bat                 ← Install all dependencies (run first)
│   ├── start_backend.bat           ← Start FastAPI backend
│   └── start_void.bat              ← Launch VOID ball UI
│
├── LLM_placeholder/
│   └── README.md                   ← Place your LoRA adapter files here
│
└── README.md                       ← This file
```

---

## Features

| Icon | Feature | How it works |
|------|---------|-------------|
| 💬 | **Suggest** | Speak your chat context → Mistral suggests a reply |
| 📝 | **Summarize** | Screenshots screen → Gemini summarizes content |
| 📸 | **Screenshot** | Saves screenshot to `~/Pictures/VOID/` with auto-folder |
| 🎤 | **Voice** | Whisper listens → types your words into active app |
| 🔍 | **Explain** | Screenshots screen → Gemini reads + explains with voice |
| 🌐 | **Translate** | Screenshots screen → translates Telugu↔English |
| ✍️ | **Auto Type** | Speak context → Mistral suggests → types it directly |
| 📋 | **History** | Shows last 5 VOID actions |

**Additional:**
- 🔊 Speaks every result aloud (pyttsx3)
- ⎘ Copy button on every result popup
- 🖱️ Drag ball anywhere on screen
- 🔄 System tray: hide/show/quit
- 🗄️ All actions logged to PostgreSQL
- 📅 Meeting summarizer endpoint (for future meeting feature)

---

## Setup Guide

### Prerequisites
- Python 3.10+
- PostgreSQL installed and running
- Your Telugu LoRA adapter files (LLM folder)
- Gemini API key (free at https://aistudio.google.com)
- Mistral-7B cached at D:\huggingface (already downloaded)

---

### Step 1 — Copy your LLM folder
Copy your LoRA adapter folder into this project and rename it `LLM`:
```
VOID_Project/
└── LLM/
    ├── adapter_config.json
    ├── adapter_model.safetensors
    └── tokenizer_config.json   ← make sure tokenizer_class is "LlamaTokenizer"
```

Fix tokenizer_config.json if needed — replace contents with:
```json
{
  "bos_token": "<s>",
  "eos_token": "</s>",
  "pad_token": "</s>",
  "unk_token": "<unk>",
  "tokenizer_class": "LlamaTokenizer",
  "model_max_length": 32768,
  "legacy": false,
  "clean_up_tokenization_spaces": false,
  "sp_model_kwargs": {}
}
```

---

### Step 2 — PostgreSQL Setup
Open psql or pgAdmin and run:
```sql
CREATE USER void_user WITH PASSWORD 'void_password';
CREATE DATABASE void_db OWNER void_user;
```
Or run the full script: `database/setup.sql`

---

### Step 3 — Configure .env
Edit `backend/.env`:
```
GEMINI_API_KEY=your_actual_key_here    ← get from aistudio.google.com (free)
ADAPTER_PATH=../LLM                    ← path to your LoRA folder
HF_HOME=D:\huggingface                 ← where Mistral is cached
```

---

### Step 4 — Install Dependencies
```bat
scripts\install.bat
```
This creates a venv and installs both backend and frontend dependencies.

---

### Step 5 — Run VOID

**Terminal 1 — Backend:**
```bat
scripts\start_backend.bat
```
Wait for: `✅ Mistral + Telugu LoRA ready!`

**Terminal 2 — VOID Ball:**
```bat
scripts\start_void.bat
```
The glowing VOID ball appears on screen!

---

## API Endpoints

| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/health` | Health check |
| POST | `/text/suggest` | Chat reply suggestion |
| POST | `/text/summarize` | Summarize text |
| POST | `/text/translate` | Telugu ↔ English |
| POST | `/text/voice-log` | Log voice transcription |
| POST | `/screen/analyze` | Screen analysis (suggest/summarize/explain/translate) |
| POST | `/screen/explain` | Deep screen explanation with optional question |
| POST | `/screen/save-screenshot` | Save screenshot to disk + DB |
| GET | `/screen/screenshots` | List saved screenshots |
| POST | `/meeting/summarize` | Summarize meeting transcription |
| GET | `/history/actions` | Recent action logs |
| GET | `/history/voice` | Voice transcription history |
| GET | `/history/meetings` | Past meeting summaries |

Swagger UI: `http://localhost:8000/docs`

---

## Architecture

```
┌─────────────────────────────────────┐
│         VOID Ball (PyQt5)           │
│  Floating UI · Radial Menu · TTS   │
│  Whisper Voice · Screenshot        │
└──────────────┬──────────────────────┘
               │ HTTP (localhost:8000)
┌──────────────▼──────────────────────┐
│      FastAPI Backend               │
│  ┌─────────────┐ ┌───────────────┐ │
│  │   Mistral   │ │ Gemini Vision │ │
│  │ 7B + Telugu │ │  (free API)   │ │
│  │    LoRA     │ │               │ │
│  └─────────────┘ └───────────────┘ │
│  ┌───────────────────────────────┐ │
│  │       PostgreSQL DB           │ │
│  │ action_logs · screenshots     │ │
│  │ voice_logs · meeting_logs     │ │
│  └───────────────────────────────┘ │
└────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | PyQt5 |
| Voice Input | OpenAI Whisper (tiny) |
| Voice Output | pyttsx3 |
| Screenshot | pyautogui + Pillow |
| OCR | EasyOCR |
| Text AI | Mistral-7B-v0.1 + Telugu LoRA |
| Vision AI | Google Gemini 1.5 Flash |
| Backend | FastAPI + Uvicorn |
| Database | PostgreSQL + SQLAlchemy |
| Auto-typing | pyautogui |
