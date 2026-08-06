"""
VOID — Reminder Service
Set reminders with desktop notifications via plyer
"""

from typing import Optional, List, Dict
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import threading
import time

from services.memory_service import add_memory, get_context_for_query

# In-memory reminders (in production, store in DB)
_reminders: List[Dict] = []
_reminder_id_counter = 0


def set_reminder(text: str, when: str) -> str:
    """Set a reminder.
    
    Args:
        text: What to remind about
        when: Natural time string or datetime
    
    Returns:
        Confirmation string
    """
    global _reminder_id_counter

    try:
        # Try to parse time
        parsed_time = date_parser.parse(when, fuzzy=True)
        if parsed_time < datetime.now():
            # If time has passed, assume tomorrow
            parsed_time = parsed_time + timedelta(days=1)

        _reminder_id_counter += 1
        reminder = {
            "id": _reminder_id_counter,
            "text": text,
            "when": parsed_time,
            "created_at": datetime.now(),
            "notified": False,
        }
        _reminders.append(reminder)

        # Schedule notification
        delay = (parsed_time - datetime.now()).total_seconds()
        if delay > 0:
            timer = threading.Timer(delay, _fire_reminder, args=[reminder])
            timer.daemon = True
            timer.start()

        # Store in memory
        add_memory(
            f"Reminder set: {text} at {parsed_time.strftime('%I:%M %p %b %d')}",
            category="reminders",
            importance=2,
        )

        return (
            f"✅ **Reminder set!**\n"
            f"📌 {text}\n"
            f"⏰ {parsed_time.strftime('%I:%M %p, %b %d')}\n\n"
            f"I'll notify you then bro!"
        )

    except (ValueError, TypeError):
        return (
            f"❌ Time understand avvaledhu bro. Try something like:\n"
            f"  'in 30 minutes'\n"
            f"  'at 3 PM'\n"
            f"  'tomorrow 9 AM'"
        )


def _fire_reminder(reminder: dict):
    """Fire a reminder notification."""
    reminder["notified"] = True

    # Desktop notification via plyer
    try:
        from plyer import notification
        notification.notify(
            title="🔔 VOID Reminder",
            message=reminder["text"],
            timeout=10,
        )
    except Exception:
        pass  # plyer not available, silently continue

    # Log in memory
    add_memory(
        f"Reminder fired: {reminder['text']}",
        category="reminders",
        importance=1,
    )


def get_pending_reminders() -> List[Dict]:
    """Get all pending reminders."""
    now = datetime.now()
    return [
        r for r in _reminders
        if not r["notified"] and r["when"] > now
    ]


def get_overdue_reminders() -> List[Dict]:
    """Get reminders that should have fired but weren't notified."""
    now = datetime.now()
    return [
        r for r in _reminders
        if not r["notified"] and r["when"] <= now
    ]


def list_reminders() -> str:
    """List all pending reminders."""
    pending = get_pending_reminders()

    if not pending:
        return "📋 No pending reminders bro"

    lines = [f"📋 **Reminders** ({len(pending)} pending)"]
    for r in sorted(pending, key=lambda x: x["when"]):
        lines.append(
            f"  ⏰ {r['when'].strftime('%I:%M %p, %b %d')}\n"
            f"     📌 {r['text']}"
        )

    return "\n".join(lines)


def clear_reminder(reminder_id: int) -> str:
    """Clear a specific reminder by ID."""
    global _reminders
    for r in _reminders:
        if r["id"] == reminder_id:
            r["notified"] = True
            return f"✅ Reminder {reminder_id} cleared bro"

    return f"❌ Reminder {reminder_id} dorakaledhu bro"


def clear_all_reminders() -> str:
    """Clear all reminders."""
    global _reminders
    count = len(_reminders)
    _reminders = []
    return f"✅ {count} reminder(s) cleared bro"
