"""
VOID Backend — Screen Action Routes
Routes: /screen/analyze, /screen/explain, /screen/save-screenshot
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

router = APIRouter(prefix="/screen", tags=["Screen Actions"])


class ScreenRequest(BaseModel):
    screenshot_b64: str
    action: str   # suggest | summarize | explain | translate


class ExplainRequest(BaseModel):
    screenshot_b64: str
    question: Optional[str] = ""   # optional follow-up question


class SaveScreenshotRequest(BaseModel):
    screenshot_b64: str
    folder_name: Optional[str] = None
    context: Optional[str] = None  # whatsapp | pdf | browser | code | other


# ── Analyze Screen ────────────────────────────────────────────────────────────
@router.post("/analyze")
def analyze_screen(req: ScreenRequest, db: Session = Depends(get_db)):
    """
    Unified screen analysis. Action determines what Gemini Vision does:
    suggest | summarize | explain | translate
    """
    result = gemini_service.analyze(req.screenshot_b64, req.action)

    log = models.ActionLog(
        action=req.action,
        input_text="[screenshot]",
        output_text=result[:500],
    )
    db.add(log)
    db.commit()
    return {"result": result, "action": req.action}


# ── Explain Screen (PDF / image / chart) ──────────────────────────────────────
@router.post("/explain")
def explain_screen(req: ExplainRequest, db: Session = Depends(get_db)):
    """
    Deep explanation of screen content.
    Optionally pass a user question for follow-up context.
    Gemini Vision reads and explains text, charts, code, images.
    """
    result = gemini_service.describe_image(req.screenshot_b64, req.question)

    log = models.ActionLog(
        action="explain",
        input_text=req.question or "[screenshot]",
        output_text=result[:500],
    )
    db.add(log)
    db.commit()
    return {"explanation": result}


# ── Save Screenshot ───────────────────────────────────────────────────────────
@router.post("/save-screenshot")
def save_screenshot(req: SaveScreenshotRequest, db: Session = Depends(get_db)):
    """
    Save a base64 screenshot to ~/Pictures/VOID/<folder>/
    Auto-generates folder name by date if not provided.
    """
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = req.folder_name or f"VOID_Screenshots_{datetime.now().strftime('%Y-%m-%d')}"
    folder_name = re.sub(r'[<>:"/\\|?*]', '_', folder_name)  # sanitize

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
    """Return list of saved screenshots from DB"""
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
