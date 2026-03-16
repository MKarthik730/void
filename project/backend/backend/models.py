"""
VOID Backend — SQLAlchemy Database Models
Tables: action_logs, screenshots, voice_logs, meeting_logs
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base


class ActionLog(Base):
    """Logs every VOID action (suggest, summarize, explain, translate, autotype)"""
    __tablename__ = "action_logs"

    id          = Column(Integer, primary_key=True, index=True)
    action      = Column(String(50),  nullable=False)
    input_text  = Column(Text,        nullable=True)
    output_text = Column(Text,        nullable=True)
    language    = Column(String(20),  default="auto")
    created_at  = Column(DateTime(timezone=True), server_default=func.now())


class Screenshot(Base):
    """Stores metadata for every saved screenshot"""
    __tablename__ = "screenshots"

    id         = Column(Integer, primary_key=True, index=True)
    filepath   = Column(Text,        nullable=False)
    folder     = Column(String(255), nullable=True)
    context    = Column(String(100), nullable=True)   # whatsapp | pdf | browser | etc
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VoiceLog(Base):
    """Logs every voice input transcription"""
    __tablename__ = "voice_logs"

    id            = Column(Integer, primary_key=True, index=True)
    transcription = Column(Text,       nullable=True)
    language      = Column(String(20), default="auto")
    action_taken  = Column(String(50), nullable=True)  # what was done with this voice input
    created_at    = Column(DateTime(timezone=True), server_default=func.now())


class MeetingLog(Base):
    """Stores meeting transcriptions and summaries"""
    __tablename__ = "meeting_logs"

    id            = Column(Integer, primary_key=True, index=True)
    transcription = Column(Text, nullable=True)
    summary       = Column(Text, nullable=True)
    action_items  = Column(Text, nullable=True)   # extracted action items
    duration_secs = Column(Integer, default=0)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
