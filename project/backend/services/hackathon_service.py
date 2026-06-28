"""
VOID — Hackathon Mode
Timed submission mode with progress checks and deadline management
"""

from typing import Optional, Dict
from datetime import datetime, timedelta
import threading
import time

from services.memory_service import add_memory

# Active hackathon sessions
_active_hackathons: Dict[str, dict] = {}

# Known hackathons from history
KNOWN_HACKATHONS = [
    {
        "name": "Hack2Skill — INDIA RUNS",
        "project": "AI Resume Ranker",
        "status": "completed",
    },
    {
        "name": "DevNetwork AI/ML Hackathon 2026",
        "project": "ShadeMatch",
        "status": "completed",
    },
]


def activate_hackathon_mode(hours_remaining: float, hackathon_name: str = "") -> str:
    """Activate hackathon mode with a countdown timer.

    Args:
        hours_remaining: Hours until deadline
        hackathon_name: Name of the hackathon
    """
    deadline = datetime.now() + timedelta(hours=hours_remaining)
    session_id = f"hackathon_{datetime.now().timestamp()}"

    _active_hackathons[session_id] = {
        "name": hackathon_name or "Unnamed Hackathon",
        "deadline": deadline,
        "hours_initial": hours_remaining,
        "started_at": datetime.now(),
        "active": True,
    }

    # Store in memory
    add_memory(
        f"Hackathon mode started for {hackathon_name or 'unnamed'} — "
        f"{hours_remaining} hours remaining. Deadline: {deadline.strftime('%b %d, %I:%M %p')}",
        category="hackathon",
        importance=4,
    )

    response = (
        f"🚨 **HACKATHON MODE ACTIVATED** 🔥\n\n"
        f"Event: {hackathon_name or 'Unnamed Hackathon'}\n"
        f"⏱️ {hours_remaining:.1f} hours remaining\n"
        f"📅 Deadline: {deadline.strftime('%b %d, %I:%M %p')}\n\n"
        f"**Rules of engagement:**\n"
        f"1. Ship first, polish later\n"
        f"2. Cut scope ruthlessly — core features only\n"
        f"3. No distractions\n"
        f"4. We shipping this! 🚀\n\n"
        f"Let's go bro! 💪🔥"
    )

    # Schedule progress checks
    if hours_remaining >= 3:
        # Check at halfway
        half_time = (hours_remaining / 2) * 3600
        threading.Timer(half_time, _progress_check, args=[session_id]).start()

        # Check at 3 hours
        if hours_remaining > 3:
            three_hours_before = (hours_remaining - 3) * 3600
            threading.Timer(three_hours_before, _three_hour_warning, args=[session_id]).start()

    # 1 hour warning
    if hours_remaining > 1:
        one_hour_before = (hours_remaining - 1) * 3600
        threading.Timer(one_hour_before, _one_hour_warning, args=[session_id]).start()

    # 15 min warning
    if hours_remaining > 0.25:
        fifteen_min_before = (hours_remaining - 0.25) * 3600
        threading.Timer(fifteen_min_before, _fifteen_min_warning, args=[session_id]).start()

    # Deadline
    total_seconds = hours_remaining * 3600
    threading.Timer(total_seconds, _deadline_reached, args=[session_id]).start()

    return response


def _progress_check(session_id: str):
    """Halfway progress check."""
    session = _active_hackathons.get(session_id)
    if not session or not session["active"]:
        return

    remaining = (session["deadline"] - datetime.now()).total_seconds() / 3600
    from services.ollama_service import run as llm_run

    message = (
        f"⏰ **Progress Check — {remaining:.1f} hours remaining**\n\n"
        f"Bro, emi complete chesav? Emi pending?\n"
        f"Scope cut cheyyala? Quick update cheyyi!"
    )
    # In production, this would be a push notification
    print(f"\n[VOID HACKATHON] {message}\n")


def _three_hour_warning(session_id: str):
    """3 hours before deadline warning."""
    session = _active_hackathons.get(session_id)
    if not session or not session["active"]:
        return

    message = (
        f"⚠️ **3 Hours Remaining!**\n\n"
        f"Final stretch bro — cut scope cheyyali?\n"
        f"Core features ready aa? Let's lock in! 🔥"
    )
    print(f"\n[VOID HACKATHON] {message}\n")


def _one_hour_warning(session_id: str):
    """1 hour before deadline warning."""
    session = _active_hackathons.get(session_id)
    if not session or not session["active"]:
        return

    message = (
        f"🚨 **1 Hour Remaining!** 🚨\n\n"
        f"Deploy chesava? README complete aa?\n"
        f"Submission link ready aa? Polish later, ship now!"
    )
    print(f"\n[VOID HACKATHON] {message}\n")


def _fifteen_min_warning(session_id: str):
    """15 minutes before deadline warning."""
    session = _active_hackathons.get(session_id)
    if not session or not session["active"]:
        return

    message = (
        f"🚀 **15 MINUTES LEFT!** 🚀\n\n"
        f"SUBMIT CHEYYI BRO — POLISH LATER, SHIP NOW! 🚀🚀🚀"
    )
    print(f"\n[VOID HACKATHON] {message}\n")


def _deadline_reached(session_id: str):
    """Deadline reached."""
    session = _active_hackathons.get(session_id)
    if not session:
        return

    session["active"] = False
    elapsed = (datetime.now() - session["started_at"]).total_seconds() / 3600

    add_memory(
        f"Hackathon ended: {session['name']} — ran for {elapsed:.1f} hours",
        category="hackathon",
        importance=4,
    )

    message = (
        f"⏰ **DEADLINE REACHED!** ⏰\n\n"
        f"Time's up bro! You ran for {elapsed:.1f} hours.\n\n"
        f"Emi submit chesav? How'd it go? 🚀"
    )
    print(f"\n[VOID HACKATHON] {message}\n")


def get_hackathon_status() -> str:
    """Get status of active hackathon sessions."""
    if not _active_hackathons:
        return "No active hackathons bro"

    active = [s for s in _active_hackathons.values() if s["active"]]
    if not active:
        return "No active hackathons bro — more info: ee hackathon lo part chesav?"

    session = active[0]
    remaining = (session["deadline"] - datetime.now()).total_seconds() / 3600
    if remaining < 0:
        session["active"] = False
        return "Hackathon deadline passed bro! Emi submit chesav?"

    hours_done = session["hours_initial"] - remaining
    pct = (hours_done / session["hours_initial"]) * 100 if session["hours_initial"] > 0 else 0

    return (
        f"🚨 **Hackathon Mode Active** 🔥\n\n"
        f"Event: {session['name']}\n"
        f"⏱️ **{remaining:.1f} hours remaining** ({pct:.0f}% done)\n"
        f"📅 Deadline: {session['deadline'].strftime('%b %d, %I:%M %p')}\n\n"
        f"Progress: {'█' * int(pct / 10)}{'▒' * (10 - int(pct / 10))} {pct:.0f}%\n\n"
        f"Keep shipping bro! 🚀"
    )


def end_hackathon() -> str:
    """End the active hackathon session."""
    for session_id, session in _active_hackathons.items():
        if session["active"]:
            session["active"] = False
            elapsed = (datetime.now() - session["started_at"]).total_seconds() / 3600
            add_memory(
                f"Hackathon ended early: {session['name']} — ran for {elapsed:.1f} hours",
                category="hackathon",
                importance=3,
            )
            return (
                f"✅ Hackathon mode ended!\n\n"
                f"You ran for {elapsed:.1f} hours.\n"
                f"Time to review and submit! 🚀"
            )

    return "No active hackathon to end bro"


def get_known_hackathons() -> str:
    """List known past hackathons from memory."""
    lines = ["🏆 **Past Hackathons**"]
    for h in KNOWN_HACKATHONS:
        lines.append(f"  • {h['name']} — {h['project']} [{h['status']}]")
    return "\n".join(lines)
