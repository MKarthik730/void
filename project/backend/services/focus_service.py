"""
VOID — Focus Service
Pomodoro timer, focus mode, distraction tracking
"""

from typing import Optional, Dict
from datetime import datetime, timedelta
import threading
import time

# Active focus sessions
_active_sessions: Dict[str, dict] = {}


def start_focus(duration_minutes: int = 25) -> str:
    """Start a focus session. Returns confirmation."""
    session_id = f"focus_{datetime.now().timestamp()}"

    end_time = datetime.now() + timedelta(minutes=duration_minutes)

    _active_sessions[session_id] = {
        "started_at": datetime.now(),
        "end_at": end_time,
        "duration": duration_minutes,
        "completed": False,
    }

    # Schedule end notification
    def _end_session():
        if session_id in _active_sessions:
            _active_sessions[session_id]["completed"] = True

            from services.memory_service import add_memory
            add_memory(
                f"Completed {duration_minutes}min focus session at {datetime.now().strftime('%I:%M %p')}",
                category="productivity",
                importance=2,
            )

    timer = threading.Timer(duration_minutes * 60, _end_session)
    timer.daemon = True
    timer.start()

    # Store in memory
    from services.memory_service import add_memory
    add_memory(
        f"Started {duration_minutes}min focus session at {datetime.now().strftime('%I:%M %p')}",
        category="productivity",
        importance=1,
    )

    # Pomodoro-style suggestion
    if duration_minutes == 25:
        return (
            f"🎯 **Focus mode activated — {duration_minutes} minutes!** 💪\n\n"
            f"Pomodoro style: {duration_minutes}min work, then 5min break.\n"
            f"Ends at: {end_time.strftime('%I:%M %p')}\n\n"
            f"Luck avasaram ledu bro — cheseyyi! 🚀"
        )
    elif duration_minutes >= 60:
        return (
            f"🎯 **Deep focus mode — {duration_minutes} minutes!** 🔥\n\n"
            f"Long session bro — take a 10min break in between if needed.\n"
            f"Ends at: {end_time.strftime('%I:%M %p')}\n\n"
            f"Ship something great! 🚀"
        )
    else:
        return (
            f"🎯 **Focus mode activated — {duration_minutes} minutes!**\n\n"
            f"Ends at: {end_time.strftime('%I:%M %p')}\n\n"
            f"Let's go bro! 💪"
        )


def get_focus_status() -> str:
    """Get status of all active focus sessions."""
    if not _active_sessions:
        return "🎯 No active focus sessions"

    now = datetime.now()
    active = []

    for sid, session in _active_sessions.items():
        if not session["completed"]:
            remaining = session["end_at"] - now
            if remaining.total_seconds() > 0:
                mins_left = int(remaining.total_seconds() // 60)
                active.append(
                    f"  ⏱️ {mins_left} min remaining "
                    f"(started {session['started_at'].strftime('%I:%M %p')})"
                )

    if active:
        return "🎯 **Active Focus Sessions**\n" + "\n".join(active)
    return "🎯 No active focus sessions"


def end_focus() -> str:
    """End all focus sessions."""
    global _active_sessions
    if not _active_sessions:
        return "🎯 No active sessions to end bro"

    count = len([s for s in _active_sessions.values() if not s["completed"]])
    for sid in _active_sessions:
        _active_sessions[sid]["completed"] = True

    return f"🎯 Focus session ended! {count} session(s) completed. Break theeskoni malli start cheyyi 💪"


def suggest_pomodoro() -> str:
    """Suggest starting a pomodoro based on time of day."""
    now = datetime.now()
    hour = now.hour

    # Morning (6-12): Best for deep work
    if 6 <= hour < 12:
        return "☀️ Morning time bro — best for deep work. 25min pomodoro start cheyyala? 🚀"
    # Afternoon (12-5): Good for coding
    elif 12 <= hour < 17:
        return "🌤️ Afternoon session — good time to ship code. Focus mode start cheyyala? 💪"
    # Evening (5-10): Project time
    elif 17 <= hour < 22:
        return "🌆 Evening time — project work ki perfect. 25min focus cheyyala? 🔥"
    # Night (10+): Wind down
    else:
        return "🌙 Bro sleep time daggarlo undi — okka quick 15min session cheyyala?"
