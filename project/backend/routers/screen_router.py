"""
VOID Backend — Screen Action Routes
Routes: /screen/analyze, /screen/explain, /screen/whatsapp-suggest, /screen/save-screenshot
"""
import os
import re
import base64
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
from config import SCREENSHOTS_ROOT
import models
from services import gemini_service
from services import qwen_service

router = APIRouter(prefix="/screen", tags=["Screen Actions"])


class ScreenRequest(BaseModel):
    screenshot_b64: str
    action: str   # suggest | summarize | explain | translate


class ExplainRequest(BaseModel):
    screenshot_b64: str
    question: Optional[str] = ""


class WhatsAppRequest(BaseModel):
    screenshot_b64: str


class SaveScreenshotRequest(BaseModel):
    screenshot_b64: str
    folder_name: Optional[str] = None
    context: Optional[str] = None


# ── Analyze Screen ────────────────────────────────────────────────────────────
@router.post("/analyze")
def analyze_screen(req: ScreenRequest, db: Session = Depends(get_db)):
    result = gemini_service.analyze(req.screenshot_b64, req.action)
    log = models.ActionLog(
        action=req.action,
        input_text="[screenshot]",
        output_text=result[:500],
    )
    db.add(log)
    db.commit()
    return {"result": result, "action": req.action}


# ── Explain Screen ────────────────────────────────────────────────────────────
@router.post("/explain")
def explain_screen(req: ExplainRequest, db: Session = Depends(get_db)):
    result = gemini_service.describe_image(req.screenshot_b64, req.question)
    log = models.ActionLog(
        action="explain",
        input_text=req.question or "[screenshot]",
        output_text=result[:500],
    )
    db.add(log)
    db.commit()
    return {"explanation": result}


# ── WhatsApp Suggest ──────────────────────────────────────────────────────────
@router.post("/whatsapp-suggest")
def whatsapp_suggest(req: WhatsAppRequest, db: Session = Depends(get_db)):
    """
    1. Use Groq vision to extract the last few messages from WhatsApp screenshot
    2. Pass extracted text to Qwen to generate 3 Tenglish reply suggestions
    Returns: {"suggestions": ["reply1", "reply2", "reply3"]}
    """
    # Step 1 — Vision: extract chat text from screenshot
    extract_prompt = (
        "Look at this WhatsApp chat screenshot. "
        "Extract only the last 5 messages as plain text. "
        "Format: Speaker: message, one per line. Nothing else."
    )
    chat_text = gemini_service.describe_image(req.screenshot_b64, extract_prompt)

    # Step 2 — Qwen: generate 3 Tenglish replies based on extracted chat
    suggest_prompt = (
        "You are a Tenglish WhatsApp assistant. "
        "Read this WhatsApp conversation and generate exactly 3 reply suggestions. "
        "STRICT RULES:\n"
        "- Each reply must be a COMPLETE SENTENCE, minimum 4 words\n"
        "- Tenglish: mix Telugu words in English script with English naturally\n"
        "- Examples of good replies: 'Ayyo bro, ela undi ra?' | 'Okay kada, nenu chestanu' | 'Arrey, adi cheyyadam kashtam ga'\n"
        "- DO NOT output single words like 'cheppu' or 'ga' alone\n"
        "- Output FORMAT must be exactly: sentence1 | sentence2 | sentence3\n"
        "- Nothing else before or after, no numbers, no explanation\n\n"
        f"Conversation:\n{chat_text}\n\n"
        "Reply suggestions:"
    )
    raw = qwen_service.run(suggest_prompt, max_new_tokens=120)

    # Parse pipe-separated suggestions
    suggestions = [s.strip() for s in raw.split("|") if s.strip()][:3]

    # Fallback if parsing fails
    if not suggestions:
        suggestions = [raw.strip()[:60]]

    log = models.ActionLog(
        action="whatsapp_suggest",
        input_text="[whatsapp screenshot]",
        output_text=" | ".join(suggestions),
    )
    db.add(log)
    db.commit()

    return {"suggestions": suggestions, "chat_context": chat_text}


# ── Save Screenshot ───────────────────────────────────────────────────────────
@router.post("/save-screenshot")
def save_screenshot(req: SaveScreenshotRequest, db: Session = Depends(get_db)):
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = req.folder_name or f"VOID_Screenshots_{datetime.now().strftime('%Y-%m-%d')}"
    folder_name = re.sub(r'[<>:"/\\|?*]', '_', folder_name)

    save_dir = os.path.join(SCREENSHOTS_ROOT, folder_name)
    os.makedirs(save_dir, exist_ok=True)

    filename = f"screenshot_{timestamp}.png"
    filepath = os.path.join(save_dir, filename)

    img_bytes = base64.b64decode(req.screenshot_b64)
    with open(filepath, "wb") as f:
        f.write(img_bytes)

    log = models.Screenshot(
        filepath=filepath,
        folder=folder_name,
        context=req.context or "unknown",
    )
    db.add(log)
    db.commit()
    return {"saved_to": filepath, "folder": folder_name, "filename": filename}


# ── List Saved Screenshots ────────────────────────────────────────────────────
@router.get("/screenshots")
def list_screenshots(limit: int = 20, db: Session = Depends(get_db)):
    shots = (
        db.query(models.Screenshot)
        .order_by(models.Screenshot.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "screenshots": [
            {
                "path":    s.filepath,
                "folder":  s.folder,
                "context": s.context,
                "time":    str(s.created_at),
            }
            for s in shots
        ]
    }