"""
VOID — Voice Service
Speech-to-text via faster-whisper, text-to-speech via pyttsx3
"""

import os
from typing import Optional
import config


def transcribe(audio_path: str) -> Optional[str]:
    """Transcribe audio file using faster-whisper.

    Args:
        audio_path: Path to audio file (wav/mp3/ogg)

    Returns:
        Transcribed text or None on failure
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return "[faster-whisper install cheyyaledhu bro — pip install faster-whisper]"

    if not os.path.exists(audio_path):
        return f"[Audio file dorakaledhu: {audio_path}]"

    try:
        model = WhisperModel(
            config.WHISPER_MODEL,
            device="cpu",
            compute_type="int8",
        )
        segments, info = model.transcribe(audio_path, language="te")

        # Infer language
        detected_lang = info.language if info else "en"

        text_parts = []
        for segment in segments:
            text_parts.append(segment.text.strip())

        text = " ".join(text_parts)

        if not text:
            return "[Transcription empty bro — audio clear ga ledhu emo]"

        return text

    except Exception as e:
        return f"[Transcription failed: {str(e)[:100]}]"


def speak(text: str) -> bool:
    """Speak text using pyttsx3 TTS.

    Args:
        text: Text to speak aloud

    Returns:
        True if successful, False otherwise
    """
    try:
        import pyttsx3
    except ImportError:
        return False

    try:
        engine = pyttsx3.init()

        # Configure voice
        voices = engine.getProperty("voices")
        if voices:
            # Try to find a voice that works for Tenglish
            if config.TTS_VOICE == "male":
                engine.setProperty("voice", voices[0].id)
            elif len(voices) > 1:
                engine.setProperty("voice", voices[1].id)

        engine.setProperty("rate", 160)  # Slightly slower for clarity
        engine.setProperty("volume", 0.9)

        engine.say(text)
        engine.runAndWait()
        return True

    except Exception:
        return False


def format_for_voice(text: str) -> str:
    """Format text for voice output (no markdown, natural speech).

    Args:
        text: Text with markdown/bullets

    Returns:
        Voice-friendly text
    """
    # Remove markdown formatting
    text = text.replace("**", "")
    text = text.replace("*", "")
    text = text.replace("`", "")
    text = text.replace("```", "")

    # Remove bullet symbols
    text = text.replace("•", "")
    text = text.replace("- ", "")
    text = text.replace("  ", " ")

    # Remove emoji prefixes for cleaner speech (keep some)
    import re
    # Remove standalone emoji at start of lines
    text = re.sub(r'^[🟢🟡🔴🟠🔵⚪⬜🔹🔸✅❌⚠️ℹ️📌⏰📋🎯💪🚀🔥🌤️☀️🌧️🌐💻📧📅📝📄🔗📰🗂️]+ ', '', text, flags=re.MULTILINE)

    # Spell out numbers for natural speech
    def spell_number(match):
        num = int(match.group())
        if num <= 20:
            words = ["zero", "one", "two", "three", "four", "five", "six", "seven",
                     "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
                     "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]
            return words[num]
        return str(num)

    text = re.sub(r'\b(\d+)\b', spell_number, text)

    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text
