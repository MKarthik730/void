from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base
from pgvector.sqlalchemy import Vector


class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(50), nullable=False)
    input_text = Column(Text, nullable=True)
    output_text = Column(Text, nullable=True)
    language = Column(String(20), default="auto")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Screenshot(Base):
    __tablename__ = "screenshots"

    id = Column(Integer, primary_key=True, index=True)
    filepath = Column(Text, nullable=False)
    folder = Column(String(255), nullable=True)
    context = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VoiceLog(Base):
    __tablename__ = "voice_logs"

    id = Column(Integer, primary_key=True, index=True)
    transcription = Column(Text, nullable=True)
    language = Column(String(20), default="auto")
    action_taken = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MeetingLog(Base):
    __tablename__ = "meeting_logs"

    id = Column(Integer, primary_key=True, index=True)
    transcription = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)
    duration_secs = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(Text, nullable=False)
    assistant_response = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=True)
    category = Column(String(50), default="general")
    importance = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
