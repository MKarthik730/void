

# 🌌VOID | Advanced AI Desktop Assistant

**VOID** is a low-latency, privacy-first desktop companion inspired by "Jarvis." Built with **PyQt6** and powered by local **LLMs (Qwen2.5)**, it combines a sleek glassmorphic floating UI with deep system control, OCR, and voice integration.

---

##  Features

### 🧠 Intelligence & Context

* **Local LLM Integration:** Powered by `llama.cpp` using Qwen2.5 3B for high-speed, offline reasoning.
* **Tenglish Support:** Native understanding of Telugu-English code-switching.
* **Long-term Memory:** SQLite-backed context retention for ongoing tasks.
* **Study Suite:** Automatic generation of quizzes and flashcards from provided text.

### 👁️ Vision & Utility

* **OCR Screen Reader:** Instant text extraction from any part of the screen via `mss` and `pytesseract`.
* **Snapshot to Markdown:** Convert visual data into structured documentation.
* **Clipboard Orchestrator:** Read, analyze, and rewrite clipboard content on the fly.

### ⚙️ System Control

* **OS Operations:** Open/close applications, file search, and volume/brightness management.
* **Network Management:** Connect or disconnect from Wi-Fi via `nmcli`.
* **Voice-First Interface:** * **Wake Word:** "Hey Jarvis" activation.
* **STT:** Fast transcription via Whisper (Tiny).
* **TTS:** Clean vocal feedback via `pyttsx3`.



---

## 🎨 Interface & Aesthetics

The UI is designed to be non-intrusive but highly accessible, utilizing a **frameless, glassmorphic** design.

### The Floating Sphere

The core of Void is an 80x80px interactive sphere that lives on your desktop.

* 🔵 **Idle:** Slow electric blue pulse (#00d4ff).
* 🟢 **Listening:** Vibrant green glow.
* 🌀 **Thinking:** Rotating ring animation.
* 🔴 **Error:** Sharp red flash.

### The Command Center

Expanding the sphere reveals a 400x600px panel:

* **Glassmorphic Surface:** Background blur with #0a0a0f transparency.
* **Side Dock:** Quick-access icons for Chat, OCR, Todo, and Settings.
* **Status Bar:** Real-time feedback on current system mode.

---

## 🛠️ Tech Stack

| Component | Technology |
| --- | --- |
| **Framework** | PyQt6 (Python) |
| **Model** | Qwen2.5 3B (GGUF Q4_K_M) |
| **Inference** | llama.cpp / FastAPI |
| **Vision** | Pytesseract / MSS |
| **Speech** | OpenAI Whisper / pyttsx3 |
| **Database** | SQLite |

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* Tesseract OCR engine installed on your OS.
* `llama-cpp-python` for local LLM acceleration.

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/MKarthik730/void.git
cd void

```


2. **Install Dependencies:**
```bash
pip install -r requirements.txt

```


3. **Run the Assistant:**
```bash
python main.py

```




---

