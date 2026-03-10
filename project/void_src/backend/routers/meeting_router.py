"""
VOID Backend — Meeting & History Routes
Routes: /meeting/summarize, /history/actions, /history/voice
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
import models
from services import mistral_service

router = APIRouter(tags=["Meeting & History"])


class MeetingRequest(BaseModel):
    transcription: str
    duration_secs: Optional[int] = 0


# ── Meeting Summarizer ────────────────────────────────────────────────────────
@router.post("/meeting/summarize")
def summarize_meeting(req: MeetingRequest, db: Session = Depends(get_db)):
    """
    Takes a full meeting transcription and returns:
    - A concise summary
    - Extracted action items
    """
    summary_instruction = (
        "You are an expert meeting assistant. "
        "Read this meeting transcription and provide:\n"
        "1. A clear summary (3-5 sentences)\n"
        "2. A list of action items with owners if mentioned\n\n"
        f"Transcription:\n{req.transcription}"
    )
    result = mistral_service.run(summary_instruction, max_new_tokens=400)

    # Try to split summary and action items
    lines       = result.split("\n")
    summary     = result
    action_items = ""
    for i, line in enumerate(lines):
        if "action" in line.lower():
            summary      = "\n".join(lines[:i]).strip()
            action_items = "\n".join(lines[i:]).strip()
            break

    log = models.MeetingLog(
        transcription=req.transcription[:2000],
        summary=summary[:1000],
        action_items=action_items[:500],
        duration_secs=req.duration_secs,
    )
    db.add(log)
    db.commit()
    return {
        "summary":      summary,
        "action_items": action_items,
        "full_response": result,
    }


# ── Action History ────────────────────────────────────────────────────────────
@router.get("/history/actions")
def action_history(limit: int = 20, db: Session = Depends(get_db)):
    """Return recent VOID action logs"""
    logs = (
        db.query(models.ActionLog)
        .order_by(models.ActionLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "history": [
            {
                "action":   l.action,
                "input":    l.input_text,
                "output":   l.output_text,
                "language": l.language,
                "time":     str(l.created_at),
            }
            for l in logs
        ]
    }


# ── Voice History ─────────────────────────────────────────────────────────────
@router.get("/history/voice")
def voice_history(limit: int = 20, db: Session = Depends(get_db)):
    """Return recent voice transcription logs"""
    logs = (
        db.query(models.VoiceLog)
        .order_by(models.VoiceLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "voice_logs": [
            {
                "transcription": l.transcription,
                "language":      l.language,
                "action_taken":  l.action_taken,
                "time":          str(l.created_at),
            }
            for l in logs
        ]
    }


# ── Meeting History ───────────────────────────────────────────────────────────
@router.get("/history/meetings")
def meeting_history(limit: int = 10, db: Session = Depends(get_db)):
    """Return past meeting summaries"""
    meetings = (
        db.query(models.MeetingLog)
        .order_by(models.MeetingLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "meetings": [
            {
                "summary":      m.summary,
                "action_items": m.action_items,
                "duration_secs": m.duration_secs,
                "time":         str(m.created_at),
            }
            for m in meetings
        ]
    }
