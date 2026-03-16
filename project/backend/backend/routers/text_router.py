"""
VOID Backend — Text Action Routes
Routes: /suggest, /summarize, /translate, /voice-log
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
import models
from services import mistral_service

router = APIRouter(prefix="/text", tags=["Text Actions"])


class TextRequest(BaseModel):
    text: str
    language: Optional[str] = "auto"


class TranslateRequest(BaseModel):
    text: str
    target: str = "telugu"   # "telugu" or "english"


class VoiceLogRequest(BaseModel):
    transcription: str
    language: str = "auto"
    action_taken: Optional[str] = None


# ── Suggest ───────────────────────────────────────────────────────────────────
@router.post("/suggest")
def suggest(req: TextRequest, db: Session = Depends(get_db)):
    """
    Given chat conversation text, suggest the best next reply.
    """
    instruction = (
        "You are a helpful, friendly chat assistant. "
        "Read the following conversation carefully and suggest the single best next reply. "
        "Keep it natural and conversational.\n\n"
        f"Conversation:\n{req.text}"
    )
    result = mistral_service.run(instruction, max_new_tokens=150)

    log = models.ActionLog(
        action="suggest",
        input_text=req.text[:500],
        output_text=result[:500],
        language=req.language,
    )
    db.add(log)
    db.commit()
    return {"suggestion": result}


# ── Summarize ─────────────────────────────────────────────────────────────────
@router.post("/summarize")
def summarize(req: TextRequest, db: Session = Depends(get_db)):
    """
    Summarize given text content clearly and concisely.
    """
    instruction = (
        "Summarize the following content in clear, simple points. "
        "Capture only the most important information.\n\n"
        f"Content:\n{req.text}"
    )
    result = mistral_service.run(instruction, max_new_tokens=200)

    log = models.ActionLog(
        action="summarize",
        input_text=req.text[:500],
        output_text=result[:500],
        language=req.language,
    )
    db.add(log)
    db.commit()
    return {"summary": result}


# ── Translate ─────────────────────────────────────────────────────────────────
@router.post("/translate")
def translate(req: TranslateRequest, db: Session = Depends(get_db)):
    """
    Translate text between Telugu and English.
    """
    if req.target == "telugu":
        instruction = f"Translate the following English text to Telugu:\n\n{req.text}"
    else:
        instruction = f"Translate the following Telugu text to English:\n\n{req.text}"

    result = mistral_service.run(instruction, max_new_tokens=300)

    log = models.ActionLog(
        action="translate",
        input_text=req.text[:500],
        output_text=result[:500],
        language=req.target,
    )
    db.add(log)
    db.commit()
    return {"translation": result, "target_language": req.target}


# ── Voice Log ─────────────────────────────────────────────────────────────────
@router.post("/voice-log")
def log_voice(req: VoiceLogRequest, db: Session = Depends(get_db)):
    """
    Save a voice transcription to the database.
    Called by frontend after Whisper transcribes audio.
    """
    log = models.VoiceLog(
        transcription=req.transcription,
        language=req.language,
        action_taken=req.action_taken,
    )
    db.add(log)
    db.commit()
    return {"logged": True, "transcription": req.transcription}
