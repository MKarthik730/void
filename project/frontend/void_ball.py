"""
VOID — Floating AI Assistant Ball
PyQt5 Frontend: glowing ball + radial menu + voice + TTS + result popup
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
    QMenu, QAction, QInputDialog, QMessageBox
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

ICONS = [
    {"emoji": "💬", "name": "Suggest",    "action": "suggest",    "angle": 270},
    {"emoji": "📝", "name": "Summarize",  "action": "summarize",  "angle": 315},
    {"emoji": "📸", "name": "Screenshot", "action": "screenshot", "angle": 0},
    {"emoji": "🎤", "name": "Voice",      "action": "voice",      "angle": 45},
    {"emoji": "🔍", "name": "Explain",    "action": "explain",    "angle": 90},
    {"emoji": "🌐", "name": "Translate",  "action": "translate",  "angle": 135},
    {"emoji": "✍️", "name": "Auto Type",  "action": "autotype",   "angle": 180},
    {"emoji": "📋", "name": "History",    "action": "history",    "angle": 225},
]

# ── TTS ───────────────────────────────────────────────────────────────────────
_tts = pyttsx3.init()
_tts.setProperty("rate", 155)
_tts.setProperty("volume", 0.9)

def speak(text: str):
    """Speak text in background thread"""
    def _run():
        _tts.say(text[:400])
        _tts.runAndWait()
    threading.Thread(target=_run, daemon=True).start()

# ── Whisper Voice Input ───────────────────────────────────────────────────────
print("⏳ Loading Whisper tiny model...")
_whisper = whisper.load_model("tiny")
print("✅ Whisper ready!")

def record_and_transcribe(duration: int = RECORD_SECS) -> str:
    """Record mic audio and transcribe with Whisper"""
    speak("Listening...")
    audio = sd.rec(int(duration * SAMPLERATE), samplerate=SAMPLERATE,
                   channels=1, dtype="int16")
    sd.wait()
    tmp = tempfile.mktemp(suffix=".wav")
    wav.write(tmp, SAMPLERATE, audio)
    result = _whisper.transcribe(tmp, language=None)  # auto-detect language
    os.remove(tmp)
    return result["text"].strip()

# ── Screenshot Helper ─────────────────────────────────────────────────────────
def screenshot_b64() -> str:
    """Take a screenshot and return as base64 PNG string"""
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

# ── Action Worker Thread ──────────────────────────────────────────────────────
class ActionWorker(QThread):
    finished = pyqtSignal(str, str)   # (action_name, result_text)
    status   = pyqtSignal(str)        # status message during processing

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
                # Log to backend
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
                self.status.emit("👁️ Gemini is reading your screen...")
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

        # Circle
        if self.hovered:
            p.setBrush(QBrush(QColor(0, 255, 200, 230)))
        else:
            p.setBrush(QBrush(QColor(15, 15, 25, 210)))
        pen = QPen(QColor(0, 255, 200, 160))
        pen.setWidth(1)
        p.setPen(pen)
        p.drawEllipse(2, 2, s - 4, s - 4)

        # Emoji
        p.setPen(Qt.white if not self.hovered else QColor(10, 10, 20))
        p.setFont(QFont("Segoe UI Emoji", 20))
        p.drawText(QRect(0, 0, s, s), Qt.AlignCenter, self.data["emoji"])


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

        # Header bar
        header = QLabel(f"◈ VOID  ·  {action.upper()}")
        header.setStyleSheet("""
            color: #00FFC8;
            font-family: 'Courier New', monospace;
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 4px;
        """)

        # Divider
        divider = QLabel("─" * 42)
        divider.setStyleSheet("color: #1a3a35; font-size: 10px;")

        # Content
        content = QLabel(text[:600] + ("..." if len(text) > 600 else ""))
        content.setWordWrap(True)
        content.setStyleSheet("""
            color: #D0D8D6;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.7;
        """)

        # Buttons
        btn_style = """
            QPushButton {
                background: transparent;
                color: #4a6a64;
                border: 1px solid #1a3535;
                border-radius: 5px;
                padding: 5px 14px;
                font-family: 'Courier New';
                font-size: 10px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                color: #00FFC8;
                border-color: #00FFC8;
                background: rgba(0,255,200,0.05);
            }
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

        # Position near ball
        self.move(screen_pos.x() + 90, screen_pos.y() - 30)
        self.adjustSize()

        # Auto close after 20 seconds
        QTimer.singleShot(20000, self.close)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 14, 14)
        p.fillPath(path, QColor(8, 10, 16, 240))
        pen = QPen(QColor(0, 255, 200, 40))
        pen.setWidth(1)
        p.setPen(pen)
        p.drawPath(path)


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

        # Pulse timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(25)

        # Status label (shown below ball while thinking)
        self._status = StatusLabel(self)
        self._status.move(
            self.center.x() - 130,
            self.center.y() + BALL_SIZE // 2 + 10
        )

        # Build icon buttons around ball
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

    # ── Animation tick ────────────────────────────────────────────────────────
    def _tick(self):
        self._pulse += 0.035 * self._pulse_d
        if self._pulse >= 1.0: self._pulse_d = -1
        if self._pulse <= 0.0: self._pulse_d  = 1
        self.update()

    # ── Paint ─────────────────────────────────────────────────────────────────
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.center.x(), self.center.y()
        r = BALL_SIZE // 2

        # Outer glow rings
        alpha = int(20 + 18 * self._pulse)
        for i in range(4, 0, -1):
            glow = QColor(0, 255, 200, alpha // i)
            p.setBrush(QBrush(glow))
            p.setPen(Qt.NoPen)
            offset = i * 9
            p.drawEllipse(cx - r - offset, cy - r - offset,
                          (r + offset) * 2, (r + offset) * 2)

        # Main ball
        grad = QRadialGradient(cx - r // 3, cy - r // 3, r * 1.6)
        if self.thinking:
            grad.setColorAt(0, QColor(255, 180, 30, 255))
            grad.setColorAt(0.6, QColor(180, 80, 0, 230))
            grad.setColorAt(1,   QColor(60, 20, 0, 210))
        elif self.expanded:
            grad.setColorAt(0, QColor(0, 255, 200, 255))
            grad.setColorAt(0.5, QColor(0, 160, 130, 230))
            grad.setColorAt(1,   QColor(0, 40, 50, 210))
        else:
            grad.setColorAt(0, QColor(50, 55, 80, 255))
            grad.setColorAt(0.5, QColor(18, 18, 30, 230))
            grad.setColorAt(1,   QColor(4, 4, 12, 210))

        p.setBrush(QBrush(grad))
        border_alpha = int(80 + 80 * self._pulse)
        pen = QPen(QColor(0, 255, 200, border_alpha))
        pen.setWidth(2)
        p.setPen(pen)
        p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # Inner shine
        shine = QRadialGradient(cx - r // 4, cy - r // 3, r // 2)
        shine.setColorAt(0, QColor(255, 255, 255, 30))
        shine.setColorAt(1, QColor(255, 255, 255, 0))
        p.setBrush(QBrush(shine))
        p.setPen(Qt.NoPen)
        p.drawEllipse(cx - r + 4, cy - r + 4, r * 2 - 8, r * 2 - 8)

        # Label
        p.setPen(QColor(0, 255, 200, 210 + int(40 * self._pulse)))
        label = "⏳" if self.thinking else "VOID"
        p.setFont(QFont("Courier New", 9, QFont.Bold))
        p.drawText(QRect(cx - r, cy - r, r * 2, r * 2), Qt.AlignCenter, label)

    # ── Mouse events ──────────────────────────────────────────────────────────
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

    # ── Menu toggle ───────────────────────────────────────────────────────────
    def _toggle_menu(self):
        self.expanded = not self.expanded
        for btn in self._icons:
            btn.setVisible(self.expanded)
        self.update()

    # ── Action handler ────────────────────────────────────────────────────────
    def _on_action(self, action: str):
        self._toggle_menu()
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

        # Speak result
        speak(result[:350])

        # Show popup
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
        "VOID AI Assistant v1.0\n\nTelugu Mistral + Gemini Vision\nBuilt with PyQt5 + FastAPI"
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

    print("✅ VOID is running! Look for the glowing ball on your screen.")
    print("   Right-click the system tray icon to quit.")

    sys.exit(app.exec_())
