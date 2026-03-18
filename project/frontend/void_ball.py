"""
VOID — Floating AI Assistant Ball
PyQt5 Frontend: glowing ball + radial menu + voice + TTS + result popup
NEW: Ask VOID (chat), Draft Email, WhatsApp Tenglish suggestions
"""

import sys
import os
import math
import base64
import threading
import tempfile
import subprocess
import requests
import pyautogui
import pyttsx3
import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from io import BytesIO
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QSystemTrayIcon,
    QMenu, QAction, QInputDialog, QMessageBox,
    QTextEdit, QLineEdit, QScrollArea, QFrame
)
from PyQt5.QtCore import (
    Qt, QPoint, QTimer, QThread,
    pyqtSignal, QRect, QSize
)
from PyQt5.QtGui import (
    QPainter, QColor, QBrush, QPen, QFont,
    QRadialGradient, QPainterPath, QLinearGradient
)

# ── Config ────────────────────────────────────────────────────────────────────
BACKEND_URL   = "http://localhost:8000"
BALL_SIZE     = 72
ICON_RADIUS   = 115
ICON_BTN_SIZE = 58
RECORD_SECS   = 6
SAMPLERATE    = 16000

# JARVIS HUD-inspired icons
ICONS = [
    {"symbol": "⬡",  "label": "MSG",   "name": "WhatsApp",   "action": "whatsapp",   "angle": 270, "color": "#00E676"},
    {"symbol": "≣",  "label": "SUM",   "name": "Summarize",  "action": "summarize",  "angle": 315, "color": "#00B8D4"},
    {"symbol": "⊡",  "label": "CAP",   "name": "Screenshot", "action": "screenshot", "angle": 0,   "color": "#00B8D4"},
    {"symbol": "◎",  "label": "MIC",   "name": "Voice",      "action": "voice",      "angle": 45,  "color": "#FFD740"},
    {"symbol": "⊹",  "label": "SCAN",  "name": "Explain",    "action": "explain",    "angle": 90,  "color": "#00B8D4"},
    {"symbol": "⟐",  "label": "TRNSL", "name": "Translate",  "action": "translate",  "angle": 135, "color": "#00B8D4"},
    {"symbol": "⊠",  "label": "MAIL",  "name": "Email",      "action": "email",      "angle": 180, "color": "#FF6D00"},
    {"symbol": "⬡",  "label": "A.I.",  "name": "Ask VOID",   "action": "askvoid",    "angle": 225, "color": "#E040FB"},
]

# ── TTS ───────────────────────────────────────────────────────────────────────
_tts = pyttsx3.init()
_tts.setProperty("rate", 155)
_tts.setProperty("volume", 0.9)

def speak(text: str):
    def _run():
        _tts.say(text[:400])
        _tts.runAndWait()
    threading.Thread(target=_run, daemon=True).start()

# ── Whisper Voice Input ───────────────────────────────────────────────────────
print("⏳ Loading Whisper tiny model...")
_whisper = whisper.load_model("tiny")
print("✅ Whisper ready!")

def record_and_transcribe(duration: int = RECORD_SECS) -> str:
    speak("Listening...")
    audio = sd.rec(int(duration * SAMPLERATE), samplerate=SAMPLERATE,
                   channels=1, dtype="int16")
    sd.wait()
    tmp = tempfile.mktemp(suffix=".wav")
    wav.write(tmp, SAMPLERATE, audio)
    result = _whisper.transcribe(tmp, language=None)
    os.remove(tmp)
    return result["text"].strip()

# ── Screenshot Helper ─────────────────────────────────────────────────────────
def screenshot_b64() -> str:
    shot = pyautogui.screenshot()
    buf  = BytesIO()
    shot.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

# ── API Helpers ───────────────────────────────────────────────────────────────
def api_post(path: str, payload: dict, timeout: int = 90) -> dict:
    try:
        r = requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to VOID backend. Is the server running?"}
    except Exception as e:
        return {"error": str(e)}

def api_get(path: str, timeout: int = 15) -> dict:
    try:
        r = requests.get(f"{BACKEND_URL}{path}", timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


# ── Chat Window ───────────────────────────────────────────────────────────────
class ChatWindow(QWidget):
    """Professional floating chat window to Ask VOID anything"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(420, 540)
        self.chat_history = []  # list of (role, text)
        self._drag_pos = None
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self._container = QWidget(self)
        self._container.setFixedSize(420, 540)
        self._container.setStyleSheet("""
            QWidget {
                background: rgba(6, 8, 14, 245);
                border-radius: 18px;
                border: 1px solid rgba(0, 255, 200, 50);
            }
        """)

        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(18, 14, 18, 16)
        layout.setSpacing(10)

        # Header
        header_row = QHBoxLayout()
        title = QLabel("◈ VOID  ·  CHAT")
        title.setStyleSheet("""
            color: #00FFC8;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 4px;
        """)
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #4a6a64;
                border: 1px solid #1a3535;
                border-radius: 12px;
                font-size: 10px;
            }
            QPushButton:hover { color: #00FFC8; border-color: #00FFC8; }
        """)
        close_btn.clicked.connect(self.hide)
        header_row.addWidget(title)
        header_row.addStretch()
        header_row.addWidget(close_btn)

        # Divider
        divider = QLabel("─" * 50)
        divider.setStyleSheet("color: #1a3a35; font-size: 9px;")

        # Chat display area
        self._chat_area = QTextEdit()
        self._chat_area.setReadOnly(True)
        self._chat_area.setStyleSheet("""
            QTextEdit {
                background: transparent;
                color: #D0D8D6;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                border: none;
                line-height: 1.6;
            }
            QScrollBar:vertical {
                background: rgba(0,0,0,0);
                width: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0,255,200,80);
                border-radius: 2px;
            }
        """)
        self._chat_area.setPlaceholderText("Ask me anything, bro...")

        # WhatsApp suggestion strip
        self._wa_strip = QWidget()
        self._wa_strip.setFixedHeight(38)
        self._wa_strip.setStyleSheet("background: transparent;")
        wa_layout = QHBoxLayout(self._wa_strip)
        wa_layout.setContentsMargins(0, 0, 0, 0)
        wa_layout.setSpacing(6)
        self._wa_label = QLabel("💬 WhatsApp:")
        self._wa_label.setStyleSheet("color: #4a6a64; font-family: 'Courier New'; font-size: 10px;")
        self._wa_btn1 = QPushButton("")
        self._wa_btn2 = QPushButton("")
        self._wa_btn3 = QPushButton("")
        for btn in [self._wa_btn1, self._wa_btn2, self._wa_btn3]:
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(0,255,200,10);
                    color: #00FFC8;
                    border: 1px solid rgba(0,255,200,40);
                    border-radius: 10px;
                    padding: 3px 10px;
                    font-family: 'Courier New';
                    font-size: 10px;
                }
                QPushButton:hover { background: rgba(0,255,200,25); }
            """)
            btn.hide()
            btn.clicked.connect(lambda checked, b=btn: self._type_suggestion(b.text()))
        wa_layout.addWidget(self._wa_label)
        wa_layout.addWidget(self._wa_btn1)
        wa_layout.addWidget(self._wa_btn2)
        wa_layout.addWidget(self._wa_btn3)
        wa_layout.addStretch()
        self._wa_strip.hide()

        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Type or press 🎤 to speak...")
        self._input.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 255, 200, 8);
                color: #D0D8D6;
                border: 1px solid rgba(0,255,200,50);
                border-radius: 10px;
                padding: 8px 14px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
            QLineEdit:focus { border-color: rgba(0,255,200,120); }
        """)
        self._input.returnPressed.connect(self._send_text)

        mic_btn = QPushButton("🎤")
        mic_btn.setFixedSize(36, 36)
        mic_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0,255,200,15);
                border: 1px solid rgba(0,255,200,60);
                border-radius: 18px;
                font-size: 14px;
            }
            QPushButton:hover { background: rgba(0,255,200,35); }
        """)
        mic_btn.clicked.connect(self._send_voice)

        send_btn = QPushButton("➤")
        send_btn.setFixedSize(36, 36)
        send_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0,255,200,20);
                color: #00FFC8;
                border: 1px solid rgba(0,255,200,80);
                border-radius: 18px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background: rgba(0,255,200,45); }
        """)
        send_btn.clicked.connect(self._send_text)

        input_row.addWidget(self._input)
        input_row.addWidget(mic_btn)
        input_row.addWidget(send_btn)

        layout.addLayout(header_row)
        layout.addWidget(divider)
        layout.addWidget(self._chat_area, 1)
        layout.addWidget(self._wa_strip)
        layout.addLayout(input_row)

        outer.addWidget(self._container)

    def _append_message(self, role: str, text: str):
        if role == "user":
            prefix = '<span style="color:#00FFC8; font-weight:bold;">YOU ▸</span> '
        else:
            prefix = '<span style="color:#FFB830; font-weight:bold;">VOID ▸</span> '
        self._chat_area.append(f'{prefix}<span style="color:#D0D8D6;">{text}</span><br>')
        self._chat_area.verticalScrollBar().setValue(
            self._chat_area.verticalScrollBar().maximum()
        )

    def _send_text(self):
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self._process_query(text)

    def _send_voice(self):
        self._append_message("void", "🎤 Listening...")
        def _run():
            text = record_and_transcribe(5)
            self._input.setText(text)
            self._process_query(text)
        threading.Thread(target=_run, daemon=True).start()

    def _process_query(self, text: str):
        self._append_message("user", text)
        self.chat_history.append({"role": "user", "content": text})
        self._append_message("void", "⏳ Thinking...")

        def _run():
            res = api_post("/text/suggest", {"text": text})
            reply = res.get("suggestion", res.get("error", "No response"))
            self.chat_history.append({"role": "assistant", "content": reply})
            # Remove "thinking" line
            cursor = self._chat_area.textCursor()
            self._chat_area.undo()
            self._append_message("void", reply)
            speak(reply[:300])
            # Show WhatsApp suggestions if reply looks conversational
            self._show_wa_suggestions(reply)
        threading.Thread(target=_run, daemon=True).start()

    def _show_wa_suggestions(self, reply: str):
        """Generate 3 short Tenglish WhatsApp reply suggestions"""
        def _run():
            prompt = (
                "Generate exactly 3 very short WhatsApp reply suggestions in Tenglish "
                "(Telugu words in English script mixed with English). "
                "Each suggestion max 8 words. Casual, friendly tone. "
                "Format: only the 3 suggestions separated by | character. "
                f"Context: {reply[:200]}"
            )
            res = api_post("/text/suggest", {"text": prompt})
            suggestions_raw = res.get("suggestion", "")
            parts = [s.strip() for s in suggestions_raw.split("|") if s.strip()][:3]
            if parts:
                self._wa_strip.show()
                btns = [self._wa_btn1, self._wa_btn2, self._wa_btn3]
                for i, btn in enumerate(btns):
                    if i < len(parts):
                        btn.setText(parts[i])
                        btn.show()
                    else:
                        btn.hide()
        threading.Thread(target=_run, daemon=True).start()

    def _type_suggestion(self, text: str):
        """Type the suggestion into the active window"""
        self.hide()
        import time
        time.sleep(0.3)
        pyautogui.typewrite(text, interval=0.04)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.LeftButton:
            self.move(e.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    def show_near(self, pos: QPoint):
        self.move(pos.x() + 90, pos.y() - 270)
        self.show()
        self.raise_()
        self._input.setFocus()


# ── Email Draft Window ────────────────────────────────────────────────────────
class EmailDraftWindow(QWidget):
    """Draft professional emails by voice"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(460, 480)
        self._drag_pos = None
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        container = QWidget(self)
        container.setFixedSize(460, 480)
        container.setStyleSheet("""
            QWidget {
                background: rgba(6, 8, 14, 245);
                border-radius: 18px;
                border: 1px solid rgba(0, 255, 200, 50);
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 18)
        layout.setSpacing(10)

        # Header
        header_row = QHBoxLayout()
        title = QLabel("◈ VOID  ·  EMAIL DRAFT")
        title.setStyleSheet("""
            color: #00FFC8;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 3px;
        """)
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #4a6a64;
                border: 1px solid #1a3535; border-radius: 12px; font-size: 10px;
            }
            QPushButton:hover { color: #00FFC8; border-color: #00FFC8; }
        """)
        close_btn.clicked.connect(self.hide)
        header_row.addWidget(title)
        header_row.addStretch()
        header_row.addWidget(close_btn)

        divider = QLabel("─" * 55)
        divider.setStyleSheet("color: #1a3a35; font-size: 9px;")

        # Instructions
        hint = QLabel("🎤 Speak what you want to say → VOID drafts a professional email")
        hint.setWordWrap(True)
        hint.setStyleSheet("""
            color: #4a6a64;
            font-family: 'Courier New', monospace;
            font-size: 10px;
        """)

        # Draft output
        self._draft_area = QTextEdit()
        self._draft_area.setPlaceholderText("Your email draft will appear here...")
        self._draft_area.setStyleSheet("""
            QTextEdit {
                background: rgba(0, 255, 200, 5);
                color: #D0D8D6;
                border: 1px solid rgba(0,255,200,30);
                border-radius: 10px;
                padding: 12px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                line-height: 1.6;
            }
        """)

        # Status
        self._status = QLabel("")
        self._status.setStyleSheet("""
            color: #FFB830;
            font-family: 'Courier New', monospace;
            font-size: 10px;
        """)

        # Button row
        btn_style = """
            QPushButton {
                background: rgba(0,255,200,12);
                color: #00FFC8;
                border: 1px solid rgba(0,255,200,50);
                border-radius: 8px;
                padding: 8px 18px;
                font-family: 'Courier New';
                font-size: 10px;
                letter-spacing: 1px;
            }
            QPushButton:hover { background: rgba(0,255,200,28); }
        """
        btn_row = QHBoxLayout()
        record_btn = QPushButton("🎤  RECORD & DRAFT")
        record_btn.setStyleSheet(btn_style)
        record_btn.clicked.connect(self._record_and_draft)

        copy_btn = QPushButton("⎘  COPY")
        copy_btn.setStyleSheet(btn_style)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self._draft_area.toPlainText()))

        clear_btn = QPushButton("✕  CLEAR")
        clear_btn.setStyleSheet(btn_style)
        clear_btn.clicked.connect(self._draft_area.clear)

        btn_row.addWidget(record_btn)
        btn_row.addWidget(copy_btn)
        btn_row.addStretch()
        btn_row.addWidget(clear_btn)

        layout.addLayout(header_row)
        layout.addWidget(divider)
        layout.addWidget(hint)
        layout.addWidget(self._draft_area, 1)
        layout.addWidget(self._status)
        layout.addLayout(btn_row)

        outer.addWidget(container)

    def _record_and_draft(self):
        self._status.setText("🎤 Listening... speak your email idea")
        def _run():
            text = record_and_transcribe(8)
            self._status.setText("🧠 Drafting professional email...")
            instruction = (
                "Draft a professional, well-structured email based on this voice note. "
                "Include Subject, greeting, body, and sign-off. "
                "Make it concise and professional.\n\n"
                f"Voice note: {text}"
            )
            res = api_post("/text/suggest", {"text": instruction})
            draft = res.get("suggestion", res.get("error", "Failed to draft email"))
            self._draft_area.setPlainText(draft)
            self._status.setText("✅ Draft ready — edit and copy!")
            speak("Email draft is ready")
        threading.Thread(target=_run, daemon=True).start()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.LeftButton:
            self.move(e.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    def show_near(self, pos: QPoint):
        self.move(pos.x() + 90, pos.y() - 240)
        self.show()
        self.raise_()



# ── WhatsApp Reply Window ─────────────────────────────────────────────────────
class WhatsAppWindow(QWidget):
    """Screenshot WhatsApp chat → show 3 Tenglish suggestions → auto send"""
    send_signal   = pyqtSignal(str)
    update_signal = pyqtSignal(list, str)  # (suggestions, error)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_pos = None
        self._sug_btns = []
        self._build_ui()
        self.update_signal.connect(self._apply_suggestions)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 18)
        layout.setSpacing(8)

        # Header
        header_row = QHBoxLayout()
        title = QLabel("💚 VOID  ·  WHATSAPP REPLY")
        title.setStyleSheet("color:#25D366; font-family:'Courier New'; font-size:11px; font-weight:bold; letter-spacing:3px;")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("QPushButton{background:transparent;color:#4a6a64;border:1px solid #1a3535;border-radius:12px;font-size:10px;}QPushButton:hover{color:#25D366;border-color:#25D366;}")
        close_btn.clicked.connect(self.hide)
        header_row.addWidget(title)
        header_row.addStretch()
        header_row.addWidget(close_btn)
        layout.addLayout(header_row)

        # Divider
        div = QLabel("─" * 48)
        div.setStyleSheet("color:#1a3a35; font-size:9px;")
        layout.addWidget(div)

        # Status
        self._status = QLabel("Click SCAN to read your WhatsApp chat")
        self._status.setWordWrap(True)
        self._status.setStyleSheet("color:#4a6a64; font-family:'Courier New'; font-size:10px;")
        layout.addWidget(self._status)

        # 3 suggestion buttons — ALWAYS visible, just updated with text
        btn_style = """
            QPushButton {{
                background: rgba(37,211,102,{a});
                color: #D0FFE8;
                border: 1px solid rgba(37,211,102,80);
                border-radius: 8px;
                padding: 9px 12px;
                font-family: 'Courier New';
                font-size: 11px;
                text-align: left;
                min-height: 36px;
            }}
            QPushButton:hover {{
                background: rgba(37,211,102,50);
                color: #ffffff;
            }}
        """
        for i in range(3):
            btn = QPushButton(f"  · · ·")
            btn.setStyleSheet(btn_style.format(a=12 + i*6))
            btn.setEnabled(False)  # disabled until suggestions arrive
            btn.clicked.connect(lambda checked, b=btn: self._send_suggestion(b.text().strip()))
            self._sug_btns.append(btn)
            layout.addWidget(btn)

        layout.addSpacing(4)

        # Scan button
        scan_btn = QPushButton("📷  SCAN WHATSAPP CHAT")
        scan_btn.setStyleSheet("""
            QPushButton {
                background: rgba(37,211,102,18);
                color: #25D366;
                border: 1px solid rgba(37,211,102,80);
                border-radius: 10px;
                padding: 10px;
                font-family: 'Courier New';
                font-size: 11px;
                font-weight: bold;
                min-height: 38px;
            }
            QPushButton:hover { background: rgba(37,211,102,35); }
        """)
        scan_btn.clicked.connect(self._scan_and_suggest)
        layout.addWidget(scan_btn)

        self.setFixedWidth(440)

    def _scan_and_suggest(self):
        self._status.setText("📸 Reading your screen...")
        for btn in self._sug_btns:
            btn.setText("  · · ·")
            btn.setEnabled(False)

        # Hide window, take screenshot, show window — all on main thread first
        self.hide()
        QApplication.processEvents()

        import time
        time.sleep(0.5)
        b64 = screenshot_b64()

        self.show()
        QApplication.processEvents()
        self._status.setText("🧠 Generating Tenglish replies...")

        # Now do the slow API call in background thread
        def _run(b64=b64):
            print("[WA] Calling /screen/whatsapp-suggest...")
            res = api_post("/screen/whatsapp-suggest", {"screenshot_b64": b64})
            suggestions = res.get("suggestions", [])
            error = res.get("error", "")
            print(f"[WA] Suggestions: {suggestions}")
            # Emit signal — guaranteed to run on main Qt thread
            self.update_signal.emit(suggestions, error)

        threading.Thread(target=_run, daemon=True).start()

    def _apply_suggestions(self, suggestions: list, error: str):
        """Called on main thread via signal — safely updates UI"""
        if error and not suggestions:
            self._status.setText(f"⚠️ {error[:80]}")
            return
        if suggestions:
            self._status.setText("✅ Tap a reply to auto-send:")
            for i, btn in enumerate(self._sug_btns):
                if i < len(suggestions):
                    btn.setText(f"  {suggestions[i]}")
                    btn.setEnabled(True)
                else:
                    btn.setText("  · · ·")
                    btn.setEnabled(False)
        else:
            self._status.setText("⚠️ Could not generate suggestions.")

    def _send_suggestion(self, text: str):
        # Emit signal so sending happens on main thread — avoids freeze
        self.send_signal.emit(text.strip())

    def _do_send(self, text: str):
        """Runs on main Qt thread — safe to touch clipboard and focus windows"""
        import time
        import ctypes
        import ctypes.wintypes

        self.hide()
        QApplication.processEvents()

        # Find and focus WhatsApp Desktop window
        try:
            EnumWindows      = ctypes.windll.user32.EnumWindows
            EnumWindowsProc  = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
            GetWindowText    = ctypes.windll.user32.GetWindowTextW
            SetForegroundWindow = ctypes.windll.user32.SetForegroundWindow
            ShowWindow       = ctypes.windll.user32.ShowWindow
            IsWindowVisible  = ctypes.windll.user32.IsWindowVisible

            wa_hwnd = None
            def enum_cb(hwnd, lparam):
                nonlocal wa_hwnd
                buf = ctypes.create_unicode_buffer(256)
                GetWindowText(hwnd, buf, 256)
                if "WhatsApp" in buf.value and IsWindowVisible(hwnd):
                    wa_hwnd = hwnd
                return True

            EnumWindows(EnumWindowsProc(enum_cb), 0)

            if wa_hwnd:
                ShowWindow(wa_hwnd, 9)
                SetForegroundWindow(wa_hwnd)
        except Exception as ex:
            print(f"Focus error: {ex}")

        # Use QTimer to delay paste so window focus settles
        def _paste():
            QApplication.clipboard().setText(text)
            screen_w, screen_h = pyautogui.size()
            pyautogui.click(screen_w // 2, screen_h - 80)
            import time
            time.sleep(0.15)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.1)
            pyautogui.press("enter")

        QTimer.singleShot(600, _paste)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.LeftButton:
            self.move(e.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    def show_near(self, pos: QPoint):
        self.move(pos.x() + 90, pos.y() - 160)
        self.show()
        self.raise_()

# ── Action Worker Thread ──────────────────────────────────────────────────────
class ActionWorker(QThread):
    finished = pyqtSignal(str, str)
    status   = pyqtSignal(str)

    def __init__(self, action: str):
        super().__init__()
        self.action = action

    def run(self):
        action = self.action
        result = ""

        try:
            if action == "suggest":
                self.status.emit("🎤 Listening for context...")
                text = record_and_transcribe(5)
                self.status.emit("🧠 Generating suggestion...")
                res  = api_post("/text/suggest", {"text": text})
                result = res.get("suggestion", res.get("error", "No response"))

            elif action == "summarize":
                self.status.emit("📸 Capturing screen...")
                b64  = screenshot_b64()
                self.status.emit("🧠 Summarizing...")
                res  = api_post("/screen/analyze", {"screenshot_b64": b64, "action": "summarize"})
                result = res.get("result", res.get("error", "No response"))

            elif action == "screenshot":
                self.status.emit("📸 Saving screenshot...")
                b64  = screenshot_b64()
                res  = api_post("/screen/save-screenshot", {"screenshot_b64": b64})
                result = f"✅ Saved to:\n{res.get('saved_to', res.get('error', 'Unknown'))}"

            elif action == "voice":
                self.status.emit("🎤 Listening...")
                text = record_and_transcribe(RECORD_SECS)
                self.status.emit("⌨️ Typing...")
                api_post("/text/voice-log", {
                    "transcription": text,
                    "language": "auto",
                    "action_taken": "type"
                })
                pyautogui.typewrite(text, interval=0.04)
                result = f"Typed: {text}"

            elif action == "explain":
                self.status.emit("📸 Capturing screen...")
                b64  = screenshot_b64()
                self.status.emit("👁️ Analyzing your screen...")
                res  = api_post("/screen/explain", {"screenshot_b64": b64, "question": ""})
                result = res.get("explanation", res.get("error", "No response"))

            elif action == "translate":
                self.status.emit("📸 Capturing screen...")
                b64  = screenshot_b64()
                self.status.emit("🌐 Translating...")
                res  = api_post("/screen/analyze", {"screenshot_b64": b64, "action": "translate"})
                result = res.get("result", res.get("error", "No response"))

            elif action == "autotype":
                self.status.emit("🎤 Listening...")
                text = record_and_transcribe(5)
                self.status.emit("🧠 Generating reply...")
                res  = api_post("/text/suggest", {"text": text})
                suggestion = res.get("suggestion", "")
                if suggestion:
                    self.status.emit("⌨️ Typing reply...")
                    pyautogui.typewrite(suggestion, interval=0.04)
                result = f"Typed suggestion:\n{suggestion}"

            elif action == "history":
                self.status.emit("📋 Fetching history...")
                res  = api_get("/history/actions?limit=5")
                logs = res.get("history", [])
                if logs:
                    result = "\n\n".join([
                        f"[{l['action'].upper()}] {(l['output'] or '')[:100]}"
                        for l in logs
                    ])
                else:
                    result = res.get("error", "No history found")

            else:
                result = "Unknown action"

        except Exception as e:
            result = f"Error: {str(e)}"

        self.finished.emit(action, result)


# ── Icon Button ───────────────────────────────────────────────────────────────
class IconButton(QWidget):
    clicked_action = pyqtSignal(str)

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.data    = data
        self.hovered = False
        self.setFixedSize(ICON_BTN_SIZE, ICON_BTN_SIZE)
        self.setToolTip(data["name"])
        self.setCursor(Qt.PointingHandCursor)
        self.hide()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked_action.emit(self.data["action"])

    def enterEvent(self, e):
        self.hovered = True
        self.update()

    def leaveEvent(self, e):
        self.hovered = False
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        s = ICON_BTN_SIZE
        col = QColor(self.data.get("color", "#00B8D4"))
        cr = col.red(); cg = col.green(); cb = col.blue()

        # Outer glow when hovered
        if self.hovered:
            for i in range(3, 0, -1):
                glow = QColor(cr, cg, cb, 15 * i)
                p.setBrush(QBrush(glow))
                p.setPen(Qt.NoPen)
                p.drawRoundedRect(4-i, 4-i, s-8+i*2, s-8+i*2, 7, 7)

        # Background fill
        bg_alpha = 60 if self.hovered else 20
        p.setBrush(QBrush(QColor(cr, cg, cb, bg_alpha)))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(4, 4, s-8, s-8, 6, 6)

        # Diagonal corner cuts — JARVIS HUD style
        pen = QPen(QColor(cr, cg, cb, 200 if self.hovered else 100))
        pen.setWidth(1)
        p.setPen(pen)
        # Main border
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(4, 4, s-8, s-8, 4, 4)
        # Corner tick marks
        tick = 6
        p.drawLine(4, 4, 4+tick, 4)          # top-left H
        p.drawLine(4, 4, 4, 4+tick)          # top-left V
        p.drawLine(s-4, 4, s-4-tick, 4)      # top-right H
        p.drawLine(s-4, 4, s-4, 4+tick)      # top-right V
        p.drawLine(4, s-4, 4+tick, s-4)      # bot-left H
        p.drawLine(4, s-4, 4, s-4-tick)      # bot-left V
        p.drawLine(s-4, s-4, s-4-tick, s-4)  # bot-right H
        p.drawLine(s-4, s-4, s-4, s-4-tick)  # bot-right V

        # Main symbol
        sym_col = QColor(cr, cg, cb, 255 if self.hovered else 180)
        p.setPen(sym_col)
        p.setFont(QFont("Segoe UI Symbol", 16, QFont.Normal))
        p.drawText(QRect(0, -4, s, s), Qt.AlignCenter, self.data["symbol"])

        # Short label at bottom
        lbl_col = QColor(cr, cg, cb, 220 if self.hovered else 120)
        p.setPen(lbl_col)
        p.setFont(QFont("Courier New", 5, QFont.Bold))
        p.drawText(QRect(0, s-13, s, 11), Qt.AlignCenter, self.data.get("label", ""))


# ── Result Popup ──────────────────────────────────────────────────────────────
class ResultPopup(QWidget):
    def __init__(self, text: str, action: str, screen_pos: QPoint):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(360)
        self.setMaximumWidth(480)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(12)

        header = QLabel(f"◈ VOID  ·  {action.upper()}")
        header.setStyleSheet("""
            color: #00FFC8; font-family: 'Courier New', monospace;
            font-size: 10px; font-weight: bold; letter-spacing: 4px;
        """)
        divider = QLabel("─" * 42)
        divider.setStyleSheet("color: #1a3a35; font-size: 10px;")
        content = QLabel(text[:600] + ("..." if len(text) > 600 else ""))
        content.setWordWrap(True)
        content.setStyleSheet("""
            color: #D0D8D6; font-family: 'Courier New', monospace;
            font-size: 12px; line-height: 1.7;
        """)

        btn_style = """
            QPushButton {
                background: transparent; color: #4a6a64;
                border: 1px solid #1a3535; border-radius: 5px;
                padding: 5px 14px; font-family: 'Courier New';
                font-size: 10px; letter-spacing: 1px;
            }
            QPushButton:hover { color: #00FFC8; border-color: #00FFC8; background: rgba(0,255,200,0.05); }
        """
        btn_row = QHBoxLayout()
        speak_btn = QPushButton("🔊  SPEAK")
        speak_btn.setStyleSheet(btn_style)
        speak_btn.clicked.connect(lambda: speak(text))
        copy_btn = QPushButton("⎘  COPY")
        copy_btn.setStyleSheet(btn_style)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(text))
        close_btn = QPushButton("✕  CLOSE")
        close_btn.setStyleSheet(btn_style)
        close_btn.clicked.connect(self.close)

        btn_row.addWidget(speak_btn)
        btn_row.addWidget(copy_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)

        layout.addWidget(header)
        layout.addWidget(divider)
        layout.addWidget(content)
        layout.addLayout(btn_row)

        self.move(screen_pos.x() + 90, screen_pos.y() - 30)
        self.adjustSize()
        QTimer.singleShot(20000, self.close)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, 10, 10)
        p.fillPath(path, QColor(4, 10, 20, 255))
        # Border
        pen = QPen(QColor(0, 180, 220, 180))
        pen.setWidth(1)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(1, 1, w-2, h-2, 10, 10)
        # Corner marks
        cp = QPen(QColor(0, 200, 255, 220))
        cp.setWidth(2)
        p.setPen(cp)
        t = 10
        p.drawLine(1,1,1+t,1); p.drawLine(1,1,1,1+t)
        p.drawLine(w-1,1,w-1-t,1); p.drawLine(w-1,1,w-1,1+t)
        p.drawLine(1,h-1,1+t,h-1); p.drawLine(1,h-1,1,h-1-t)
        p.drawLine(w-1,h-1,w-1-t,h-1); p.drawLine(w-1,h-1,w-1,h-1-t)


# ── Status Label ──────────────────────────────────────────────────────────────
class StatusLabel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text = ""
        self.setFixedSize(260, 30)
        self.hide()

    def set_text(self, text: str):
        self.text = text
        self.show()
        self.update()

    def clear(self):
        self.text = ""
        self.hide()

    def paintEvent(self, e):
        if not self.text:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 8, 8)
        p.fillPath(path, QColor(8, 10, 16, 200))
        p.setPen(QColor(0, 255, 200, 200))
        p.setFont(QFont("Courier New", 10))
        p.drawText(QRect(0, 0, self.width(), self.height()), Qt.AlignCenter, self.text)


# ── VOID Ball Widget ──────────────────────────────────────────────────────────
class VoidBall(QWidget):
    WIDGET_SIZE = 310

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(self.WIDGET_SIZE, self.WIDGET_SIZE)

        self.center   = QPoint(self.WIDGET_SIZE // 2, self.WIDGET_SIZE // 2)
        self.expanded = False
        self.thinking = False
        self.dragging = False
        self.drag_pos = QPoint()
        self._pulse   = 0.0
        self._pulse_d = 1
        self._worker  = None
        self._popup   = None

        # Floating windows
        self._chat_window  = ChatWindow()
        self._email_window = EmailDraftWindow()
        self._wa_window    = WhatsAppWindow()

        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(25)

        self._status = StatusLabel(self)
        self._status.move(
            self.center.x() - 130,
            self.center.y() + BALL_SIZE // 2 + 10
        )

        self._icons: list[IconButton] = []
        for data in ICONS:
            btn = IconButton(data, self)
            btn.clicked_action.connect(self._on_action)
            rad  = math.radians(data["angle"] - 90)
            bx   = int(self.center.x() + ICON_RADIUS * math.cos(rad)) - ICON_BTN_SIZE // 2
            by   = int(self.center.y() + ICON_RADIUS * math.sin(rad)) - ICON_BTN_SIZE // 2
            btn.move(bx, by)
            self._icons.append(btn)

        self.move(80, 80)
        self.show()

    def _tick(self):
        self._pulse += 0.035 * self._pulse_d
        if self._pulse >= 1.0: self._pulse_d = -1
        if self._pulse <= 0.0: self._pulse_d  = 1
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.center.x(), self.center.y()
        r = BALL_SIZE // 2

        # ── Color scheme based on state ──
        if self.thinking:
            core_col   = QColor(255, 160, 0)    # gold — processing
            ring_col   = QColor(255, 200, 50)
            glow_col   = QColor(255, 140, 0)
        elif self.expanded:
            core_col   = QColor(0, 200, 255)    # arc blue — active
            ring_col   = QColor(100, 220, 255)
            glow_col   = QColor(0, 180, 255)
        else:
            core_col   = QColor(0, 160, 220)    # JARVIS blue — idle
            ring_col   = QColor(50, 180, 230)
            glow_col   = QColor(0, 120, 200)

        pulse = self._pulse

        # ── Outer diffuse glow ──
        for i in range(6, 0, -1):
            off = i * 9
            alpha = int((8 + 6 * pulse) / i)
            p.setBrush(QBrush(QColor(glow_col.red(), glow_col.green(), glow_col.blue(), alpha)))
            p.setPen(Qt.NoPen)
            p.drawEllipse(cx-r-off, cy-r-off, (r+off)*2, (r+off)*2)

        # ── Deep space background ball ──
        bg = QRadialGradient(cx, cy, r)
        bg.setColorAt(0,   QColor(8,  20, 40, 255))
        bg.setColorAt(0.6, QColor(4,  10, 24, 255))
        bg.setColorAt(1,   QColor(2,   4, 12, 255))
        p.setBrush(QBrush(bg))
        p.setPen(Qt.NoPen)
        p.drawEllipse(cx-r, cy-r, r*2, r*2)

        # ── Arc reactor ring 1 — outer ──
        pen1_alpha = int(120 + 100 * pulse)
        pen1 = QPen(QColor(ring_col.red(), ring_col.green(), ring_col.blue(), pen1_alpha))
        pen1.setWidth(2)
        p.setPen(pen1)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(cx-r+3, cy-r+3, (r-3)*2, (r-3)*2)

        # ── Arc reactor ring 2 — middle ──
        pen2 = QPen(QColor(core_col.red(), core_col.green(), core_col.blue(), int(60 + 40*pulse)))
        pen2.setWidth(1)
        p.setPen(pen2)
        p.drawEllipse(cx-r+9, cy-r+9, (r-9)*2, (r-9)*2)

        # ── HUD corner ticks on outer ring ──
        tick_pen = QPen(QColor(ring_col.red(), ring_col.green(), ring_col.blue(), int(180 + 60*pulse)))
        tick_pen.setWidth(2)
        p.setPen(tick_pen)
        import math as _math
        for angle_deg in [0, 90, 180, 270]:
            a = _math.radians(angle_deg)
            x1 = int(cx + (r-2) * _math.cos(a))
            y1 = int(cy + (r-2) * _math.sin(a))
            x2 = int(cx + (r+6) * _math.cos(a))
            y2 = int(cy + (r+6) * _math.sin(a))
            p.drawLine(x1, y1, x2, y2)

        # ── 45-degree short ticks ──
        short_pen = QPen(QColor(ring_col.red(), ring_col.green(), ring_col.blue(), int(80 + 40*pulse)))
        short_pen.setWidth(1)
        p.setPen(short_pen)
        for angle_deg in [45, 135, 225, 315]:
            a = _math.radians(angle_deg)
            x1 = int(cx + (r-1) * _math.cos(a))
            y1 = int(cy + (r-1) * _math.sin(a))
            x2 = int(cx + (r+4) * _math.cos(a))
            y2 = int(cy + (r+4) * _math.sin(a))
            p.drawLine(x1, y1, x2, y2)

        # ── Arc reactor core glow ──
        core_r = 14
        core_grad = QRadialGradient(cx, cy, core_r * 2)
        core_grad.setColorAt(0,   QColor(core_col.red(), core_col.green(), core_col.blue(), int(200 + 55*pulse)))
        core_grad.setColorAt(0.4, QColor(core_col.red(), core_col.green(), core_col.blue(), int(80 + 40*pulse)))
        core_grad.setColorAt(1,   QColor(core_col.red(), core_col.green(), core_col.blue(), 0))
        p.setBrush(QBrush(core_grad))
        p.setPen(Qt.NoPen)
        p.drawEllipse(cx-core_r*2, cy-core_r*2, core_r*4, core_r*4)

        # ── Center label ──
        if self.thinking:
            label    = "···"
            txt_col  = QColor(255, 200, 50, 240)
            fsize    = 11
        else:
            label    = "VOID"
            txt_col  = QColor(200, 235, 255, int(180 + 60*pulse))
            fsize    = 8
        p.setPen(txt_col)
        p.setFont(QFont("Courier New", fsize, QFont.Bold))
        p.drawText(QRect(cx-r, cy-r, r*2, r*2), Qt.AlignCenter, label)

        # ── Status dot ──
        dot = QColor(0, 255, 100, 200) if not self.thinking else QColor(255, 180, 0, 200)
        p.setBrush(QBrush(dot))
        p.setPen(Qt.NoPen)
        p.drawEllipse(cx-3, cy+r-9, 6, 6)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            diff = e.pos() - self.center
            if diff.x()**2 + diff.y()**2 <= (BALL_SIZE // 2 + 5) ** 2:
                if not self.thinking:
                    self._toggle_menu()
            else:
                self.dragging = True
                self.drag_pos = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self.dragging and e.buttons() == Qt.LeftButton:
            self.move(e.globalPos() - self.drag_pos)

    def mouseReleaseEvent(self, e):
        self.dragging = False

    def _toggle_menu(self):
        self.expanded = not self.expanded
        for btn in self._icons:
            btn.setVisible(self.expanded)
        self.update()

    def _on_action(self, action: str):
        self._toggle_menu()

        # These open dedicated windows instead of the generic worker
        if action == "askvoid":
            self._chat_window.show_near(self.mapToGlobal(self.center))
            return
        if action == "email":
            self._email_window.show_near(self.mapToGlobal(self.center))
            return
        if action == "whatsapp":
            self._wa_window.show_near(self.mapToGlobal(self.center))
            return

        self.thinking = True
        self._status.set_text("⏳ Processing...")
        self.update()

        self._worker = ActionWorker(action)
        self._worker.status.connect(self._on_status)
        self._worker.finished.connect(self._on_result)
        self._worker.start()

    def _on_status(self, msg: str):
        self._status.set_text(msg)

    def _on_result(self, action: str, result: str):
        self.thinking = False
        self._status.clear()
        self.update()
        speak(result[:350])
        if self._popup:
            self._popup.close()
        self._popup = ResultPopup(result, action, self.mapToGlobal(self.center))
        self._popup.show()


# ── System Tray ───────────────────────────────────────────────────────────────
def build_tray(app: QApplication, ball: VoidBall) -> QSystemTrayIcon:
    tray = QSystemTrayIcon(app)
    tray.setToolTip("VOID AI Assistant")
    menu = QMenu()

    toggle = QAction("👁  Show / Hide VOID", app)
    toggle.triggered.connect(lambda: ball.hide() if ball.isVisible() else ball.show())

    about = QAction("ℹ  About VOID", app)
    about.triggered.connect(lambda: QMessageBox.information(
        None, "VOID",
        "VOID AI Assistant v2.0\n\nQwen2.5-3B + Groq Vision\nChat · Email · WhatsApp Tenglish\nBuilt with PyQt5 + FastAPI"
    ))

    quit_a = QAction("✕  Quit", app)
    quit_a.triggered.connect(app.quit)

    menu.addAction(toggle)
    menu.addAction(about)
    menu.addSeparator()
    menu.addAction(quit_a)

    tray.setContextMenu(menu)
    tray.activated.connect(lambda reason: ball.show() if reason == QSystemTrayIcon.DoubleClick else None)
    tray.show()
    return tray


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("VOID")

    ball = VoidBall()
    tray = build_tray(app, ball)

    print("✅ VOID v2.0 is running!")
    print("   🤖 Ask VOID — chat with AI")
    print("   📧 Email — draft emails by voice")
    print("   💬 WhatsApp Tenglish suggestions")

    sys.exit(app.exec_())